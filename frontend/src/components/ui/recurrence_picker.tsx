import { useEffect, useState } from "react";

type RecurrenceType = "one_time" | "cron";
type CronPreset = "weekly" | "monthly" | "custom";

interface Props {
    value: string;
    onChange: (value: string) => void;
    periodStart?: string;
    periodEnd?: string;
    onPeriodChange?: (start: string, end: string) => void;
    required?: boolean;
    showOneTime?: boolean;
}

const DAYS = [
    { value: "MON", label: "Mo" },
    { value: "TUE", label: "Tu" },
    { value: "WED", label: "We" },
    { value: "THU", label: "Th" },
    { value: "FRI", label: "Fr" },
    { value: "SAT", label: "Sa" },
    { value: "SUN", label: "Su" },
];

const DAY_NAMES: Record<string, string> = {
    MON: "Monday", TUE: "Tuesday", WED: "Wednesday", THU: "Thursday",
    FRI: "Friday", SAT: "Saturday", SUN: "Sunday",
};

function ordinal(n: number): string {
    const s = ["th", "st", "nd", "rd"];
    const v = n % 100;
    return n + (s[(v - 20) % 10] || s[v] || s[0]);
}

/** Detect whether a raw value is a cron expression (5 space-separated fields). */
function isCron(raw: string): boolean {
    return raw.trim().split(/\s+/).length === 5;
}

/** Infer the preset from a cron expression. */
function inferPreset(cron: string): CronPreset {
    const parts = cron.trim().split(/\s+/);
    if (parts.length !== 5) return "weekly";
    const [, , dayOfMonth, , dayOfWeek] = parts;
    if (dayOfWeek !== "*") return "weekly";
    if (dayOfMonth !== "*") return "monthly";
    return "custom";
}

/** Extract selected days from a weekly cron like "0 0 * * MON,WED". */
function parseDays(cron: string): string[] {
    const parts = cron.trim().split(/\s+/);
    if (parts.length !== 5 || parts[4] === "*") return [];
    return parts[4].split(",").map((d) => d.toUpperCase());
}

/** Extract day-of-month from a monthly cron like "0 0 15 * *". */
function parseMonthDay(cron: string): number {
    const parts = cron.trim().split(/\s+/);
    if (parts.length !== 5 || parts[2] === "*") return 1;
    return parseInt(parts[2], 10) || 1;
}

function buildWeeklyCron(days: string[]): string {
    if (days.length === 0) return "";
    const ordered = DAYS.map((d) => d.value).filter((v) => days.includes(v));
    return `0 0 * * ${ordered.join(",")}`;
}

function buildMonthlyCron(day: number): string {
    return `0 0 ${day} * *`;
}

function describeValue(type: RecurrenceType, preset: CronPreset, days: string[], monthDay: number, dateValue: string, customCron: string): string {
    if (type === "one_time") {
        return dateValue ? `One time on ${dateValue}` : "One time";
    }
    if (preset === "weekly") {
        if (days.length === 0) return "Weekly — select days";
        const names = DAYS.filter((d) => days.includes(d.value)).map((d) => DAY_NAMES[d.value]);
        if (names.length === 1) return `Every ${names[0]}`;
        return `Every ${names.slice(0, -1).join(", ")} and ${names[names.length - 1]}`;
    }
    if (preset === "monthly") {
        return `Monthly on the ${ordinal(monthDay)}`;
    }
    if (preset === "custom") {
        return customCron ? `Cron: ${customCron}` : "Enter a cron expression";
    }
    return "";
}

