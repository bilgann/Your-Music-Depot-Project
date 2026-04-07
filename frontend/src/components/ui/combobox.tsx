"use client";

import { useState, useRef, useEffect, useCallback } from "react";

interface Option {
    value: string;
    label: string;
}

interface ComboboxProps {
    label: string;
    value: string;
    onChange: (value: string, label?: string) => void;
    /** Static options list (used when fetchOptions is not provided). */
    options?: Option[];
    /** Async search function — overrides static options. Called with the current query. */
    fetchOptions?: (query: string) => Promise<Option[]>;
    /** Display label for the current value (used in async mode when editing). */
    valueLabel?: string;
    required?: boolean;
    placeholder?: string;
}

export function Combobox({
    label,
    value,
    onChange,
    options = [],
    fetchOptions,
    valueLabel,
    required,
    placeholder,
}: ComboboxProps) {
    const isAsync = !!fetchOptions;

    // Static mode: derive display text from options list
    const staticLabel = options.find((o) => o.value === value)?.label ?? "";
    const initialDisplay = isAsync ? (valueLabel ?? "") : staticLabel;

    const [query, setQuery] = useState(initialDisplay);
    const [open, setOpen] = useState(false);
    const [asyncOptions, setAsyncOptions] = useState<Option[]>([]);
    const [fetching, setFetching] = useState(false);
    const containerRef = useRef<HTMLDivElement>(null);
    const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

    // Sync display when external value/label changes
    useEffect(() => {
        if (isAsync) {
            setQuery(valueLabel ?? "");
        } else {
            setQuery(options.find((o) => o.value === value)?.label ?? "");
        }
    }, [value, valueLabel, options, isAsync]);

    // Close on outside click
    useEffect(() => {
        function handleClick(e: MouseEvent) {
            if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
                setOpen(false);
                // Revert display text to current selection
                if (isAsync) {
                    setQuery(valueLabel ?? "");
                } else {
                    setQuery(options.find((o) => o.value === value)?.label ?? "");
                }
            }
        }
        document.addEventListener("mousedown", handleClick);
        return () => document.removeEventListener("mousedown", handleClick);
    }, [value, valueLabel, options, isAsync]);

    const doFetch = useCallback(
        async (q: string) => {
            if (!fetchOptions) return;
            setFetching(true);
            try {
                const results = await fetchOptions(q);
                setAsyncOptions(results);
            } finally {
                setFetching(false);
            }
        },
        [fetchOptions]
    );

    function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
        const q = e.target.value;
        setQuery(q);
        onChange(""); // clear selection until user picks
        setOpen(true);

        if (isAsync) {
            if (debounceRef.current) clearTimeout(debounceRef.current);
            debounceRef.current = setTimeout(() => doFetch(q), 300);
        }
    }

    function handleFocus() {
        setOpen(true);
        if (isAsync && asyncOptions.length === 0) {
            doFetch(query);
        }
    }

    function handleSelect(opt: Option) {
        onChange(opt.value, opt.label);
        setQuery(opt.label);
        setOpen(false);
    }

    const displayOptions = isAsync ? asyncOptions : (
        query ? options.filter((o) => o.label.toLowerCase().includes(query.toLowerCase())) : options
    );

    return (
        <div className="form-field combobox-field" ref={containerRef}>
            <label>{label}</label>
            <input
                type="text"
                value={query}
                onChange={handleInputChange}
                onFocus={handleFocus}
                placeholder={placeholder ?? `Search ${label.toLowerCase()}…`}
                required={required && !value}
                autoComplete="off"
            />
            {required && <input type="hidden" value={value} required />}
            {open && (fetching ? (
                <ul className="combobox-list">
                    <li className="combobox-empty">Loading…</li>
                </ul>
            ) : displayOptions.length > 0 ? (
                <ul className="combobox-list">
                    {displayOptions.map((opt) => (
                        <li
                            key={opt.value}
                            className={`combobox-option${opt.value === value ? " combobox-option--selected" : ""}`}
                            onMouseDown={() => handleSelect(opt)}
                        >
                            {opt.label}
                        </li>
                    ))}
                </ul>
            ) : (
                <ul className="combobox-list">
                    <li className="combobox-empty">No results</li>
                </ul>
            ))}
        </div>
    );
}
