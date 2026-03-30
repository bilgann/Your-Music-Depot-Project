"use client";

import { useEffect, useState } from "react";
import Navbar from "@/components/ui/navbar";
import Button from "@/components/ui/button";
import { changePassword } from "@/features/auth/api/auth";

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
    const [currentPassword, setCurrentPassword] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState<{ text: string; success: boolean } | null>(null);

    useEffect(() => {
        const token = localStorage.getItem("token");
        if (token) setUser(decodeToken(token));
    }, []);

    async function handleChangePassword(e: React.FormEvent) {
        e.preventDefault();
        setMessage(null);
        if (newPassword !== confirmPassword) {
            setMessage({ text: "New passwords do not match.", success: false });
            return;
        }
        if (newPassword.length < 6) {
            setMessage({ text: "New password must be at least 6 characters.", success: false });
            return;
        }
        setSaving(true);
        try {
            const result = await changePassword(currentPassword, newPassword);
            setMessage({ text: result.message, success: result.success });
            if (result.success) {
                setCurrentPassword("");
                setNewPassword("");
                setConfirmPassword("");
            }
        } catch {
            setMessage({ text: "Failed to change password.", success: false });
        } finally {
            setSaving(false);
        }
    }

    return (
        <>
            <Navbar title="Settings" className="page-settings" />
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

            <div className="settings-card" style={{ marginTop: 24 }}>
                <h3 style={{ marginBottom: 16 }}>Change Password</h3>
                <form onSubmit={handleChangePassword} style={{ display: "grid", gap: 12, maxWidth: 400 }}>
                    <div className="form-field">
                        <label>Current Password</label>
                        <input type="password" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} required />
                    </div>
                    <div className="form-field">
                        <label>New Password</label>
                        <input type="password" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} required minLength={6} />
                    </div>
                    <div className="form-field">
                        <label>Confirm New Password</label>
                        <input type="password" value={confirmPassword} onChange={(e) => setConfirmPassword(e.target.value)} required minLength={6} />
                    </div>
                    {message && (
                        <p style={{ color: message.success ? "var(--success-color, green)" : "var(--danger-color, red)" }}>
                            {message.text}
                        </p>
                    )}
                    <div>
                        <Button variant="primary" type="submit" disabled={saving}>
                            {saving ? "Saving..." : "Change Password"}
                        </Button>
                    </div>
                </form>
            </div>
        </>
    );
}
