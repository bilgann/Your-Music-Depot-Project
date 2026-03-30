import { useEffect, useState } from "react";
import { createCourse, deleteCourse, updateCourse } from "@/features/courses/api/course";
import { getInstructors } from "@/features/instructors/api/instructor";
import { getRooms } from "@/features/rooms/api/room";
import { useToast } from "@/components/ui/toast";
import type { Course, CourseInstrument } from "@/features/courses/api/course";

type Option = { value: string; label: string };

export type CourseFormState = {
    name: string;
    description: string;
    room_id: string;
    instructor_ids: string[];
    period_start: string;
    period_end: string;
    recurrence: string;
    start_time: string;
    end_time: string;
    charge_type: "one_time" | "hourly";
    rate_amount: string;
    capacity: string;
    status: string;
    skill_min: string;
    skill_max: string;
    required_instruments: CourseInstrument[];
};

const emptyForm: CourseFormState = {
    name: "",
    description: "",
    room_id: "",
    instructor_ids: [],
    period_start: "",
    period_end: "",
    recurrence: "",
    start_time: "",
    end_time: "",
    charge_type: "one_time",
    rate_amount: "",
    capacity: "",
    status: "draft",
    skill_min: "",
    skill_max: "",
    required_instruments: [],
};

function toFormState(course: Course): CourseFormState {
    return {
        name: course.name,
        description: course.description ?? "",
        room_id: course.room_id,
        instructor_ids: course.instructor_ids ?? [],
        period_start: course.period_start,
        period_end: course.period_end,
        recurrence: course.recurrence,
        start_time: course.start_time,
        end_time: course.end_time,
        charge_type: course.rate?.charge_type ?? "one_time",
        rate_amount: course.rate?.amount ? String(course.rate.amount) : "",
        capacity: course.capacity ? String(course.capacity) : "",
        status: course.status ?? "draft",
        skill_min: course.skill_range?.min_level ?? "",
        skill_max: course.skill_range?.max_level ?? "",
        required_instruments: course.required_instruments ?? [],
    };
}

export function useCourseCrud(refresh: () => Promise<void>) {
    const { toast } = useToast();
    const [showModal, setShowModal] = useState(false);
    const [editing, setEditing] = useState<Course | null>(null);
    const [form, setForm] = useState<CourseFormState>(emptyForm);
    const [saving, setSaving] = useState(false);
    const [rooms, setRooms] = useState<Option[]>([]);
    const [instructors, setInstructors] = useState<Option[]>([]);

    useEffect(() => {
        async function loadOptions() {
            try {
                const [roomData, instructorData] = await Promise.all([
                    getRooms(),
                    getInstructors(),
                ]);
                setRooms(roomData.map((room) => ({ value: room.room_id, label: room.name })));
                setInstructors(instructorData.map((instructor) => ({ value: instructor.instructor_id, label: instructor.name })));
            } catch {
                setRooms([]);
                setInstructors([]);
            }
        }

        void loadOptions();
    }, []);

    function openAdd() {
        setEditing(null);
        setForm(emptyForm);
        setShowModal(true);
    }

    function openEdit(course: Course) {
        setEditing(course);
        setForm(toFormState(course));
        setShowModal(true);
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();

        if (form.instructor_ids.length === 0) {
            toast("Select at least one instructor.", "error");
            return;
        }

        if ((form.skill_min && !form.skill_max) || (!form.skill_min && form.skill_max)) {
            toast("Provide both minimum and maximum skill levels.", "error");
            return;
        }

        setSaving(true);
        try {
            const payload = {
                name: form.name,
                room_id: form.room_id,
                instructor_ids: form.instructor_ids,
                recurrence: form.recurrence,
                start_time: form.start_time,
                end_time: form.end_time,
                period_start: form.period_start,
                period_end: form.period_end,
                ...(form.description && { description: form.description }),
                ...(form.rate_amount && {
                    rate: {
                        charge_type: form.charge_type,
                        amount: Number(form.rate_amount),
                        currency: "CAD",
                    },
                }),
                ...(form.required_instruments.length > 0 && { required_instruments: form.required_instruments }),
                ...(form.capacity && { capacity: Number(form.capacity) }),
                ...(form.skill_min && form.skill_max && {
                    skill_range: {
                        min_level: form.skill_min,
                        max_level: form.skill_max,
                    },
                }),
                ...(form.status && { status: form.status }),
            };

            if (editing) {
                await updateCourse(editing.course_id, payload);
            } else {
                await createCourse(payload);
            }

            setShowModal(false);
            toast(editing ? "Course updated." : "Course created.", "success");
            await refresh();
        } catch {
            toast("Failed to save course.", "error");
        } finally {
            setSaving(false);
        }
    }

    async function handleDelete(course: Course) {
        if (!confirm("Delete this course?")) return;
        try {
            await deleteCourse(course.course_id);
            toast("Course deleted.", "success");
            await refresh();
        } catch {
            toast("Failed to delete course.", "error");
        }
    }

    return {
        showModal,
        setShowModal,
        editing,
        form,
        setForm,
        saving,
        rooms,
        instructors,
        openAdd,
        openEdit,
        handleSubmit,
        handleDelete,
    };
}