export default function RecurrencePicker({ value, onChange, periodStart, periodEnd, onPeriodChange, required, showOneTime = true }: Props) {
    const existingIsCron = isCron(value);

    const [type, setType] = useState<RecurrenceType>(
        existingIsCron ? "cron" : (showOneTime ? "one_time" : "cron")
    );
    const [preset, setPreset] = useState<CronPreset>(
        existingIsCron ? inferPreset(value) : "weekly"
    );
    const [selectedDays, setSelectedDays] = useState<string[]>(
        existingIsCron ? parseDays(value) : []
    );
    const [monthDay, setMonthDay] = useState(
        existingIsCron ? parseMonthDay(value) : 1
    );
    const [dateValue, setDateValue] = useState(existingIsCron ? "" : value);
    const [customCron, setCustomCron] = useState(
        existingIsCron && inferPreset(value) === "custom" ? value : ""
    );

    useEffect(() => {
        if (type === "one_time") {
            onChange(dateValue);
            return;
        }
        let cron = "";
        if (preset === "weekly") cron = buildWeeklyCron(selectedDays);
        else if (preset === "monthly") cron = buildMonthlyCron(monthDay);
        else if (preset === "custom") cron = customCron;
        if (cron) onChange(cron);
    }, [type, preset, selectedDays, monthDay, dateValue, customCron]);

    function toggleDay(day: string) {
        setSelectedDays((prev) =>
            prev.includes(day) ? prev.filter((d) => d !== day) : [...prev, day]
        );
    }

    function handleTypeChange(newType: RecurrenceType) {
        setType(newType);
        if (newType === "one_time") {
            setPreset("weekly");
            setSelectedDays([]);
        }
    }

    const preview = describeValue(type, preset, selectedDays, monthDay, dateValue, customCron);
    const isRecurring = type === "cron";

    return (
        <div className="recurrence-picker">
            <label className="recurrence-picker__label">Recurrence</label>

            <div className="recurrence-picker__controls">
                {/* Type selector */}
                <div className="recurrence-picker__type">
                    {showOneTime && (
                        <button
                            type="button"
                            className={`recurrence-tab${type === "one_time" ? " recurrence-tab--active" : ""}`}
                            onClick={() => handleTypeChange("one_time")}
                        >
                            One Time
                        </button>
                    )}
                    <button
                        type="button"
                        className={`recurrence-tab${type === "cron" ? " recurrence-tab--active" : ""}`}
                        onClick={() => handleTypeChange("cron")}
                    >
                        Recurring
                    </button>
                </div>

                {/* One-time: date input */}
                {type === "one_time" && (
                    <input
                        className="recurrence-picker__date"
                        type="date"
                        value={dateValue}
                        onChange={(e) => setDateValue(e.target.value)}
                        required={required}
                    />
                )}

                {/* Recurring: preset selector + fields */}
                {type === "cron" && (
                    <>
                        <div className="recurrence-picker__preset">
                            {([["weekly", "Weekly"], ["monthly", "Monthly"], ["custom", "Custom"]] as const).map(([key, label]) => (
                                <button
                                    key={key}
                                    type="button"
                                    className={`recurrence-tab${preset === key ? " recurrence-tab--active" : ""}`}
                                    onClick={() => setPreset(key)}
                                >
                                    {label}
                                </button>
                            ))}
                        </div>

                        {preset === "weekly" && (
                            <div className="recurrence-picker__days">
                                {DAYS.map((day) => (
                                    <button
                                        key={day.value}
                                        type="button"
                                        onClick={() => toggleDay(day.value)}
                                        className={`day-toggle day-toggle--sm${selectedDays.includes(day.value) ? " day-toggle--active" : ""}`}
                                        title={DAY_NAMES[day.value]}
                                    >
                                        {day.label}
                                    </button>
                                ))}
                            </div>
                        )}

                        {preset === "monthly" && (
                            <div className="recurrence-picker__month-day">
                                <label>Day of month</label>
                                <input
                                    type="number"
                                    min={1}
                                    max={31}
                                    value={monthDay}
                                    onChange={(e) => setMonthDay(Math.max(1, Math.min(31, parseInt(e.target.value, 10) || 1)))}
                                />
                            </div>
                        )}

                        {preset === "custom" && (
                            <div className="recurrence-picker__custom">
                                <input
                                    type="text"
                                    placeholder="e.g. 0 15 * * MON,WED"
                                    value={customCron}
                                    onChange={(e) => setCustomCron(e.target.value)}
                                    required={required}
                                    spellCheck={false}
                                />
                                <span className="recurrence-picker__hint">
                                    Format: minute hour day-of-month month day-of-week
                                </span>
                            </div>
                        )}
                    </>
                )}

                {/* Period range for recurring */}
                {isRecurring && onPeriodChange && (
                    <div className="recurrence-picker__period">
                        <div className="form-field">
                            <label>Period Start</label>
                            <input
                                type="date"
                                value={periodStart ?? ""}
                                onChange={(e) => onPeriodChange(e.target.value, periodEnd ?? "")}
                                required={required}
                            />
                        </div>
                        <div className="form-field">
                            <label>Period End</label>
                            <input
                                type="date"
                                value={periodEnd ?? ""}
                                onChange={(e) => onPeriodChange(periodStart ?? "", e.target.value)}
                                required={required}
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* Preview */}
            {preview && (
                <p className="recurrence-picker__preview">{preview}</p>
            )}
        </div>
    );
}
