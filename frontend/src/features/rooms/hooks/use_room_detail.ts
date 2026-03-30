import { useEffect, useMemo, useState } from "react";
import { getInstructors } from "@/features/instructors/api/instructor";
import {
    buildRoomSessions,
    getRoomById,
    getRoomLessons,
    updateRoomBlockedTimes,
} from "@/features/rooms/api/room_detail";
import { getStudents } from "@/features/students/api/student";
import { useToast } from "@/components/ui/toast";
import type { Instructor } from "@/features/instructors/api/instructor";
import type { Student } from "@/features/students/api/student";
import type { RoomBlockedTime, RoomDetail, RoomSession } from "@/features/rooms/api/room_detail";

export type BlockedTimeFormState = {
    label: string;
    block_type: string;
    start_date: string;
    end_date: string;
};

const emptyBlockedTimeForm: BlockedTimeFormState = {
    label: "",
    block_type: "other",
    start_date: "",
    end_date: "",
};

function toBlockedTimePayload(form: BlockedTimeFormState): RoomBlockedTime {
    if (form.start_date && form.end_date && form.start_date !== form.end_date) {
        return {
            label: form.label,
            block_type: form.block_type,
            date_range: {
                period_start: form.start_date,
                period_end: form.end_date,
            },
        };
    }

    return {
        label: form.label,
        block_type: form.block_type,
        date: form.start_date || form.end_date,
    };
}

export function useRoomDetail(roomId: string) {
    const { toast } = useToast();
    const [room, setRoom] = useState<RoomDetail | null>(null);
    const [lessons, setLessons] = useState<RoomSession[]>([]);
    const [instructors, setInstructors] = useState<Instructor[]>([]);
    const [students, setStudents] = useState<Student[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showBlockedTimeModal, setShowBlockedTimeModal] = useState(false);
    const [blockedTimeForm, setBlockedTimeForm] = useState<BlockedTimeFormState>(emptyBlockedTimeForm);
    const [savingBlockedTime, setSavingBlockedTime] = useState(false);

    async function refresh() {
        try {
            setLoading(true);
            const [roomData, lessonData, instructorData, studentData] = await Promise.all([
                getRoomById(roomId),
                getRoomLessons(),
                getInstructors(),
                getStudents(),
            ]);

            setRoom(roomData);
            setInstructors(instructorData);
            setStudents(studentData);
            setLessons(buildRoomSessions(lessonData, roomId, instructorData, studentData));
            setError(null);
        } catch {
            setError("Could not load room details.");
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => { void refresh(); }, [roomId]);

    const upcomingSessions = useMemo(
        () => lessons.filter((lesson) => new Date(lesson.start_time).getTime() >= Date.now()),
        [lessons]
    );

    const blockedTimes = room?.blocked_times ?? [];

    function openBlockedTimeModal() {
        setBlockedTimeForm(emptyBlockedTimeForm);
        setShowBlockedTimeModal(true);
    }

    async function handleBlockedTimeSubmit(e: React.FormEvent) {
        e.preventDefault();
        if (!room) return;
        setSavingBlockedTime(true);
        try {
            const nextBlockedTimes = [...blockedTimes, toBlockedTimePayload(blockedTimeForm)];
            const updated = await updateRoomBlockedTimes(room.room_id, nextBlockedTimes);
            setRoom(updated);
            setShowBlockedTimeModal(false);
        } catch {
            toast("Failed to save blocked time.", "error");
        } finally {
            setSavingBlockedTime(false);
        }
    }

    async function handleBlockedTimeDelete(index: number) {
        if (!room) return;
        if (!confirm("Delete this blocked time?")) return;
        try {
            const nextBlockedTimes = blockedTimes.filter((_, blockedIndex) => blockedIndex !== index);
            const updated = await updateRoomBlockedTimes(room.room_id, nextBlockedTimes);
            setRoom(updated);
        } catch {
            toast("Failed to delete blocked time.", "error");
        }
    }

    return {
        room,
        upcomingSessions,
        blockedTimes,
        loading,
        error,
        refresh,
        showBlockedTimeModal,
        setShowBlockedTimeModal,
        blockedTimeForm,
        setBlockedTimeForm,
        savingBlockedTime,
        openBlockedTimeModal,
        handleBlockedTimeSubmit,
        handleBlockedTimeDelete,
    };
}