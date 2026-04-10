import { describe, it, expect, vi, beforeEach } from "vitest";
import { login, logout } from "./auth";

const MOCK_TOKEN = "header.payload.signature";

beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
});

// ── login ─────────────────────────────────────────────────────────────────

describe("login", () => {
    it("calls the correct endpoint with POST", async () => {
        vi.mocked(fetch).mockResolvedValue({
            json: async () => ({ success: true, message: "barnes logged in successfully.", data: MOCK_TOKEN }),
        } as Response);

        await login("barnes", "password");

        expect(fetch).toHaveBeenCalledWith(
            expect.stringContaining("/user/login?username=barnes&password=password"),
            { method: "POST" }
        );
    });

    it("returns success and token on valid credentials", async () => {
        vi.mocked(fetch).mockResolvedValue({
            json: async () => ({ success: true, message: "barnes logged in successfully.", data: MOCK_TOKEN }),
        } as Response);

        const result = await login("barnes", "password");

        expect(result.success).toBe(true);
        expect(result.data).toBe(MOCK_TOKEN);
    });

    it("returns failure and null data on invalid credentials", async () => {
        vi.mocked(fetch).mockResolvedValue({
            json: async () => ({ success: false, message: "Login failed for wrong.", data: null }),
        } as Response);

        const result = await login("wrong", "credentials");

        expect(result.success).toBe(false);
        expect(result.data).toBeNull();
    });

    it("URL-encodes special characters in username and password", async () => {
        vi.mocked(fetch).mockResolvedValue({
            json: async () => ({ success: false, message: "", data: null }),
        } as Response);

        await login("user name", "p@ss&word");

        expect(fetch).toHaveBeenCalledWith(
            expect.stringContaining("username=user%20name&password=p%40ss%26word"),
            expect.anything()
        );
    });
});

// ── logout ────────────────────────────────────────────────────────────────

describe("logout", () => {
    it("calls the correct endpoint with DELETE", async () => {
        vi.mocked(fetch).mockResolvedValue({} as Response);

        await logout(MOCK_TOKEN);

        expect(fetch).toHaveBeenCalledWith(
            expect.stringContaining("/user/logout"),
            expect.objectContaining({ method: "DELETE" })
        );
    });

    it("sends the token as a Bearer Authorization header", async () => {
        vi.mocked(fetch).mockResolvedValue({} as Response);

        await logout(MOCK_TOKEN);

        expect(fetch).toHaveBeenCalledWith(
            expect.anything(),
            expect.objectContaining({
                headers: { Authorization: `Bearer ${MOCK_TOKEN}` },
            })
        );
    });
});