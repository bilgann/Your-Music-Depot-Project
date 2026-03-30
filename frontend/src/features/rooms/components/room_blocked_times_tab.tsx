import Button from "@/components/ui/button";
import DataTable from "@/components/ui/data_table";
import type { RoomBlockedTime } from "@/features/rooms/api/room_detail";

interface Props {
    blockedTimes: RoomBlockedTime[];
    onAdd: () => void;
    onDelete: (index: number) => void;
}

function formatWindow(item: RoomBlockedTime) {
    if (item.date) return item.date;
    if (item.date_range) return `${item.date_range.period_start} to ${item.date_range.period_end}`;
    if (item.recurrence) return item.recurrence.value;
    return "--";
}

export default function RoomBlockedTimesTab({ blockedTimes, onAdd, onDelete }: Props) {
    return (
        <>
            <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 16 }}>
                <Button variant="primary" onClick={onAdd}>Add Blocked Time</Button>
            </div>
            <DataTable
                loading={false}
                error={null}
                data={blockedTimes.map((item, index) => ({ ...item, _index: index }))}
                emptyMessage="No blocked times recorded for this room."
                getKey={(item) => `${item.label}-${item._index}`}
                columns={[
                    { header: "Label", render: (item) => item.label },
                    { header: "Type", render: (item) => item.block_type },
                    { header: "Window", render: (item) => formatWindow(item) },
                ]}
                onDelete={(item) => onDelete(item._index)}
            />
        </>
    );
}