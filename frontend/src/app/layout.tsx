"use client";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { SideBar } from "@/components/layout/Sidebar/Sidebar";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <div className="app-layout">
          <SideBar />
          <main className="app-content">{children}</main>
        </div>
      </body>
    </html>
  );
}