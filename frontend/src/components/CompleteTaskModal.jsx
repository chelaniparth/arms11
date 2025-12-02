import React, { useState } from 'react';
import api from '../services/api';
import { X, CheckCircle } from 'lucide-react';

const CompleteTaskModal = ({ isOpen, onClose, task, onTaskCompleted }) => {
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        achieved_qty: '',
        remarks: ''
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.post(`/tasks/${task.task_id}/complete`, {
                achieved_qty: parseInt(formData.achieved_qty),
                remarks: formData.remarks
            });
            onTaskCompleted();
            onClose();
        } catch (error) {
            console.error("Failed to complete task", error);
            alert("Failed to complete task");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen || !task) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
                <div className="flex items-center justify-between p-6 border-b border-slate-100">
                    <h2 className="text-xl font-bold text-slate-900">Complete Task</h2>
                    <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full text-slate-500 transition-colors">
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div className="bg-slate-50 p-4 rounded-lg mb-4">
                        <div className="text-sm text-slate-500">Task</div>
                        <div className="font-medium text-slate-900">{task.company_name}</div>
                        <div className="text-sm text-slate-500 mt-2">Target Quantity</div>
                        <div className="font-medium text-slate-900">{task.target_qty}</div>
                    </div>

                    {/* Achieved Qty */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Achieved Quantity</label>
                        <input
                            type="number"
                            name="achieved_qty"
                            required
                            min="0"
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all"
                            value={formData.achieved_qty}
                            onChange={handleChange}
                        />
                    </div>

                    {/* Remarks */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Remarks</label>
                        <textarea
                            name="remarks"
                            rows="3"
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all"
                            value={formData.remarks}
                            onChange={handleChange}
                            placeholder="Add any comments about the completion..."
                        ></textarea>
                    </div>

                    <div className="flex justify-end pt-4 border-t border-slate-100 mt-6">
                        <button
                            type="button"
                            onClick={onClose}
                            className="mr-3 px-4 py-2 text-sm font-medium text-slate-700 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-emerald-600 rounded-lg hover:bg-emerald-700 disabled:opacity-50 transition-colors shadow-lg shadow-emerald-600/20"
                        >
                            <CheckCircle className="w-4 h-4 mr-2" />
                            {loading ? 'Completing...' : 'Complete Task'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CompleteTaskModal;
