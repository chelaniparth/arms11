import React, { useState, useEffect } from 'react';
import { X, Calendar, BarChart2 } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const WorkflowVolumeModal = ({ isOpen, onClose, workflow, onUpdate }) => {
    const { user } = useAuth();
    const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
    const [quantity, setQuantity] = useState('');
    const [analystId, setAnalystId] = useState('');
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);

    const isAdminOrManager = user?.role === 'admin' || user?.role === 'manager';

    useEffect(() => {
        if (isOpen) {
            if (isAdminOrManager) {
                fetchUsers();
            }
            setAnalystId(user?.id || '');
            setQuantity('');
            setDate(new Date().toISOString().split('T')[0]);
        }
    }, [isOpen, user, isAdminOrManager]);

    const fetchUsers = async () => {
        try {
            const response = await api.get('/users');
            setUsers(response.data);
        } catch (error) {
            console.error("Failed to fetch users", error);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            await api.post('/workflows/volume', {
                workflow_type: workflow.workflow_type,
                date: date,
                quantity: parseInt(quantity),
                analyst_id: analystId || user.id
            });
            onUpdate();
            onClose();
        } catch (error) {
            console.error("Failed to record volume", error);
            alert("Failed to record volume");
        } finally {
            setSaving(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
                <div className="flex items-center justify-between p-4 border-b border-slate-100">
                    <h2 className="text-lg font-bold text-slate-900">Record Daily Volume</h2>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-4 space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Workflow</label>
                        <div className="p-2 bg-slate-50 rounded border border-slate-200 text-slate-700 font-medium">
                            {workflow?.workflow_name} ({workflow?.workflow_type})
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Date</label>
                        <input
                            type="date"
                            value={date}
                            onChange={(e) => setDate(e.target.value)}
                            className="w-full rounded-lg border-slate-200 focus:border-primary-500 focus:ring-primary-500"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Quantity</label>
                        <input
                            type="number"
                            min="0"
                            value={quantity}
                            onChange={(e) => setQuantity(e.target.value)}
                            className="w-full rounded-lg border-slate-200 focus:border-primary-500 focus:ring-primary-500"
                            placeholder="e.g. 140"
                            required
                        />
                    </div>

                    {isAdminOrManager && (
                        <div>
                            <label className="block text-sm font-medium text-slate-700 mb-1">Analyst</label>
                            <select
                                value={analystId}
                                onChange={(e) => setAnalystId(e.target.value)}
                                className="w-full rounded-lg border-slate-200 focus:border-primary-500 focus:ring-primary-500"
                            >
                                {users.map(u => (
                                    <option key={u.id} value={u.id}>{u.full_name} ({u.username})</option>
                                ))}
                            </select>
                            <p className="text-xs text-slate-500 mt-1">Assign this volume to a specific analyst.</p>
                        </div>
                    )}

                    <div className="flex justify-end gap-3 pt-2">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50 rounded-lg transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={saving}
                            className="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 rounded-lg transition-colors disabled:opacity-50"
                        >
                            {saving ? 'Saving...' : 'Record Volume'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default WorkflowVolumeModal;
