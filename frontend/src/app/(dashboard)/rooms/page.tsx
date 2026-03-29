"use client";

import Navbar from "@/components/ui/navbar";
import DataTable from "@/components/ui/data_table";
import Modal from "@/components/ui/modal";
import Button from "@/components/ui/button";
import { TextField, NumberField } from "@/components/ui/fields";
import { useRooms } from "@/features/rooms/hooks/use_rooms";
import { useRoomCrud } from "@/features/rooms/hooks/use_room_crud";

export default function RoomsPage() {
    const { rooms, loading, error, refresh, page, setPage, search, setSearch, pageCount } = useRooms();
    const { showModal, setShowModal, editing, form, setForm, saving, openAdd, openEdit, handleSubmit, handleDelete } = useRoomCrud(refresh);

    return (
        <>
            <Navbar
                title="Rooms"
                className="page-rooms"
                search={search}
                onSearchChange={setSearch}
                actions={<Button variant="primary" onClick={openAdd}>+ Add Room</Button>}
            />
            <DataTable
                loading={loading} error={error} data={rooms}
                emptyMessage="No rooms found. Add one to get started."
                getKey={(room) => room.room_id}
                columns={[
                    { header: "Name",     render: (room) => room.name },
                    { header: "Capacity", render: (room) => room.capacity ?? "--" },
                ]}
                onEdit={openEdit} onDelete={handleDelete}
                page={page} pageCount={pageCount} onPageChange={setPage}
            />
            {showModal && (
                <Modal title={editing ? "Edit Room" : "Add Room"} onClose={() => setShowModal(false)} onSubmit={handleSubmit} submitLabel={editing ? "Update" : "Create"} saving={saving}>
                    <TextField   label="Room Name" value={form.name}     onChange={(v) => setForm({ ...form, name: v })}     required />
                    <NumberField label="Capacity"   value={form.capacity} onChange={(v) => setForm({ ...form, capacity: v })} min={1} />
                </Modal>
            )}
        </>
    );
}
