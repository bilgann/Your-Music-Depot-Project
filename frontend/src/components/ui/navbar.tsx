"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Button from "./button";

interface NavbarProps {
    title: React.ReactNode;
    back?: { label: string; href?: string; onClick?: () => void };
    search?: string;
    onSearchChange?: (s: string) => void;
    searchPlaceholder?: string;
    actions?: React.ReactNode;
    className?: string;
}

export default function Navbar({
    title,
    back,
    search,
    onSearchChange,
    searchPlaceholder,
    actions,
    className,
}: NavbarProps) {
    const [inputValue, setInputValue] = useState(search ?? "");
    useEffect(() => { setInputValue(search ?? ""); }, [search]);
    useEffect(() => {
        if (!onSearchChange) return;
        const t = setTimeout(() => onSearchChange(inputValue), 300);
        return () => clearTimeout(t);
    }, [inputValue]); // eslint-disable-line react-hooks/exhaustive-deps

    const searchEnabled = !!onSearchChange;

    return (
        <div className={["page-navbar", className].filter(Boolean).join(" ")}>
            <div className="page-navbar-left">
                {back ? (
                    <nav className="page-breadcrumb">
                        {back.href ? (
                            <Link href={back.href} className="breadcrumb-link">{back.label}</Link>
                        ) : (
                            <button className="breadcrumb-link" onClick={back.onClick}>{back.label}</button>
                        )}
                        <span className="breadcrumb-sep">/</span>
                        <h1>{title}</h1>
                    </nav>
                ) : (
                    <h1>{title}</h1>
                )}
            </div>
            {(searchEnabled || actions) && (
                <div className="page-navbar-right">
                    {searchEnabled && (
                        <input
                            className="table-search-input"
                            type="search"
                            placeholder={searchPlaceholder ?? (typeof title === "string" ? `Search ${title.toLowerCase()}…` : "Search…")}
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                        />
                    )}
                    {actions && <div className="page-navbar-actions">{actions}</div>}
                </div>
            )}
        </div>
    );
}
