'use client';

import React, { useState, useMemo } from 'react';

export type Student = {
  id: string;
  name: string;
  email: string;
  dob: string;
  skills: string;
};

const initialStudents: Student[] = [
  { id: '1', name: 'Alice Smith', email: 'alice@example.com', dob: '2000-05-15', skills: 'Piano, Vocals' },
  { id: '2', name: 'Bob Johnson', email: 'bob@example.com', dob: '1998-11-22', skills: 'Guitar' },
];

export default function StudentPage() {
  const [students, setStudents] = useState<Student[]>(initialStudents);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
  const [currentStudent, setCurrentStudent] = useState<Student | null>(null);
  
  // Delete Confirmation state
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [studentToDelete, setStudentToDelete] = useState<Student | null>(null);

  // Form states
  const [formData, setFormData] = useState({ name: '', email: '', dob: '', skills: '' });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Memoized filtered students
  const filteredStudents = useMemo(() => {
    return students.filter(student => 
      student.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      student.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      student.skills.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [students, searchQuery]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.name.trim()) newErrors.name = 'Name is required';
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/^\S+@\S+\.\S+$/.test(formData.email)) {
      newErrors.email = 'Email format is invalid';
    }
    if (!formData.dob) newErrors.dob = 'Date of Birth is required';
    if (!formData.skills.trim()) newErrors.skills = 'Skills are required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleOpenModal = (mode: 'add' | 'edit', student?: Student) => {
    setModalMode(mode);
    if (mode === 'edit' && student) {
      setCurrentStudent(student);
      setFormData({
        name: student.name,
        email: student.email,
        dob: student.dob,
        skills: student.skills
      });
    } else {
      setCurrentStudent(null);
      setFormData({ name: '', email: '', dob: '', skills: '' });
    }
    setErrors({});
    setIsModalOpen(true);
  };

  const handleSave = () => {
    if (!validateForm()) return;

    if (modalMode === 'add') {
      const newStudent: Student = {
        id: Date.now().toString(),
        ...formData
      };
      setStudents([...students, newStudent]);
    } else if (modalMode === 'edit' && currentStudent) {
      setStudents(students.map(s => s.id === currentStudent.id ? { ...currentStudent, ...formData } : s));
    }
    setIsModalOpen(false);
  };

  const confirmDelete = (student: Student) => {
    setStudentToDelete(student);
    setIsDeleteOpen(true);
  };

  const handleDelete = () => {
    if (studentToDelete) {
      setStudents(students.filter(s => s.id !== studentToDelete.id));
      setIsDeleteOpen(false);
      setStudentToDelete(null);
    }
  };

  return (
    <div className="w-full p-6 text-white min-h-screen">
      <div className="mb-6 flex justify-between items-center bg-zinc-900 p-4 rounded-lg shadow-lg border border-purple-500/30">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">Students</h1>
        
        <div className="flex gap-4 items-center">
          <div className="relative">
            <input 
              type="text" 
              placeholder="Search students..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bg-zinc-800 text-white placeholder-gray-400 px-4 py-2 rounded-md outline-none border border-zinc-700 focus:border-purple-500 transition-colors"
            />
          </div>
          
          <button 
            onClick={() => handleOpenModal('add')}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md transition font-medium"
          >
            + Add Student
          </button>
        </div>
      </div>

      <div className="w-full bg-zinc-900 rounded-lg overflow-hidden border border-purple-500/50 shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse text-left">
            <thead>
              <tr className="bg-zinc-950 text-gray-300 text-sm border-b border-purple-500/30">
                <th className="p-4 font-semibold">Name</th>
                <th className="p-4 font-semibold">Email</th>
                <th className="p-4 font-semibold">DOB</th>
                <th className="p-4 font-semibold">Skills</th>
                <th className="p-4 font-semibold text-center w-32">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredStudents.length > 0 ? (
                filteredStudents.map((student) => (
                  <tr key={student.id} className="border-b border-zinc-800 hover:bg-zinc-800/50 transition-colors">
                    <td className="p-4">{student.name}</td>
                    <td className="p-4 text-gray-400">{student.email}</td>
                    <td className="p-4">{student.dob}</td>
                    <td className="p-4">
                      <span className="bg-purple-900/40 text-purple-300 px-2 py-1 rounded-md text-sm border border-purple-700/50">
                        {student.skills}
                      </span>
                    </td>
                    <td className="p-4">
                      <div className="flex justify-center gap-3">
                        <button 
                          onClick={() => handleOpenModal('edit', student)}
                          className="text-blue-400 hover:text-blue-300 transition"
                        >
                          Edit
                        </button>
                        <button 
                          onClick={() => confirmDelete(student)}
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
                  <td colSpan={5} className="p-8 text-center text-gray-500">
                    No students found matching your criteria.
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
              <h2 className="text-xl font-semibold">{modalMode === 'add' ? 'Add New Student' : 'Edit Student'}</h2>
            </div>
            
            <div className="p-6 flex flex-col gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Full Name</label>
                <input 
                  type="text" 
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className={`w-full bg-zinc-800 text-white px-3 py-2 rounded-md outline-none border ${errors.name ? 'border-red-500' : 'border-zinc-700 focus:border-purple-500'} transition-colors`}
                  placeholder="John Doe"
                />
                {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Email Address</label>
                <input 
                  type="email" 
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className={`w-full bg-zinc-800 text-white px-3 py-2 rounded-md outline-none border ${errors.email ? 'border-red-500' : 'border-zinc-700 focus:border-purple-500'} transition-colors`}
                  placeholder="john@example.com"
                />
                {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
              </div>
              
              <div>
                <label className="block text-sm text-gray-400 mb-1">Date of Birth</label>
                <input 
                  type="date" 
                  value={formData.dob}
                  onChange={(e) => setFormData({...formData, dob: e.target.value})}
                  className={`w-full bg-zinc-800 text-white px-3 py-2 rounded-md outline-none border ${errors.dob ? 'border-red-500' : 'border-zinc-700 focus:border-purple-500'} transition-[border-color]`}
                />
                {errors.dob && <p className="text-red-500 text-xs mt-1">{errors.dob}</p>}
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Skills (Comma separated)</label>
                <input 
                  type="text" 
                  value={formData.skills}
                  onChange={(e) => setFormData({...formData, skills: e.target.value})}
                  className={`w-full bg-zinc-800 text-white px-3 py-2 rounded-md outline-none border ${errors.skills ? 'border-red-500' : 'border-zinc-700 focus:border-purple-500'} transition-colors`}
                  placeholder="Piano, Guitar, Vocals..."
                />
                {errors.skills && <p className="text-red-500 text-xs mt-1">{errors.skills}</p>}
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
              <h2 className="text-xl font-bold mb-2">Delete Student?</h2>
              <p className="text-gray-400 mb-6">
                Are you sure you want to delete <span className="text-white font-medium">{studentToDelete?.name}</span>? This action cannot be undone.
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