"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import type { FC } from "react";
import type { IconDefinition } from "@fortawesome/free-solid-svg-icons";
import {
    faHouse, faGraduationCap, faUsers,
    faChalkboardUser, faBook, faDoorOpen, faFileInvoiceDollar, faCreditCard,
    faGear, faRightFromBracket, faBars, faXmark,
} from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import Button from "@/components/ui/button";
import { useAuth } from "@/context/auth";

interface NavItem {
    label: string;
    path: string;
    icon: IconDefinition;
}

const NAV_ITEMS: NavItem[] = [
    { label: "Home",        path: "/home",        icon: faHouse },
    { label: "Students",    path: "/students",    icon: faGraduationCap },
    { label: "Clients",     path: "/clients",     icon: faUsers },
    { label: "Instructors", path: "/instructors", icon: faChalkboardUser },
    { label: "Courses",     path: "/courses",     icon: faBook },
    { label: "Rooms",       path: "/rooms",       icon: faDoorOpen },
    { label: "Invoices",    path: "/invoices",    icon: faFileInvoiceDollar },
    { label: "Payments",    path: "/payments",    icon: faCreditCard },
    { label: "Settings",    path: "/settings",    icon: faGear },
];

export const SideBar: FC = () => {
    const pathname = usePathname();
    const { clearToken } = useAuth();
    const [open, setOpen] = useState(false);

    return (
        <>
            <button className="sidebar-toggle" onClick={() => setOpen(!open)} aria-label="Toggle sidebar">
                <FontAwesomeIcon icon={open ? faXmark : faBars} />
            </button>
            <aside className={`sidebar-container${open ? " sidebar-open" : ""}`}>
                <nav>
                    {NAV_ITEMS.map((item) => (
                        <Button
                            key={item.path}
                            variant="sidebar"
                            href={item.path}
                            icon={item.icon}
                            active={pathname === item.path}
                            onClick={() => setOpen(false)}
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
        </>
    );
};
