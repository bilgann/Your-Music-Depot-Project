'use client';

import React, { useState, useEffect, useMemo } from 'react';

export type Instructor = {
  id: string;
  fullName: string;
  instrument: string;
  skillLevel: number;
  status: string;
  availability: string;
  payRate: number;
};

export default function InstructorPage() {
  const [instructors, setInstructors] = useState<Instructor[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
  const [currentInstructor, setCurrentInstructor] = useState<Instructor | null>(null);
  
  // Delete state
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [instructorToDelete, setInstructorToDelete] = useState<Instructor | null>(null);

  // Form states
  const [formData, setFormData] = useState({ 
    fullName: '', 
    instrument: '', 
    skillLevel: 1, 
    status: 'Active', 
    availability: '', 
    payRate: 0 
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    fetchInstructors();
  }, []);

  const fetchInstructors = async () => {
    try {
      const response = await fetch('/api/instructors');
      if (response.ok) {
        const data = await response.json();
        setInstructors(data);
      } else {
        console.error('Failed to fetch instructors');
        // Fallback for development if API is not yet ready
        setInstructors([
          { id: '1', fullName: 'David Gilmour', instrument: 'Guitar', skillLevel: 5, status: 'Active', availability: 'Weekdays', payRate: 60 }
        ]);
      }
    } catch (error) {
      console.error('Error fetching instructors:', error);
      setInstructors([
        { id: '1', fullName: 'David Gilmour', instrument: 'Guitar', skillLevel: 5, status: 'Active', availability: 'Weekdays', payRate: 60 }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const filteredInstructors = useMemo(() => {
    return instructors.filter(instructor => 
      instructor.fullName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      instructor.instrument.toLowerCase().includes(searchQuery.toLowerCase()) ||
      instructor.status.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [instructors, searchQuery]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.fullName.trim()) newErrors.fullName = 'Full Name is required';
    if (!formData.instrument.trim()) newErrors.instrument = 'Instrument is required';
    if (formData.skillLevel < 1 || formData.skillLevel > 5) newErrors.skillLevel = 'Skill level must be 1-5';
    if (!formData.availability.trim()) newErrors.availability = 'Availability is required';
    if (formData.payRate < 0) newErrors.payRate = 'Pay rate must be positive';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleOpenModal = (mode: 'add' | 'edit', instructor?: Instructor) => {
    setModalMode(mode);
    if (mode === 'edit' && instructor) {
      setCurrentInstructor(instructor);
      setFormData({
        fullName: instructor.fullName,
        instrument: instructor.instrument,
        skillLevel: instructor.skillLevel,
        status: instructor.status,
        availability: instructor.availability,
        payRate: instructor.payRate
      });
    } else {
      setCurrentInstructor(null);
      setFormData({ fullName: '', instrument: '', skillLevel: 1, status: 'Active', availability: '', payRate: 0 });
    }
    setErrors({});
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    if (!validateForm()) return;

    try {
      const isAdd = modalMode === 'add';
      const url = isAdd ? '/api/instructors' : `/api/instructors/${currentInstructor?.id}`;
      const method = isAdd ? 'POST' : 'PUT';

      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        await fetchInstructors(); // Refresh list
      } else {
        // Fallback for visual update during development if API is missing
        if (isAdd) {
          setInstructors([...instructors, { id: Date.now().toString(), ...formData }]);
        } else if (currentInstructor) {
          setInstructors(instructors.map(i => i.id === currentInstructor.id ? { ...currentInstructor, ...formData } : i));
        }
      }
    } catch (error) {
      console.error('Error saving instructor:', error);
      // Fallback
      if (modalMode === 'add') {
        setInstructors([...instructors, { id: Date.now().toString(), ...formData }]);
      } else if (currentInstructor) {
        setInstructors(instructors.map(i => i.id === currentInstructor.id ? { ...currentInstructor, ...formData } : i));
      }
    }

    setIsModalOpen(false);
  };

  const confirmDelete = (instructor: Instructor) => {
    setInstructorToDelete(instructor);
    setIsDeleteOpen(true);
  };

  const handleDelete = async () => {
    if (instructorToDelete) {
      try {
        const response = await fetch(`/api/instructors/${instructorToDelete.id}`, {
          method: 'DELETE'
        });
        
        if (response.ok) {
          await fetchInstructors();
        } else {
          // Fallback
          setInstructors(instructors.filter(i => i.id !== instructorToDelete.id));
        }
      } catch (error) {
        console.error('Error deleting instructor:', error);
        setInstructors(instructors.filter(i => i.id !== instructorToDelete.id));
      }
      
      setIsDeleteOpen(false);
      setInstructorToDelete(null);
    }
  };

  return (
    <div className="w-full p-6 text-white min-h-screen">
      <div className="mb-6 flex justify-between items-center bg-zinc-900 p-4 rounded-lg shadow-lg border border-purple-500/30">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">Instructors</h1>
        
        <div className="flex gap-4 items-center">
          <div className="relative">
            <input 
              type="text" 
              placeholder="Search instructors..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-zinc-800 text-white placeholder-gray-400 px-4 py-2 rounded-md outline-none border border-zinc-700 focus:border-purple-500 transition-colors"
            />
          </div>
          
          <button 
            onClick={() => handleOpenModal('add')}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition font-medium"
          >
            + Add Instructor
          </button>
        </div>
      </div>

      <div className="w-full bg-zinc-900 rounded-lg overflow-hidden border border-purple-500/50 shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="bg-zinc-950 text-gray-300 text-sm border-b border-purple-500/30">
                <th className="p-4 font-semibold">Full Name</th>
                <th className="p-4 font-semibold">Instrument</th>
                <th className="p-4 font-semibold">Skill Level</th>
                <th className="p-4 font-semibold">Status</th>
                <th className="p-4 font-semibold">Availability</th>
                <th className="p-4 font-semibold">Pay Rate</th>
                <th className="p-4 font-semibold text-center w-32">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                 <tr>
                    <td colSpan={7} className="p-8 text-center text-gray-500">Loading initial instructors...</td>
                 </tr>
              ) : filteredInstructors.length > 0 ? (
                filteredInstructors.map((instructor) => (
                  <tr key={instructor.id} className="border-b border-zinc-800 hover:bg-zinc-800/50 transition-colors">
                    <td className="p-4 text-white font-medium">{instructor.fullName}</td>
                    <td className="p-4">
                      <span className="bg-indigo-900/40 text-indigo-300 px-3 py-1 rounded-full text-xs font-semibold border border-indigo-700/50">
                        {instructor.instrument}
                      </span>
                    </td>
                    <td className="p-4 text-gray-300">{instructor.skillLevel}/5</td>
                    <td className="p-4">
                      {instructor.status.toLowerCase() === 'active' ? (
                        <span className="text-emerald-400 text-sm flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-emerald-500"></span>Active</span>
                      ) : (
                        <span className="text-rose-400 text-sm flex items-center gap-2"><span className="w-2 h-2 rounded-full bg-rose-500"></span>{instructor.status}</span>
                      )}
                    </td>
                    <td className="p-4 text-gray-400">{instructor.availability}</td>
                    <td className="p-4 text-purple-300">${instructor.payRate}/hr</td>
                    <td className="p-4">
                      <div className="flex justify-center gap-3">
                        <button 
                          onClick={() => handleOpenModal('edit', instructor)}
                          className="text-blue-400 hover:text-blue-300 transition"
                        >
                          Edit
                        </button>
                        <button 
                          onClick={() => confirmDelete(instructor)}
                          className="text-red-400 hover:text-red-300 transition"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-gray-500">
                    No instructors found matching your criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add/Edit Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-50 p-4">
          <div className="bg-zinc-900 border border-purple-500/40 rounded-xl shadow-2xl w-full max-w-md overflow-hidden">
            <div className="bg-zinc-950 p-4 border-b border-zinc-800">
              <h2 className="text-xl font-semibold">{modalMode === 'add' ? 'Add New Instructor' : 'Edit Instructor'}</h2>
            </div>
            
            <div className="p-6 flex flex-col gap-4 max-h-[70vh] overflow-y-auto">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Full Name</label>
                <input 
                  type="text" 
                  value={formData.fullName}
                  onChange={(e) => setFormData({...formData, fullName: e.target.value})}
                  className={`w-full bg-zinc-800 text-white px-3 py-2 rounded-md outline-none border ${errors.fullName ? 'border-red-500' : 'border-zinc-700 focus:border-purple-500'} transition-colors`}
                  placeholder="Jane Doe"
                />
                {errors.fullName && <p className="text-red-500 text-xs mt-1">{errors.fullName}</p>}
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Instrument</label>
                  <input 
                    type="text" 
                    value={formData.instrument}
                    onChange={(e) => setFormData({...formData, instrument: e.target.value})}
                    className={`w-full bg-zinc-800 text-white px-3 py-2 rounded-md outline-none border ${errors.instrument ? 'border-red-500' : 'border-zinc-700 focus:border-purple-500'} transition-colors`}
                    placeholder="Piano"
                  />
                  {errors.instrument && <p className="text-red-500 text-xs mt-1">{errors.instrument}</p>}
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Skill Level (1-5)</label>
                  <input 
                    type="number" 
                    min="1" max="5"
                    value={formData.skillLevel}
                    onChange={(e) => setFormData({...formData, skillLevel: parseInt(e.target.value) || 1})}
                    className={`w-full bg-zinc-800 text-white px-3 py-2 rounded-md outline-none border ${errors.skillLevel ? 'border-red-500' : 'border-zinc-700 focus:border-purple-500'}`}
                  />
                  {errors.skillLevel && <p className="text-red-500 text-xs mt-1">{errors.skillLevel}</p>}
                </div>
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Status</label>
                <select 
                  value={formData.status}
                  onChange={(e) => setFormData({...formData, status: e.target.value})}
                  className="w-full bg-zinc-800 text-white px-3 py-2 rounded-md outline-none border border-zinc-700 focus:border-purple-500 transition-colors"
                >
                  <option value="Active">Active</option>
                  <option value="Inactive">Inactive</option>
                  <option value="On Leave">On Leave</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Availability</label>
                <input 
                  type="text" 
                  value={formData.availability}
                  onChange={(e) => setFormData({...formData, availability: e.target.value})}
                  className={`w-full bg-zinc-800 text-white px-3 py-2 rounded-md outline-none border ${errors.availability ? 'border-red-500' : 'border-zinc-700 focus:border-purple-500'} transition-colors`}
                  placeholder="Weekdays, Weekends..."
                />
                {errors.availability && <p className="text-red-500 text-xs mt-1">{errors.availability}</p>}
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Pay Rate ($/hr)</label>
                <input 
                  type="number" 
                  min="0"
                  value={formData.payRate}
                  onChange={(e) => setFormData({...formData, payRate: parseFloat(e.target.value) || 0})}
                  className={`w-full bg-zinc-800 text-white px-3 py-2 rounded-md outline-none border ${errors.payRate ? 'border-red-500' : 'border-zinc-700 focus:border-purple-500'}`}
                />
                {errors.payRate && <p className="text-red-500 text-xs mt-1">{errors.payRate}</p>}
              </div>
            </div>
            
            <div className="bg-zinc-950 p-4 border-t border-zinc-800 flex justify-end gap-3">
              <button 
                onClick={() => setIsModalOpen(false)}
                className="px-4 py-2 text-gray-300 hover:text-white transition"
              >
                Cancel
              </button>
              <button 
                onClick={handleSave}
                className="bg-purple-600 hover:bg-purple-700 px-6 py-2 rounded-md transition font-medium text-white shadow-lg shadow-purple-600/20"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {isDeleteOpen && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex justify-center items-center z-50 p-4">
          <div className="bg-zinc-900 border border-red-500/40 rounded-xl shadow-2xl w-full max-w-sm overflow-hidden text-center">
            <div className="p-6">
              <div className="w-16 h-16 bg-red-500/20 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4 border border-red-500/50">
                <span className="text-2xl font-bold">!</span>
              </div>
              <h2 className="text-xl font-bold mb-2">Delete Instructor?</h2>
              <p className="text-gray-400 mb-6">
                Are you sure you want to delete <span className="text-white font-medium">{instructorToDelete?.fullName}</span>? This action cannot be undone.
              </p>
              
              <div className="flex gap-3 justify-center">
                <button 
                  onClick={() => setIsDeleteOpen(false)}
                  className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-md transition flex-1 font-medium"
                >
                  Cancel
                </button>
                <button 
                  onClick={handleDelete}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded-md transition flex-1 font-medium shadow-lg shadow-red-600/20"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}