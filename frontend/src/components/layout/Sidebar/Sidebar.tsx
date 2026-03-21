/* Frontend:

Page:

Home Page
Schedule Page
Clients/Students
Instructor
Rooms Page
Payments Page
    Payments History Page
Settings Page


*/
"use client";

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import type { FC } from "react";

interface NavItem {
    label: string;
    path: string;
}

const NavItems: NavItem[] = [
    { label: "Home Page", path: '/'},
    { label: "Schedule", path: "/schedule" },
    { label: "Students", path: "/students" },
    { label: "Instructors", path: "/instructors" },
    { label: "Rooms", path: "/rooms" },
    { label: "Invoices", path: "/invoices" },
    { label: "Settings", path: "/settings" },

];

export const SideBar: FC = () => {

    const pathname = usePathname();

    return (
        <aside className='sidebar-container'>
            <nav>
                {NavItems.map((item) => {
                    const isActive = pathname === item.path || (item.path !== '/' && pathname.startsWith(item.path));

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
        </aside>
    );
}