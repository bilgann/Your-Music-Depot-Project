import { useEffect, useMemo, useState } from "react";
import { getInstructors } from "@/features/instructors/api/instructor";
import {
    buildRoomSessions,
    getRoomById,
    getRoomLessons,
    updateRoomBlockedTimes,
    updateRoomInstruments,
} from "@/features/rooms/api/room_detail";
import { getRooms } from "@/features/rooms/api/room";
import { getStudents } from "@/features/students/api/student";
import { useToast } from "@/components/ui/toast";
import type { Instructor } from "@/features/instructors/api/instructor";
import type { Student } from "@/features/students/api/student";
import type { Room } from "@/features/rooms/api/room";
import type { RoomBlockedTime, RoomDetail, RoomInstrument, RoomSession } from "@/features/rooms/api/room_detail";

export type BlockedTimeFormState = {
    label: string;
    block_type: string;
    start_date: string;
    end_date: string;
    recurrence_mode: "none" | "recurring";
    recurrence: string;
};

const emptyBlockedTimeForm: BlockedTimeFormState = {
    label: "",
    block_type: "other",
    start_date: "",
    end_date: "",
    recurrence_mode: "none",
    recurrence: "",
};

function toBlockedTimePayload(form: BlockedTimeFormState): RoomBlockedTime {
    if (form.recurrence_mode === "recurring" && form.recurrence) {
        return {
            label: form.label,
            block_type: form.block_type,
            recurrence: { rule_type: "cron", value: form.recurrence },
        };
    }

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

    const [allRooms, setAllRooms] = useState<Room[]>([]);
    const [showAddInstrumentModal, setShowAddInstrumentModal] = useState(false);
    const [showMoveInstrumentModal, setShowMoveInstrumentModal] = useState(false);
    const [moveInstrumentIndex, setMoveInstrumentIndex] = useState<number | null>(null);
    const [savingInstrument, setSavingInstrument] = useState(false);

    async function refresh() {
        try {
            setLoading(true);
            const [roomData, lessonData, instructorData, studentData, roomsData] = await Promise.all([
                getRoomById(roomId),
                getRoomLessons(),
                getInstructors(),
                getStudents(),
                getRooms(),
            ]);

            setRoom(roomData);
            setInstructors(instructorData);
            setStudents(studentData);
            setAllRooms(roomsData);
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

    // ── Instrument management ────────────────────────────────────────────

    const instruments = room?.instruments ?? [];
    const otherRoomOptions = allRooms
        .filter((r) => r.room_id !== roomId)
        .map((r) => ({ value: r.room_id, label: r.name }));

    function openAddInstrumentModal() {
        setShowAddInstrumentModal(true);
    }

    function openMoveInstrumentModal(index: number) {
        setMoveInstrumentIndex(index);
        setShowMoveInstrumentModal(true);
    }

    async function handleAddInstrument(instrument: RoomInstrument) {
        if (!room) return;
        setSavingInstrument(true);
        try {
            const existing = instruments.findIndex(
                (i) => i.name === instrument.name && i.family === instrument.family,
            );
            let next: RoomInstrument[];
            if (existing >= 0) {
                next = instruments.map((i, idx) =>
                    idx === existing
                        ? { ...i, quantity: (i.quantity ?? 0) + (instrument.quantity ?? 0) }
                        : i,
                );
            } else {
                next = [...instruments, instrument];
            }
            const updated = await updateRoomInstruments(room.room_id, next);
            setRoom(updated);
            setShowAddInstrumentModal(false);
            toast("Instrument added.", "success");
        } catch {
            toast("Failed to add instrument.", "error");
        } finally {
            setSavingInstrument(false);
        }
    }

    async function handleDeleteInstrument(index: number) {
        if (!room) return;
        if (!confirm("Remove this instrument from the room?")) return;
        try {
            const next = instruments.filter((_, i) => i !== index);
            const updated = await updateRoomInstruments(room.room_id, next);
            setRoom(updated);
            toast("Instrument removed.", "success");
        } catch {
            toast("Failed to remove instrument.", "error");
        }
    }

    async function handleMoveInstrument(targetRoomId: string, quantity: number) {
        if (!room || moveInstrumentIndex === null) return;
        const source = instruments[moveInstrumentIndex];
        if (!source) return;

        setSavingInstrument(true);
        try {
            // Update source room: reduce quantity or remove
            const remaining = (source.quantity ?? 0) - quantity;
            const nextSourceInstruments = remaining > 0
                ? instruments.map((inst, idx) =>
                    idx === moveInstrumentIndex ? { ...inst, quantity: remaining } : inst,
                )
                : instruments.filter((_, idx) => idx !== moveInstrumentIndex);

            // Fetch target room to get its current instruments
            const targetRoom = await getRoomById(targetRoomId);
            const targetInstruments = targetRoom.instruments ?? [];

            // Merge into target: add quantity to existing or append
            const existingIdx = targetInstruments.findIndex(
                (i) => i.name === source.name && i.family === source.family,
            );
            let nextTargetInstruments: RoomInstrument[];
            if (existingIdx >= 0) {
                nextTargetInstruments = targetInstruments.map((inst, idx) =>
                    idx === existingIdx
                        ? { ...inst, quantity: (inst.quantity ?? 0) + quantity }
                        : inst,
                );
            } else {
                nextTargetInstruments = [...targetInstruments, { name: source.name, family: source.family, quantity }];
            }

            // Persist both rooms
            const [updatedSource] = await Promise.all([
                updateRoomInstruments(room.room_id, nextSourceInstruments),
                updateRoomInstruments(targetRoomId, nextTargetInstruments),
            ]);

            setRoom(updatedSource);
            setShowMoveInstrumentModal(false);
            setMoveInstrumentIndex(null);
            const targetName = allRooms.find((r) => r.room_id === targetRoomId)?.name ?? "other room";
            toast(`Moved ${quantity} ${source.name} to ${targetName}.`, "success");
        } catch {
            toast("Failed to move instrument.", "error");
        } finally {
            setSavingInstrument(false);
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
        // Instruments
        instruments,
        otherRoomOptions,
        showAddInstrumentModal,
        setShowAddInstrumentModal,
        showMoveInstrumentModal,
        setShowMoveInstrumentModal,
        moveInstrumentIndex,
        savingInstrument,
        openAddInstrumentModal,
        openMoveInstrumentModal,
        handleAddInstrument,
        handleDeleteInstrument,
        handleMoveInstrument,
    };
}