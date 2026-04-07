import Sections from "@/components/ui/sections";
import RoomBlockedTimesTab from "@/features/rooms/components/room_blocked_times_tab";
import RoomInstrumentsTab from "@/features/rooms/components/room_instruments_tab";
import RoomSessionsTab from "@/features/rooms/components/room_sessions_tab";
import type { RoomBlockedTime, RoomInstrument, RoomSession } from "@/features/rooms/api/room_detail";

interface Props {
    active: string;
    onChange: (key: string) => void;
    sessions: RoomSession[];
    blockedTimes: RoomBlockedTime[];
    onAddBlockedTime: () => void;
    onDeleteBlockedTime: (index: number) => void;
    instruments: RoomInstrument[];
    onAddInstrument: () => void;
    onMoveInstrument: (index: number) => void;
    onDeleteInstrument: (index: number) => void;
}

export default function RoomDetailTabs({
    active,
    onChange,
    sessions,
    blockedTimes,
    onAddBlockedTime,
    onDeleteBlockedTime,
    instruments,
    onAddInstrument,
    onMoveInstrument,
    onDeleteInstrument,
}: Props) {
    return (
        <Sections
            active={active}
            onChange={onChange}
            sections={[
                {
                    key: "sessions",
                    label: "Upcoming Sessions",
                    content: <RoomSessionsTab sessions={sessions} />,
                },
                {
                    key: "instruments",
                    label: "Instruments",
                    content: (
                        <RoomInstrumentsTab
                            instruments={instruments}
                            onAdd={onAddInstrument}
                            onMove={onMoveInstrument}
                            onDelete={onDeleteInstrument}
                        />
                    ),
                },
                {
                    key: "blocked-times",
                    label: "Blocked Times",
                    content: <RoomBlockedTimesTab blockedTimes={blockedTimes} onAdd={onAddBlockedTime} onDelete={onDeleteBlockedTime} />,
                },
            ]}
        />
    );
}
