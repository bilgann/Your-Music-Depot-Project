import InfoCard from "@/components/ui/info_card";
import type { RoomDetail } from "@/features/rooms/api/room_detail";

interface Props {
    room: RoomDetail;
}

function formatInstruments(room: RoomDetail) {
    if (!room.instruments?.length) return "--";
    return room.instruments
        .map((instrument) => `${instrument.name}${instrument.quantity ? ` x${instrument.quantity}` : ""}`)
        .join(", ");
}

export default function RoomInfoCard({ room }: Props) {
    return (
        <InfoCard
            rows={[
                { label: "Name", value: room.name },
                { label: "Capacity", value: room.capacity ?? "--" },
                { label: "Instruments", value: formatInstruments(room) },
                { label: "Blocked Times", value: room.blocked_times?.length ?? 0 },
            ]}
        />
    );
}