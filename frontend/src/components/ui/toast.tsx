"use client";

import { createContext, useCallback, useContext, useState, type FC, type ReactNode } from "react";

type ToastVariant = "success" | "error" | "info";

interface Toast {
    id: number;
    message: string;
    variant: ToastVariant;
}

interface ToastContextValue {
    toast: (message: string, variant?: ToastVariant) => void;
}

const ToastContext = createContext<ToastContextValue>({ toast: () => {} });

export const useToast = () => useContext(ToastContext);

let nextId = 0;

export const ToastProvider: FC<{ children: ReactNode }> = ({ children }) => {
    const [toasts, setToasts] = useState<Toast[]>([]);

    const toast = useCallback((message: string, variant: ToastVariant = "info") => {
        const id = ++nextId;
        setToasts((prev) => [...prev, { id, message, variant }]);
        setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 3500);
    }, []);

    return (
        <ToastContext.Provider value={{ toast }}>
            {children}
            {toasts.length > 0 && (
                <div className="toast-container">
                    {toasts.map((t) => (
                        <div key={t.id} className={`toast toast--${t.variant}`}>
                            {t.message}
                        </div>
                    ))}
                </div>
            )}
        </ToastContext.Provider>
    );
};
