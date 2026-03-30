"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import DataState from "@/components/ui/data_state";
import Navbar from "@/components/ui/navbar";
import AddInstrumentModal from "@/features/rooms/components/add_instrument_modal";
import BlockedTimeModal from "@/features/rooms/components/blocked_time_modal";
import MoveInstrumentModal from "@/features/rooms/components/move_instrument_modal";
import RoomDetailTabs from "@/features/rooms/components/room_detail_tabs";
import RoomInfoCard from "@/features/rooms/components/room_info_card";
import { useRoomDetail } from "@/features/rooms/hooks/use_room_detail";

export default function RoomDetailPage() {
    const { roomId } = useParams() as { roomId: string };
    const {
        room,
        upcomingSessions,
        blockedTimes,
        loading,
        error,
        showBlockedTimeModal,
        setShowBlockedTimeModal,
        blockedTimeForm,
        setBlockedTimeForm,
        savingBlockedTime,
        openBlockedTimeModal,
        handleBlockedTimeSubmit,
        handleBlockedTimeDelete,
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
    } = useRoomDetail(roomId);
    const [activeSection, setActiveSection] = useState("sessions");

    const moveInstrument = moveInstrumentIndex !== null ? instruments[moveInstrumentIndex] : null;

    return (
        <>
            <Navbar
                className="page-room-detail"
                title={room?.name ?? ""}
                back={{ label: "Rooms", href: "/rooms" }}
            />
            <DataState loading={loading} error={error} empty={!room} emptyMessage="Room not found.">
                {room && (
                    <>
                        <RoomInfoCard room={room} />
                        <RoomDetailTabs
                            active={activeSection}
                            onChange={setActiveSection}
                            sessions={upcomingSessions}
                            blockedTimes={blockedTimes}
                            onAddBlockedTime={openBlockedTimeModal}
                            onDeleteBlockedTime={handleBlockedTimeDelete}
                            instruments={instruments}
                            onAddInstrument={openAddInstrumentModal}
                            onMoveInstrument={openMoveInstrumentModal}
                            onDeleteInstrument={handleDeleteInstrument}
                        />
                    </>
                )}
            </DataState>
            {showBlockedTimeModal && (
                <BlockedTimeModal
                    form={blockedTimeForm}
                    saving={savingBlockedTime}
                    onChange={setBlockedTimeForm}
                    onClose={() => setShowBlockedTimeModal(false)}
                    onSubmit={handleBlockedTimeSubmit}
                />
            )}
            {showAddInstrumentModal && (
                <AddInstrumentModal
                    saving={savingInstrument}
                    onClose={() => setShowAddInstrumentModal(false)}
                    onSubmit={handleAddInstrument}
                />
            )}
            {showMoveInstrumentModal && moveInstrument && (
                <MoveInstrumentModal
                    instrument={moveInstrument}
                    roomOptions={otherRoomOptions}
                    saving={savingInstrument}
                    onClose={() => setShowMoveInstrumentModal(false)}
                    onSubmit={handleMoveInstrument}
                />
            )}
        </>
    );
}
