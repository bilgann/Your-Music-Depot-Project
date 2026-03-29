interface TextFieldProps {
    label: string;
    value: string;
    onChange: (v: string) => void;
    type?: "text" | "email";
    required?: boolean;
}

export function TextField({ label, value, onChange, type = "text", required }: TextFieldProps) {
    return (
        <div className="form-field">
            <label>{label}</label>
            <input type={type} value={value} onChange={(e) => onChange(e.target.value)} required={required} />
        </div>
    );
}

interface NumberFieldProps {
    label: string;
    value: string;
    onChange: (v: string) => void;
    min?: number;
    step?: number;
    required?: boolean;
}

export function NumberField({ label, value, onChange, min, step, required }: NumberFieldProps) {
    return (
        <div className="form-field">
            <label>{label}</label>
            <input type="number" value={value} onChange={(e) => onChange(e.target.value)} min={min} step={step} required={required} />
        </div>
    );
}

interface SelectOption {
    label: string;
    value: string;
}

interface SelectFieldProps {
    label: string;
    value: string;
    onChange: (v: string) => void;
    options: SelectOption[];
    required?: boolean;
    placeholder?: string;
}

export function SelectField({ label, value, onChange, options, required, placeholder }: SelectFieldProps) {
    return (
        <div className="form-field">
            <label>{label}</label>
            <select value={value} onChange={(e) => onChange(e.target.value)} required={required}>
                <option value="">{placeholder ?? `Select ${label.toLowerCase()}`}</option>
                {options.map((o) => (
                    <option key={o.value} value={o.value}>{o.label}</option>
                ))}
            </select>
        </div>
    );
}
