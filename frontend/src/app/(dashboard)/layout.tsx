import { AuthProvider } from "@/context/auth";
import { SideBar } from "@/components/layout/sidebar";
import { ToastProvider } from "@/components/ui/toast";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    return (
        <AuthProvider>
            <ToastProvider>
                <div className="app-layout">
                    <SideBar />
                    <main className="app-content">{children}</main>
                </div>
            </ToastProvider>
        </AuthProvider>
    );
}
