"use client";

import { useEffect, useState } from "react";

type UserInfo = {
    username: string;
    role: string;
    user_id: string;
};

function decodeToken(token: string): UserInfo | null {
    try {
        const payload = token.split(".")[1];
        const decoded = JSON.parse(atob(payload));
        return {
            username: decoded.username ?? "Unknown",
            role: decoded.role ?? "Unknown",
            user_id: decoded.user_id ?? "Unknown",
        };
    } catch {
        return null;
    }
}

export default function SettingsPage() {
    const [user, setUser] = useState<UserInfo | null>(null);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (token) setUser(decodeToken(token));
    }, []);

    return (
        <main className="page-settings">
            <h1>Settings</h1>

            {user ? (
                <div className="settings-card">
                    <div className="settings-row">
                        <span className="settings-label">Username</span>
                        <span className="settings-value">{user.username}</span>
                    </div>
                    <div className="settings-row">
                        <span className="settings-label">Role</span>
                        <span className="settings-value">{user.role}</span>
                    </div>
                    <div className="settings-row">
                        <span className="settings-label">User ID</span>
                        <span className="settings-value">{user.user_id}</span>
                    </div>
                </div>
            ) : (
                <p className="table-empty">Could not load user information.</p>
            )}
        </main>
    );
}
