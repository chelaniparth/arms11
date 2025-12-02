import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { X, UserPlus } from 'lucide-react';

const AssignTaskModal = ({ isOpen, onClose, task, onTaskAssigned }) => {
    const [loading, setLoading] = useState(false);
    const [users, setUsers] = useState([]);
    const [selectedUserId, setSelectedUserId] = useState('');

    useEffect(() => {
        if (isOpen) {
            const fetchUsers = async () => {
                try {
                    const response = await api.get('/users/');
                    setUsers(response.data);
                } catch (error) {
                    console.error("Failed to fetch users", error);
                }
            };
            fetchUsers();
            if (task?.assigned_user_id) {
                setSelectedUserId(task.assigned_user_id);
            } else {
                setSelectedUserId('');
            }
        }
    }, [isOpen, task]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await api.put(`/tasks/${task.task_id}/assign`, {
                assigned_user_id: selectedUserId
            });
            onTaskAssigned();
            onClose();
        } catch (error) {
            console.error("Failed to assign task", error);
            alert("Failed to assign task");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen || !task) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
                <div className="flex items-center justify-between p-6 border-b border-slate-100">
                    <h2 className="text-xl font-bold text-slate-900">Assign Task</h2>
                    <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full text-slate-500 transition-colors">
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    <div className="bg-slate-50 p-4 rounded-lg mb-4">
                        <div className="text-sm text-slate-500">Task</div>
                        <div className="font-medium text-slate-900">{task.company_name}</div>
                    </div>

                    {/* User Selection */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Assign To</label>
                        <select
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all"
                            value={selectedUserId}
                            onChange={(e) => setSelectedUserId(e.target.value)}
                            required
                        >
                            <option value="">Select a team member</option>
                            {users.map(user => (
                                <option key={user.id} value={user.id}>{user.full_name} ({user.role})</option>
                            ))}
                        </select>
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
                            disabled={loading || !selectedUserId}
                            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors shadow-lg shadow-primary-600/20"
                        >
                            <UserPlus className="w-4 h-4 mr-2" />
                            {loading ? 'Assigning...' : 'Assign Task'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AssignTaskModal;
