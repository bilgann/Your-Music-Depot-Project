import React from "react";

interface InfoRow {
    label: string;
    value: React.ReactNode;
    className?: string;
}

interface Props {
    rows: InfoRow[];
}

export default function InfoCard({ rows }: Props) {
    return (
        <div className="client-info-card">
            {rows.map((row) => (
                <div key={row.label} className="client-info-row">
                    <span className="client-info-label">{row.label}</span>
                    <span className={`client-info-value${row.className ? ` ${row.className}` : ""}`}>{row.value}</span>
                </div>
            ))}
        </div>
    );
}
