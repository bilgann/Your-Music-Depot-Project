"use client";

import { usePathname } from "next/navigation";
import type { FC } from "react";
import type { IconDefinition } from "@fortawesome/free-solid-svg-icons";
import {
    faHouse, faCalendar, faGraduationCap, faUsers,
    faChalkboardUser, faDoorOpen, faCreditCard,
    faGear, faRightFromBracket,
} from "@fortawesome/free-solid-svg-icons";
import Button from "@/components/ui/button";
import { useAuth } from "@/context/auth";

interface NavItem {
    label: string;
    path: string;
    icon: IconDefinition;
}

const NAV_ITEMS: NavItem[] = [
    { label: "Home",        path: "/home",        icon: faHouse },
    { label: "Schedule",    path: "/schedule",    icon: faCalendar },
    { label: "Students",    path: "/students",    icon: faGraduationCap },
    { label: "Clients",     path: "/clients",     icon: faUsers },
    { label: "Instructors", path: "/instructors", icon: faChalkboardUser },
    { label: "Rooms",       path: "/rooms",       icon: faDoorOpen },
    { label: "Payments",    path: "/payments",    icon: faCreditCard },
    { label: "Settings",    path: "/settings",    icon: faGear },
];

export const SideBar: FC = () => {
    const pathname = usePathname();
    const { clearToken } = useAuth();

    return (
        <aside className="sidebar-container">
            <nav>
                {NAV_ITEMS.map((item) => (
                    <Button
                        key={item.path}
                        variant="sidebar"
                        href={item.path}
                        icon={item.icon}
                        active={pathname === item.path}
                    >
                        {item.label}
                    </Button>
                ))}
            </nav>
            <Button
                variant="sidebar-logout"
                icon={faRightFromBracket}
                onClick={() => void clearToken()}
            >
                Log out
            </Button>
        </aside>
    );
};
