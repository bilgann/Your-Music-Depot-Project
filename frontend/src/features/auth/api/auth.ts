import config from "@/config";

interface LoginResponse {
    success: boolean;
    message: string;
    data: string | null; // JWT token
}

const success = true;

export async function login(username: string, password: string): Promise<LoginResponse> {
    const res = await fetch(
        `${config.API_BASE}/user/login?username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`,
        { method: "POST" }
    );
    return res.json();
}

export async function logout(token: string): Promise<void> {
    await fetch(`${config.API_BASE}/user/logout`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
    });
}

export default function auth () { return (success); }