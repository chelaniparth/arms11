import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { X, Save } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const EditTaskModal = ({ isOpen, onClose, task, onTaskUpdated }) => {
    const { user } = useAuth();
    const [loading, setLoading] = useState(false);
    const [users, setUsers] = useState([]);
    const [formData, setFormData] = useState({
        company_name: '',
        target_qty: 1,
        achieved_qty: 0,
        status: '',
        assigned_user_id: ''
    });

    useEffect(() => {
        if (task) {
            setFormData({
                company_name: task.company_name || '',
                target_qty: task.target_qty || 1,
                achieved_qty: task.achieved_qty || 0,
                status: task.status || 'Pending',
                assigned_user_id: task.assigned_user_id || ''
            });
        }
    }, [task]);

    useEffect(() => {
        if (isOpen && user?.role === 'admin') {
            const fetchUsers = async () => {
                try {
                    const response = await api.get('/users/');
                    setUsers(response.data);
                } catch (error) {
                    console.error("Failed to fetch users", error);
                }
            };
            fetchUsers();
        }
    }, [isOpen, user]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const payload = { ...formData };
            // If empty string, set to null (unassigned)
            if (payload.assigned_user_id === '') {
                payload.assigned_user_id = null;
            }

            await api.put(`/tasks/${task.task_id}`, payload);
            onTaskUpdated();
            onClose();
        } catch (error) {
            console.error("Failed to update task", error);
            alert("Failed to update task");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen || !task) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
                <div className="flex items-center justify-between p-6 border-b border-slate-100">
                    <h2 className="text-xl font-bold text-slate-900">Edit Task</h2>
                    <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full text-slate-500 transition-colors">
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {/* Company Name */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Company Name</label>
                        <input
                            type="text"
                            name="company_name"
                            required
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all"
                            value={formData.company_name}
                            onChange={handleChange}
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-6">
                        {/* Target Qty */}
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Target Qty</label>
                            <input
                                type="number"
                                name="target_qty"
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all"
                                value={formData.target_qty}
                                onChange={handleChange}
                                min="1"
                            />
                        </div>

                        {/* Achieved Qty */}
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Achieved Qty</label>
                            <input
                                type="number"
                                name="achieved_qty"
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all"
                                value={formData.achieved_qty}
                                onChange={handleChange}
                                min="0"
                            />
                        </div>
                    </div>

                    {/* Status */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
                        <select
                            name="status"
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all"
                            value={formData.status}
                            onChange={handleChange}
                        >
                            <option value="Pending">Pending</option>
                            <option value="In Progress">In Progress</option>
                            <option value="Completed">Completed</option>
                            <option value="Under Review">Under Review</option>
                            <option value="Paused">Paused</option>
                        </select>
                    </div>

                    {/* Assignee (Admin Only) */}
                    {user?.role === 'admin' && (
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Assign To</label>
                            <select
                                name="assigned_user_id"
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all"
                                value={formData.assigned_user_id}
                                onChange={handleChange}
                            >
                                <option value="">Unassigned</option>
                                {users.map(u => (
                                    <option key={u.id} value={u.id}>{u.full_name} ({u.role})</option>
                                ))}
                            </select>
                        </div>
                    )}

                    <div className="flex justify-end pt-4 border-t border-slate-100">
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
                            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors shadow-lg shadow-primary-600/20"
                        >
                            <Save className="w-4 h-4 mr-2" />
                            {loading ? 'Saving...' : 'Save Changes'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default EditTaskModal;
