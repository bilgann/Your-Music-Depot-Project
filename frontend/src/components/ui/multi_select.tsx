import { useRef, useState } from "react";

type Option = { value: string; label: string };

interface Props {
    label: string;
    options: Option[];
    selected: string[];
    onChange: (selected: string[]) => void;
    placeholder?: string;
    hint?: string;
    max?: number;
    disabled?: boolean;
}

export default function MultiSelect({ label, options, selected, onChange, placeholder, hint, max, disabled }: Props) {
    const [query, setQuery] = useState("");
    const [open, setOpen] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);

    const filtered = options.filter(
        (o) => !selected.includes(o.value) && o.label.toLowerCase().includes(query.toLowerCase()),
    );

    const selectedOptions = selected
        .map((v) => options.find((o) => o.value === v))
        .filter(Boolean) as Option[];

    const atMax = max !== undefined && selected.length >= max;

    function add(value: string) {
        if (atMax) return;
        onChange([...selected, value]);
        setQuery("");
    }

    function remove(value: string) {
        onChange(selected.filter((v) => v !== value));
    }

    function handleBlur(e: React.FocusEvent) {
        if (!containerRef.current?.contains(e.relatedTarget as Node)) {
            setOpen(false);
        }
    }

    return (
        <div className="form-field" ref={containerRef} onBlur={handleBlur}>
            <label>{label}</label>

            {selectedOptions.length > 0 && (
                <div className="multi-select-chips">
                    {selectedOptions.map((opt) => (
                        <span key={opt.value} className="multi-select-chip">
                            {opt.label}
                            <button type="button" onClick={() => remove(opt.value)} className="multi-select-chip-remove">
                                &times;
                            </button>
                        </span>
                    ))}
                </div>
            )}

            <div className="multi-select-input-wrapper">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onFocus={() => setOpen(true)}
                    placeholder={atMax ? `Maximum of ${max} reached` : (placeholder ?? `Search ${label.toLowerCase()}...`)}
                    disabled={disabled || atMax}
                />
                {open && !atMax && filtered.length > 0 && (
                    <div className="multi-select-dropdown">
                        {filtered.map((opt) => (
                            <button
                                key={opt.value}
                                type="button"
                                className="multi-select-option"
                                onMouseDown={(e) => e.preventDefault()}
                                onClick={() => add(opt.value)}
                            >
                                {opt.label}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            {hint && <p className="table-empty" style={{ marginTop: 8 }}>{hint}</p>}
        </div>
    );
}
