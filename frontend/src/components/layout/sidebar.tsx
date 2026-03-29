"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { FC } from "react";
import { useAuth } from "@/context/auth";

interface NavItem {
    label: string;
    path: string;
}

const NavItems: NavItem[] = [
    { label: "Home", path: "/home" },
    { label: "Schedule", path: "/schedule" },
    { label: "Students", path: "/students" },
    { label: "Clients", path: "/clients" },
    { label: "Instructors", path: "/instructors" },
    { label: "Rooms", path: "/rooms" },
    { label: "Payments", path: "/payments" },
    { label: "Settings", path: "/settings" },
];

export const SideBar: FC = () => {
    const pathname = usePathname();
    const { clearToken } = useAuth();

    return (
        <aside className="sidebar-container">
            <nav>
                {NavItems.map((item) => {
                    const isActive = pathname === item.path;
                    return (
                        <Link
                            key={item.path}
                            href={item.path}
                            className={`sidebar-link ${isActive ? "active" : ""}`}
                        >
                            {item.label}
                        </Link>
                    );
                })}
            </nav>

            <button
                className="sidebar-logout"
                onClick={() => void clearToken()}
                type="button"
            >
                Log out
            </button>
        </aside>
    );
};
