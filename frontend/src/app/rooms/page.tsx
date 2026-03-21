'use client';

import React, { useState, useEffect, useMemo } from 'react';

export type Room = {
  id: string;
  name: string;
  capacity: number;
  equipment: string;
  status: 'Available' | 'Occupied' | 'Maintenance';
};

const initialRooms: Room[] = [
  { id: '1', name: 'Room 101 - Piano Room', capacity: 2, equipment: 'Yamaha Grand Piano', status: 'Available' },
  { id: '2', name: 'Room 102 - Drum Studio', capacity: 4, equipment: 'Pearl Drum Kit, PA System', status: 'Occupied' },
  { id: '3', name: 'Room 103 - Vocal Booth', capacity: 2, equipment: 'Microphones, Acoustic Treatment', status: 'Maintenance' },
];

export default function RoomPage() {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  useEffect(() => {
    fetchRooms();
  }, []);

  const fetchRooms = async () => {
    try {
      const resp = await fetch('/api/rooms');
      if (resp.ok) {
        setRooms(await resp.json());
      } else {
        setRooms(initialRooms);
      }
    } catch {
      setRooms(initialRooms);
    } finally {
      setLoading(false);
    }
  };
  
  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
  const [currentRoom, setCurrentRoom] = useState<Room | null>(null);
  
  // Delete states
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [roomToDelete, setRoomToDelete] = useState<Room | null>(null);

  // Form states
  const [formData, setFormData] = useState({ name: '', capacity: 1, equipment: '', status: 'Available' as Room['status'] });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Search filtering
  const filteredRooms = useMemo(() => {
    return rooms.filter(room => 
      room.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      room.equipment.toLowerCase().includes(searchQuery.toLowerCase()) ||
      room.status.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [rooms, searchQuery]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name.trim()) newErrors.name = 'Room name is required';
    if (formData.capacity < 1) newErrors.capacity = 'Capacity must be at least 1';
    if (!formData.equipment.trim()) newErrors.equipment = 'Equipment description is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleOpenModal = (mode: 'add' | 'edit', room?: Room) => {
    setModalMode(mode);
    if (mode === 'edit' && room) {
      setCurrentRoom(room);
      setFormData({
        name: room.name,
        capacity: room.capacity,
        equipment: room.equipment,
        status: room.status
      });
    } else {
      setCurrentRoom(null);
      setFormData({ name: '', capacity: 1, equipment: '', status: 'Available' });
    }
    setErrors({});
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    try {
      const isAdd = modalMode === 'add';
      const url = isAdd ? '/api/rooms' : `/api/rooms/${currentRoom?.id}`;
      const method = isAdd ? 'POST' : 'PUT';

      const resp = await fetch(url, {
        method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(formData)
      });
      
      if (resp.ok) {
        await fetchRooms();
      } else {
        // Fallback
        if (isAdd) {
          setRooms([...rooms, { id: Date.now().toString(), ...formData }]);
        } else if (currentRoom) {
          setRooms(rooms.map(r => r.id === currentRoom.id ? { ...currentRoom, ...formData } : r));
        }
      }
    } catch {
       if (modalMode === 'add') {
          setRooms([...rooms, { id: Date.now().toString(), ...formData }]);
        } else if (currentRoom) {
          setRooms(rooms.map(r => r.id === currentRoom.id ? { ...currentRoom, ...formData } : r));
        }
    }

    setIsModalOpen(false);
  };

  const confirmDelete = (room: Room) => {
    setRoomToDelete(room);
    setIsDeleteOpen(true);
  };

  const handleDelete = async () => {
    if (roomToDelete) {
      try {
        const resp = await fetch(`/api/rooms/${roomToDelete.id}`, { method: 'DELETE' });
        if (resp.ok) {
          await fetchRooms();
        } else {
          setRooms(rooms.filter(r => r.id !== roomToDelete.id)); // fallback
        }
      } catch {
        setRooms(rooms.filter(r => r.id !== roomToDelete.id)); // fallback
      }
      setIsDeleteOpen(false);
      setRoomToDelete(null);
    }
  };

  const getStatusBadge = (status: Room['status']) => {
    switch (status) {
      case 'Available':
        return <span className="bg-emerald-900/40 text-emerald-400 px-3 py-1 rounded-full text-xs font-semibold border border-emerald-700/50">Available</span>;
      case 'Occupied':
        return <span className="bg-amber-900/40 text-amber-400 px-3 py-1 rounded-full text-xs font-semibold border border-amber-700/50">Occupied</span>;
      case 'Maintenance':
        return <span className="bg-rose-900/40 text-rose-400 px-3 py-1 rounded-full text-xs font-semibold border border-rose-700/50">Maintenance</span>;
    }
  };

  return (
    <div className="w-full p-6 text-white min-h-screen">
      <div className="mb-8 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-zinc-900 p-5 rounded-xl shadow-lg border border-purple-500/20">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-br from-purple-400 to-indigo-500 bg-clip-text text-transparent">Rooms Management</h1>
          <p className="text-gray-400 text-sm mt-1">Manage practice rooms, equipment, and availability</p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto">
          <div className="relative w-full sm:w-64">
            <input 
              type="text" 
              placeholder="Search rooms or equipment..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-zinc-800 text-white placeholder-gray-400 px-4 py-2.5 rounded-lg outline-none border border-zinc-700 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all text-sm"
            />
          </div>
          
          <button 
            onClick={() => handleOpenModal('add')}
            className="bg-purple-600 hover:bg-purple-500 active:bg-purple-700 text-white px-5 py-2.5 rounded-lg transition-colors font-medium text-sm whitespace-nowrap shadow-lg shadow-purple-600/20"
          >
            + Add Room
          </button>
        </div>
      </div>

      <div className="bg-zinc-900 rounded-xl border border-zinc-800 shadow-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-zinc-950/50 text-gray-400 text-xs uppercase tracking-wider border-b border-zinc-800">
                <th className="px-6 py-4 font-medium">Room Name</th>
                <th className="px-6 py-4 font-medium">Capacity</th>
                <th className="px-6 py-4 font-medium">Equipment</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/50">
              {loading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-gray-500">Loading initial rooms...</td>
                </tr>
              ) : filteredRooms.length > 0 ? (
                filteredRooms.map((room) => (
                  <tr key={room.id} className="hover:bg-zinc-800/30 transition-colors group">
                    <td className="px-6 py-4 font-medium text-gray-200">{room.name}</td>
                    <td className="px-6 py-4 text-gray-400">{room.capacity} {room.capacity === 1 ? 'person' : 'people'}</td>
                    <td className="px-6 py-4 text-gray-400 max-w-xs truncate" title={room.equipment}>{room.equipment}</td>
                    <td className="px-6 py-4">{getStatusBadge(room.status)}</td>
                    <td className="px-6 py-4">
                      <div className="flex justify-center gap-4 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                          onClick={() => handleOpenModal('edit', room)}
                          className="text-indigo-400 hover:text-indigo-300 font-medium text-sm transition-colors"
                        >
                          Edit
                        </button>
                        <button 
                          onClick={() => confirmDelete(room)}
                          className="text-rose-400 hover:text-rose-300 font-medium text-sm transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center">
                    <p className="text-gray-500 mb-2">No rooms found matching "{searchQuery}"</p>
                    <button 
                      onClick={() => setSearchQuery('')} 
                      className="text-purple-400 hover:text-purple-300 text-sm"
                    >
                      Clear search
                    </button>
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add/Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex justify-center items-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-zinc-900 border border-zinc-700/50 rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col max-h-[90vh]">
            <div className="px-6 py-5 border-b border-zinc-800 flex justify-between items-center">
              <h2 className="text-xl font-bold text-white">
                {modalMode === 'add' ? 'Add Practice Room' : 'Edit Practice Room'}
              </h2>
              <button 
                onClick={() => setIsModalOpen(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                ✕
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto space-y-5">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1.5">Room Name</label>
                <input 
                  type="text" 
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className={`w-full bg-zinc-950 text-white px-4 py-2.5 rounded-lg outline-none border ${errors.name ? 'border-rose-500 focus:ring-rose-500/20' : 'border-zinc-800 focus:border-purple-500 focus:ring-purple-500/20'} focus:ring-2 transition-all`}
                  placeholder="e.g. Room 204 - Synth Lab"
                />
                {errors.name && <p className="text-rose-400 text-xs mt-1.5">{errors.name}</p>}
              </div>
              
              <div className="grid grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Capacity</label>
                  <input 
                    type="number" 
                    min="1"
                    value={formData.capacity}
                    onChange={(e) => setFormData({...formData, capacity: parseInt(e.target.value) || 0})}
                    className={`w-full bg-zinc-950 text-white px-4 py-2.5 rounded-lg outline-none border ${errors.capacity ? 'border-rose-500 focus:ring-rose-500/20' : 'border-zinc-800 focus:border-purple-500 focus:ring-purple-500/20'} focus:ring-2 transition-all`}
                  />
                  {errors.capacity && <p className="text-rose-400 text-xs mt-1.5">{errors.capacity}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Status</label>
                  <select 
                    value={formData.status}
                    onChange={(e) => setFormData({...formData, status: e.target.value as Room['status']})}
                    className="w-full bg-zinc-950 text-white px-4 py-2.5 rounded-lg outline-none border border-zinc-800 focus:border-purple-500 focus:ring-2 focus:ring-purple-500/20 transition-all appearance-none cursor-pointer"
                  >
                    <option value="Available">Available</option>
                    <option value="Occupied">Occupied</option>
                    <option value="Maintenance">Maintenance</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1.5">Equipment Provided</label>
                <textarea 
                  value={formData.equipment}
                  onChange={(e) => setFormData({...formData, equipment: e.target.value})}
                  rows={3}
                  className={`w-full bg-zinc-950 text-white px-4 py-2.5 rounded-lg outline-none border ${errors.equipment ? 'border-rose-500 focus:ring-rose-500/20' : 'border-zinc-800 focus:border-purple-500 focus:ring-purple-500/20'} focus:ring-2 transition-all resize-none`}
                  placeholder="List instruments, amps, stands, etc."
                />
                {errors.equipment && <p className="text-rose-400 text-xs mt-1.5">{errors.equipment}</p>}
              </div>
            </div>
            
            <div className="px-6 py-4 border-t border-zinc-800 bg-zinc-950/50 flex justify-end gap-3 rounded-b-2xl">
              <button 
                onClick={() => setIsModalOpen(false)}
                className="px-5 py-2.5 rounded-lg text-gray-300 hover:bg-zinc-800 transition-colors font-medium text-sm"
              >
                Cancel
              </button>
              <button 
                onClick={handleSave}
                className="bg-purple-600 hover:bg-purple-500 active:bg-purple-700 px-6 py-2.5 rounded-lg transition-colors font-medium text-white text-sm shadow-lg shadow-purple-600/20"
              >
                {modalMode === 'add' ? 'Create Room' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {isDeleteOpen && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex justify-center items-center z-50 p-4 animate-in fade-in duration-200">
          <div className="bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden text-center transform transition-all">
            <div className="p-8">
              <div className="w-16 h-16 bg-rose-500/10 text-rose-500 rounded-full flex items-center justify-center mx-auto mb-5 border border-rose-500/20">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-8 h-8">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-white mb-2">Delete Room?</h2>
              <p className="text-gray-400 text-sm mb-6 leading-relaxed">
                You are about to delete <span className="text-white font-medium">"{roomToDelete?.name}"</span>. This action permanently removes it from the records.
              </p>
              
              <div className="flex gap-3 justify-center w-full">
                <button 
                  onClick={() => setIsDeleteOpen(false)}
                  className="px-4 py-2.5 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors flex-1 font-medium text-sm"
                >
                  Cancel
                </button>
                <button 
                  onClick={handleDelete}
                  className="px-4 py-2.5 bg-rose-600 hover:bg-rose-500 active:bg-rose-700 text-white rounded-lg transition-colors flex-1 font-medium text-sm shadow-lg shadow-rose-600/20"
                >
                  Delete Room
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
