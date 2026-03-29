"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { faEye, faEyeSlash } from "@fortawesome/free-solid-svg-icons";
import Button from "@/components/ui/button";
import { login } from "../api/auth";

export default function LoginForm() {
    const router = useRouter();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setError(null);
        setLoading(true);
        router.push("/home");
        set
        /**
        try {
            const res = await login(username, password);
            if (res.success && res.data) {
                localStorage.setItem("token", res.data);
                
            } else {
                setError(res.message);
            }
        } catch {
            setError("Unable to connect. Please try again.");
        } finally {
            setLoading(false);
        }
            */
    }

    return (
        <form className="login-form" onSubmit={handleSubmit}>
            <h1 className="login-title">Your Music Depot</h1>
            <p className="login-subtitle">Sign in to your account</p>

            {error && <p className="login-error">{error}</p>}

            <div className="login-field">
                <label htmlFor="username">Username</label>
                <input
                    id="username"
                    type="text"
                    placeholder="Enter username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                    autoComplete="username"
                />
            </div>

            <div className="login-field">
                <label htmlFor="password">Password</label>
                <div className="login-password-wrapper">
                    <input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Enter password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        autoComplete="current-password"
                    />
                    <Button
                        variant="login-toggle"
                        icon={showPassword ? faEyeSlash : faEye}
                        onClick={() => setShowPassword((prev) => !prev)}
                    >
                        {showPassword ? "Hide" : "Show"}
                    </Button>
                </div>
            </div>

            <Button variant="login" type="submit" disabled={loading}>
                {loading ? "Signing in..." : "Sign In"}
            </Button>
        </form>
    );
}