import Button from "@/components/ui/button";
import DataTable from "@/components/ui/data_table";
import type { RoomInstrument } from "@/features/rooms/api/room_detail";

interface Props {
    instruments: RoomInstrument[];
    onAdd: () => void;
    onMove: (index: number) => void;
    onDelete: (index: number) => void;
}

const FAMILY_LABELS: Record<string, string> = {
    keyboard: "Keyboard",
    strings: "Strings",
    woodwind: "Woodwind",
    brass: "Brass",
    percussion: "Percussion",
    voice: "Voice",
    other: "Other",
};

type IndexedInstrument = RoomInstrument & { _index: number };

export default function RoomInstrumentsTab({ instruments, onAdd, onMove, onDelete }: Props) {
    const data: IndexedInstrument[] = instruments.map((item, index) => ({ ...item, _index: index }));

    return (
        <>
            <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 16 }}>
                <Button variant="primary" onClick={onAdd}>Add Instrument</Button>
            </div>
            <DataTable
                loading={false}
                error={null}
                data={data}
                emptyMessage="No instruments in this room."
                getKey={(item) => `${item.name}-${item._index}`}
                columns={[
                    { header: "Instrument", render: (item) => item.name },
                    { header: "Family", render: (item) => FAMILY_LABELS[item.family] ?? item.family },
                    { header: "Quantity", render: (item) => item.quantity ?? "--" },
                    {
                        header: "Actions",
                        render: (item) => (
                            <div className="actions-cell">
                                <Button variant="secondary" onClick={() => onMove(item._index)}>
                                    Move
                                </Button>
                                <Button variant="danger" onClick={() => onDelete(item._index)}>
                                    Remove
                                </Button>
                            </div>
                        ),
                    },
                ]}
            />
        </>
    );
}
