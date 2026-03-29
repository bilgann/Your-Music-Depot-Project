/**
 * Centralised fetch wrapper for all backend API calls.
 *
 * - Automatically attaches the Authorization: Bearer <token> header
 *   to every request using the token stored in localStorage.
 * - Redirects to /login on 401 responses (expired or invalid session).
 * - Throws ApiError for non-OK responses so callers can catch them.
 */
import config from "@/config";

export class ApiError extends Error {
    constructor(public status: number, message: string) {
        super(message);
        this.name = "ApiError";
    }
}

export async function apiFetch(
    path: string,
    options: RequestInit = {}
): Promise<Response> {
    const token =
        typeof window !== "undefined" ? localStorage.getItem("token") : null;

    const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...(options.headers as Record<string, string>),
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const res = await fetch(`${config.API_BASE}${path}`, {
        ...options,
        headers,
    });

    // Session expired or token invalid — redirect to login
    if (res.status === 401) {
        if (typeof window !== "undefined") {
            localStorage.removeItem("token");
            window.location.href = "/login";
        }
        throw new ApiError(401, "Session expired. Please log in again.");
    }

    return res;
}

/**
 * Convenience wrapper that parses the standard response envelope
 * { success, message, data } and returns data directly.
 * Throws ApiError if success is false.
 */
export async function apiJson<T>(
    path: string,
    options: RequestInit = {}
): Promise<T> {
    const res = await apiFetch(path, options);
    const body = await res.json();
    if (!body.success) {
        throw new ApiError(res.status, body.message ?? "Request failed.");
    }
    return body.data as T;
}

/**
 * Like apiJson but also returns the total count from paginated responses.
 * Backend must include `total` in its response envelope.
 */
export async function apiJsonPaged<T>(
    path: string,
    options: RequestInit = {}
): Promise<{ data: T[]; total: number }> {
    const res = await apiFetch(path, options);
    const body = await res.json();
    if (!body.success) {
        throw new ApiError(res.status, body.message ?? "Request failed.");
    }
    return { data: body.data as T[], total: body.total ?? 0 };
}
