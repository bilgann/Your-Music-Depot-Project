'use client';

import React, { useState, useMemo } from 'react';

export type Payment = {
  id: string;
  studentName: string;
  amount: number;
  date: string;
  method: 'Credit Card' | 'Cash' | 'Bank Transfer' | 'Other';
  status: 'Completed' | 'Pending' | 'Overdue' | 'Refunded';
};

const initialPayments: Payment[] = [
  { id: '1', studentName: 'Alice Smith', amount: 150.00, date: '2023-10-12', method: 'Credit Card', status: 'Completed' },
  { id: '2', studentName: 'Bob Johnson', amount: 75.50, date: '2023-10-25', method: 'Cash', status: 'Pending' },
  { id: '3', studentName: 'Charlie Davis', amount: 300.00, date: '2023-09-15', method: 'Bank Transfer', status: 'Overdue' },
];

export default function PaymentPage() {
  const [payments, setPayments] = useState<Payment[]>(initialPayments);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'add' | 'edit'>('add');
  const [currentPayment, setCurrentPayment] = useState<Payment | null>(null);
  
  // Delete states
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [paymentToDelete, setPaymentToDelete] = useState<Payment | null>(null);

  // Form states
  const [formData, setFormData] = useState({ 
    studentName: '', 
    amount: 0, 
    date: new Date().toISOString().split('T')[0], 
    method: 'Credit Card' as Payment['method'],
    status: 'Completed' as Payment['status']
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Search filtering
  const filteredPayments = useMemo(() => {
    return payments.filter(payment => 
      payment.studentName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      payment.method.toLowerCase().includes(searchQuery.toLowerCase()) ||
      payment.amount.toString().includes(searchQuery)
    );
  }, [payments, searchQuery]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};
    if (!formData.studentName.trim()) newErrors.studentName = 'Student name is required';
    if (formData.amount <= 0) newErrors.amount = 'Amount must be greater than 0';
    if (!formData.date) newErrors.date = 'Payment date is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleOpenModal = (mode: 'add' | 'edit', payment?: Payment) => {
    setModalMode(mode);
    if (mode === 'edit' && payment) {
      setCurrentPayment(payment);
      setFormData({
        studentName: payment.studentName,
        amount: payment.amount,
        date: payment.date,
        method: payment.method,
        status: payment.status
      });
    } else {
      setCurrentPayment(null);
      setFormData({ 
        studentName: '', 
        amount: 0, 
        date: new Date().toISOString().split('T')[0], 
        method: 'Credit Card', 
        status: 'Completed' 
      });
    }
    setErrors({});
    setIsModalOpen(true);
  };

  const handleSave = () => {
    if (!validateForm()) return;

    if (modalMode === 'add') {
      const newPayment: Payment = {
        id: Date.now().toString(),
        ...formData
      };
      setPayments([...payments, newPayment]);
    } else if (modalMode === 'edit' && currentPayment) {
      setPayments(payments.map(p => p.id === currentPayment.id ? { ...currentPayment, ...formData } : p));
    }
    setIsModalOpen(false);
  };

  const confirmDelete = (payment: Payment) => {
    setPaymentToDelete(payment);
    setIsDeleteOpen(true);
  };

  const handleDelete = () => {
    if (paymentToDelete) {
      setPayments(payments.filter(p => p.id !== paymentToDelete.id));
      setIsDeleteOpen(false);
      setPaymentToDelete(null);
    }
  };

  const getStatusBadge = (status: Payment['status']) => {
    switch (status) {
      case 'Completed':
        return <span className="bg-emerald-900/40 text-emerald-400 px-3 py-1 rounded-full text-xs font-semibold border border-emerald-700/50">Completed</span>;
      case 'Pending':
        return <span className="bg-amber-900/40 text-amber-400 px-3 py-1 rounded-full text-xs font-semibold border border-amber-700/50">Pending</span>;
      case 'Overdue':
        return <span className="bg-rose-900/40 text-rose-400 px-3 py-1 rounded-full text-xs font-semibold border border-rose-700/50">Overdue</span>;
      case 'Refunded':
        return <span className="bg-zinc-700 text-zinc-300 px-3 py-1 rounded-full text-xs font-semibold border border-zinc-600">Refunded</span>;
    }
  };

  // Calculate total metrics
  const totalRevenue = useMemo(() => {
    return payments
      .filter(p => p.status === 'Completed')
      .reduce((sum, payment) => sum + payment.amount, 0);
  }, [payments]);

  const pendingAmount = useMemo(() => {
    return payments
      .filter(p => p.status === 'Pending' || p.status === 'Overdue')
      .reduce((sum, payment) => sum + payment.amount, 0);
  }, [payments]);

  return (
    <div className="w-full p-6 text-white min-h-screen">
      <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-zinc-900 p-5 rounded-xl shadow-lg border border-purple-500/20 col-span-1 md:col-span-2 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-br from-green-400 to-emerald-600 bg-clip-text text-transparent">Payments</h1>
            <p className="text-gray-400 text-sm mt-1">Manage student invoices and payment history</p>
          </div>
          
          <div className="flex gap-3 w-full sm:w-auto">
            <input 
              type="text" 
              placeholder="Search student or amount..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full sm:w-56 bg-zinc-800 text-white placeholder-gray-400 px-4 py-2.5 rounded-lg outline-none border border-zinc-700 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 transition-all text-sm"
            />
            <button 
              onClick={() => handleOpenModal('add')}
              className="bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white px-5 py-2.5 rounded-lg transition-colors font-medium text-sm whitespace-nowrap shadow-lg shadow-emerald-600/20"
            >
              + New Payment
            </button>
          </div>
        </div>

        <div className="bg-zinc-900 p-5 rounded-xl shadow-lg border border-purple-500/20 col-span-1 grid grid-cols-2 gap-4">
          <div className="flex flex-col justify-center">
            <span className="text-gray-400 text-xs font-medium uppercase tracking-wider mb-1">Total Received</span>
            <span className="text-2xl font-bold text-emerald-400">${totalRevenue.toFixed(2)}</span>
          </div>
          <div className="flex flex-col justify-center border-l border-zinc-800 pl-4">
            <span className="text-gray-400 text-xs font-medium uppercase tracking-wider mb-1">Pending</span>
            <span className="text-2xl font-bold text-amber-400">${pendingAmount.toFixed(2)}</span>
          </div>
        </div>
      </div>

      <div className="bg-zinc-900 rounded-xl border border-zinc-800 shadow-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-zinc-950/50 text-gray-400 text-xs uppercase tracking-wider border-b border-zinc-800">
                <th className="px-6 py-4 font-medium">Student Info</th>
                <th className="px-6 py-4 font-medium">Amount</th>
                <th className="px-6 py-4 font-medium">Date</th>
                <th className="px-6 py-4 font-medium">Method</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/50">
              {filteredPayments.length > 0 ? (
                filteredPayments.map((payment) => (
                  <tr key={payment.id} className="hover:bg-zinc-800/30 transition-colors group">
                    <td className="px-6 py-4 font-medium text-gray-200">{payment.studentName}</td>
                    <td className="px-6 py-4 font-bold text-emerald-400">${payment.amount.toFixed(2)}</td>
                    <td className="px-6 py-4 text-gray-400 text-sm">{new Date(payment.date).toLocaleDateString()}</td>
                    <td className="px-6 py-4 text-gray-400 text-sm">{payment.method}</td>
                    <td className="px-6 py-4">{getStatusBadge(payment.status)}</td>
                    <td className="px-6 py-4">
                      <div className="flex justify-center gap-4 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button 
                          onClick={() => handleOpenModal('edit', payment)}
                          className="text-blue-400 hover:text-blue-300 font-medium text-sm transition-colors"
                        >
                          Edit
                        </button>
                        <button 
                          onClick={() => confirmDelete(payment)}
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
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <p className="text-gray-500 mb-2">No payments found matching "{searchQuery}"</p>
                    <button 
                      onClick={() => setSearchQuery('')} 
                      className="text-emerald-400 hover:text-emerald-300 text-sm"
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
                {modalMode === 'add' ? 'Record New Payment' : 'Edit Payment Details'}
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
                <label className="block text-sm font-medium text-gray-300 mb-1.5">Student Name</label>
                <input 
                  type="text" 
                  value={formData.studentName}
                  onChange={(e) => setFormData({...formData, studentName: e.target.value})}
                  className={`w-full bg-zinc-950 text-white px-4 py-2.5 rounded-lg outline-none border ${errors.studentName ? 'border-rose-500 focus:ring-rose-500/20' : 'border-zinc-800 focus:border-emerald-500 focus:ring-emerald-500/20'} focus:ring-2 transition-all`}
                  placeholder="e.g. Charlie Davis"
                />
                {errors.studentName && <p className="text-rose-400 text-xs mt-1.5">{errors.studentName}</p>}
              </div>
              
              <div className="grid grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Amount ($)</label>
                  <input 
                    type="number" 
                    step="0.01"
                    min="0"
                    value={formData.amount}
                    onChange={(e) => setFormData({...formData, amount: parseFloat(e.target.value) || 0})}
                    className={`w-full bg-zinc-950 text-white px-4 py-2.5 rounded-lg outline-none border ${errors.amount ? 'border-rose-500 focus:ring-rose-500/20' : 'border-zinc-800 focus:border-emerald-500 focus:ring-emerald-500/20'} focus:ring-2 transition-all`}
                  />
                  {errors.amount && <p className="text-rose-400 text-xs mt-1.5">{errors.amount}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Date</label>
                  <input 
                    type="date" 
                    value={formData.date}
                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                    className={`w-full bg-zinc-950 text-white px-4 py-2.5 rounded-lg outline-none border ${errors.date ? 'border-rose-500 focus:ring-rose-500/20' : 'border-zinc-800 focus:border-emerald-500 focus:ring-emerald-500/20'} focus:ring-2 transition-[border-color] appearance-none cursor-pointer`}
                  />
                  {errors.date && <p className="text-rose-400 text-xs mt-1.5">{errors.date}</p>}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-5">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Payment Method</label>
                  <select 
                    value={formData.method}
                    onChange={(e) => setFormData({...formData, method: e.target.value as Payment['method']})}
                    className="w-full bg-zinc-950 text-white px-4 py-2.5 rounded-lg outline-none border border-zinc-800 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all appearance-none cursor-pointer"
                  >
                    <option value="Credit Card">Credit Card</option>
                    <option value="Cash">Cash</option>
                    <option value="Bank Transfer">Bank Transfer</option>
                    <option value="Other">Other</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-1.5">Status</label>
                  <select 
                    value={formData.status}
                    onChange={(e) => setFormData({...formData, status: e.target.value as Payment['status']})}
                    className="w-full bg-zinc-950 text-white px-4 py-2.5 rounded-lg outline-none border border-zinc-800 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-500/20 transition-all appearance-none cursor-pointer"
                  >
                    <option value="Completed">Completed</option>
                    <option value="Pending">Pending</option>
                    <option value="Overdue">Overdue</option>
                    <option value="Refunded">Refunded</option>
                  </select>
                </div>
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
                className="bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 px-6 py-2.5 rounded-lg transition-colors font-medium text-white text-sm shadow-lg shadow-emerald-600/20"
              >
                {modalMode === 'add' ? 'Record Payment' : 'Save Changes'}
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
              <h2 className="text-xl font-bold text-white mb-2">Delete Payment Record?</h2>
              <p className="text-gray-400 text-sm mb-6 leading-relaxed">
                You are about to delete the payment record for <span className="text-white font-medium">"{paymentToDelete?.studentName}"</span>. This action cannot be undone.
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
                  Delete Record
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}