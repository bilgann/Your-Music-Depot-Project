import Sections from "@/components/ui/sections";
import RoomBlockedTimesTab from "@/features/rooms/components/room_blocked_times_tab";
import RoomSessionsTab from "@/features/rooms/components/room_sessions_tab";
import type { RoomBlockedTime, RoomSession } from "@/features/rooms/api/room_detail";

interface Props {
    active: string;
    onChange: (key: string) => void;
    sessions: RoomSession[];
    blockedTimes: RoomBlockedTime[];
    onAddBlockedTime: () => void;
    onDeleteBlockedTime: (index: number) => void;
}

export default function RoomDetailTabs({
    active,
    onChange,
    sessions,
    blockedTimes,
    onAddBlockedTime,
    onDeleteBlockedTime,
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
                    key: "blocked-times",
                    label: "Blocked Times",
                    content: <RoomBlockedTimesTab blockedTimes={blockedTimes} onAdd={onAddBlockedTime} onDelete={onDeleteBlockedTime} />,
                },
            ]}
        />
    );
}