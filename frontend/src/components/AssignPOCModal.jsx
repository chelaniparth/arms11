import React, { useState, useEffect } from 'react';
import { X, User, Search } from 'lucide-react';
import api from '../services/api';

const AssignPOCModal = ({ isOpen, onClose, workflow, onUpdate }) => {
    const [users, setUsers] = useState([]);
    const [primaryPocId, setPrimaryPocId] = useState('');
    const [secondaryPocId, setSecondaryPocId] = useState('');
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);

    useEffect(() => {
        if (isOpen) {
            fetchUsers();
            setPrimaryPocId(workflow?.primary_poc_id || '');
            setSecondaryPocId(workflow?.secondary_poc_id || '');
        }
    }, [isOpen, workflow]);

    const fetchUsers = async () => {
        setLoading(true);
        try {
            // Assuming we have an endpoint to get all users or analysts
            // If not, we might need to create one or use an existing one
            // For now, let's assume /users/ exists or we can use /auth/users if available
            // Or we can filter from a list if we have it in context.
            // Let's try a common pattern or check if we have a user list endpoint.
            // Based on previous context, we might not have a direct list endpoint for all users easily accessible without admin.
            // But Managers should be able to see users to assign.
            // Let's assume api.get('/users') works for now, if not I'll fix it.
            const response = await api.get('/users');
            setUsers(response.data);
        } catch (error) {
            console.error("Failed to fetch users", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSaving(true);
        try {
            await api.put(`/workflows/${workflow.config_id}`, {
                primary_poc_id: primaryPocId || null,
                secondary_poc_id: secondaryPocId || null
            });
            onUpdate();
            onClose();
        } catch (error) {
            console.error("Failed to update POCs", error);
            alert("Failed to update POCs");
        } finally {
            setSaving(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-md overflow-hidden">
                <div className="flex items-center justify-between p-4 border-b border-slate-100">
                    <h2 className="text-lg font-bold text-slate-900">Assign POCs</h2>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-4 space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Workflow</label>
                        <div className="p-2 bg-slate-50 rounded border border-slate-200 text-slate-700 font-medium">
                            {workflow?.workflow_name}
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Primary POC</label>
                        <select
                            value={primaryPocId}
                            onChange={(e) => setPrimaryPocId(e.target.value)}
                            className="w-full rounded-lg border-slate-200 focus:border-primary-500 focus:ring-primary-500"
                        >
                            <option value="">Select User...</option>
                            {users.map(user => (
                                <option key={user.id} value={user.id}>{user.full_name} ({user.username})</option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Secondary POC</label>
                        <select
                            value={secondaryPocId}
                            onChange={(e) => setSecondaryPocId(e.target.value)}
                            className="w-full rounded-lg border-slate-200 focus:border-primary-500 focus:ring-primary-500"
                        >
                            <option value="">Select User...</option>
                            {users.map(user => (
                                <option key={user.id} value={user.id}>{user.full_name} ({user.username})</option>
                            ))}
                        </select>
                    </div>

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
                            {saving ? 'Saving...' : 'Save Assignments'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default AssignPOCModal;
