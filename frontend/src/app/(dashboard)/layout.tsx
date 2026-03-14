import { SideBar } from "@/components/layout/sidebar";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    return (
        <div className="app-layout">
            <SideBar />
            <main className="app-content">{children}</main>
        </div>
    );
}