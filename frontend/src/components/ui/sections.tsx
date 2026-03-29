interface Section {
    key: string;
    label: string;
    content: React.ReactNode;
}

interface Props {
    sections: Section[];
    active: string;
    onChange: (key: string) => void;
}

export default function Sections({ sections, active, onChange }: Props) {
    const current = sections.find((s) => s.key === active);
    return (
        <>
            <div className="client-tabs">
                {sections.map((s) => (
                    <button
                        key={s.key}
                        className={`client-tab${active === s.key ? " active" : ""}`}
                        onClick={() => onChange(s.key)}
                    >
                        {s.label}
                    </button>
                ))}
            </div>
            {current?.content}
        </>
    );
}
