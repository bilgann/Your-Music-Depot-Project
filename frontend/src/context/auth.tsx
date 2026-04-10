"use client";

/**
 * AuthContext — global authentication state for the dashboard.
 *
 * Wrap dashboard pages with <AuthProvider> to:
 *   - Guard routes: redirect to /login if no token is present.
 *   - Expose setToken / clearToken so login and logout can update state.
 *   - Provide isAuthenticated for conditional rendering.
 *
 * Usage:
 *   const { token, clearToken, isAuthenticated } = useAuth();
 */
import {
    createContext,
    useContext,
    useEffect,
    useState,
    type ReactNode,
} from "react";
import { useRouter } from "next/navigation";
import { logout as apiLogout } from "@/features/auth/api/auth";

interface AuthContextType {
    token: string | null;
    isAuthenticated: boolean;
    setToken: (token: string) => void;
    clearToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [token, setTokenState] = useState<string | null>(null);
    const [ready, setReady] = useState(false);
    const router = useRouter();

    // On mount, read the stored token and redirect if absent
    useEffect(() => {
        const stored = localStorage.getItem("token");
        if (!stored) {
            router.replace("/login");
        } else {
            setTokenState(stored);
        }
        setReady(true);
    }, [router]);

    function setToken(t: string) {
        localStorage.setItem("token", t);
        setTokenState(t);
    }

    async function clearToken() {
        const current = localStorage.getItem("token");
        if (current) {
            try {
                await apiLogout(current);
            } catch {
                // Ignore logout API errors — always clear locally
            }
        }
        localStorage.removeItem("token");
        setTokenState(null);
        router.replace("/login");
    }

    // Prevent flash of protected content while auth check is in flight
    if (!ready) return null;

    return (
        <AuthContext.Provider
            value={{ token, isAuthenticated: !!token, setToken, clearToken }}
        >
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth(): AuthContextType {
    const ctx = useContext(AuthContext);
    if (!ctx) {
        throw new Error("useAuth must be called inside an <AuthProvider>.");
    }
    return ctx;
}
