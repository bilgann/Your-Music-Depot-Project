"use client";

import Link from "next/link";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faArrowLeft, type IconDefinition } from "@fortawesome/free-solid-svg-icons";

export type ButtonVariant =
    | "primary" | "secondary" | "danger"
    | "back"
    | "icon" | "icon-danger"
    | "sidebar" | "sidebar-logout"
    | "action-primary" | "action-secondary" | "action-ghost"
    | "cal-control" | "cal-save" | "cal-cancel"
    | "event-edit" | "event-delete"
    | "login" | "login-toggle";

const CLASS_MAP: Record<ButtonVariant, string> = {
    primary:           "btn btn-primary",
    secondary:         "btn btn-secondary",
    danger:            "btn btn-danger",
    back:              "btn-back",
    icon:              "btn-icon",
    "icon-danger":     "btn-icon btn-icon--danger",
    sidebar:           "sidebar-link",
    "sidebar-logout":  "sidebar-logout",
    "action-primary":  "action-btn action-btn--primary",
    "action-secondary":"action-btn action-btn--secondary",
    "action-ghost":    "action-btn action-btn--ghost",
    "cal-control":     "today-button",
    "cal-save":        "top-save-btn",
    "cal-cancel":      "top-cancel-btn",
    "event-edit":      "event-edit-btn",
    "event-delete":    "event-delete-btn",
    "login":           "login-submit",
    "login-toggle":    "login-toggle-password",
};

interface ButtonProps {
    variant?: ButtonVariant;
    icon?: IconDefinition;
    href?: string;
    onClick?: () => void;
    disabled?: boolean;
    type?: "button" | "submit" | "reset";
    active?: boolean;
    title?: string;
    className?: string;
    children?: React.ReactNode;
}

export default function Button({
    variant = "primary",
    icon,
    href,
    onClick,
    disabled,
    type = "button",
    active,
    title,
    className,
    children,
}: ButtonProps) {
    const cls = [CLASS_MAP[variant], active && "active", className].filter(Boolean).join(" ");
    const resolvedIcon = icon ?? (variant === "back" ? faArrowLeft : undefined);

    const content = (
        <>
            {resolvedIcon && <FontAwesomeIcon icon={resolvedIcon} />}
            {children}
        </>
    );

    if (href) {
        return <Link href={href} className={cls} title={title} onClick={onClick}>{content}</Link>;
    }

    return (
        <button className={cls} onClick={onClick} disabled={disabled} type={type} title={title}>
            {content}
        </button>
    );
}
