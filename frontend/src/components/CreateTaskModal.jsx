import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const CreateTaskModal = ({ isOpen, onClose, onTaskCreated }) => {
    const { user } = useAuth();
    const [formData, setFormData] = useState({
        company_name: '',
        document_type: '',
        task_type: 'Tier I',
        priority: 'Medium',
        target_qty: 1,
        achieved_qty: 0,
        assigned_user_id: '',
        description: '',
        workflow_config_id: '',
        custom_workflow_name: ''
    });
    const [users, setUsers] = useState([]);
    const [workflows, setWorkflows] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            fetchUsers();
            fetchWorkflows();
            setFormData(prev => ({ ...prev, assigned_user_id: '' })); // Reset assignee
        }
    }, [isOpen]);

    const fetchUsers = async () => {
        try {
            const response = await api.get('/users');
            setUsers(response.data);
        } catch (error) {
            console.error("Failed to fetch users", error);
        }
    };

    const fetchWorkflows = async () => {
        try {
            const response = await api.get('/workflows/');
            setWorkflows(response.data.filter(w => w.is_active));
        } catch (error) {
            console.error("Failed to fetch workflows", error);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const payload = {
                ...formData,
                target_qty: parseInt(formData.target_qty),
                achieved_qty: parseInt(formData.achieved_qty),
                assigned_user_id: formData.assigned_user_id || null, // Handle unassigned
                workflow_config_id: formData.workflow_config_id === 'other' ? null : (formData.workflow_config_id || null),
                custom_workflow_name: formData.workflow_config_id === 'other' ? formData.custom_workflow_name : null
            };

            await api.post('/tasks/', payload);
            onTaskCreated();
            onClose();
            // Reset form
            setFormData({
                company_name: '',
                document_type: '',
                task_type: 'Tier I',
                priority: 'Medium',
                target_qty: 1,
                achieved_qty: 0,
                assigned_user_id: '',
                description: '',
                workflow_config_id: '',
                custom_workflow_name: ''
            });
        } catch (error) {
            console.error("Failed to create task", error);
            alert("Failed to create task. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl overflow-hidden max-h-[90vh] overflow-y-auto">
                <div className="flex items-center justify-between p-6 border-b border-slate-100 sticky top-0 bg-white z-10">
                    <h2 className="text-xl font-bold text-slate-900">Create New Task</h2>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
                        <X size={24} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Company Name</label>
                            <input
                                type="text"
                                name="company_name"
                                value={formData.company_name}
                                onChange={handleChange}
                                required
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Document Type</label>
                            <input
                                type="text"
                                name="document_type"
                                value={formData.document_type}
                                onChange={handleChange}
                                required
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Task Type</label>
                            <select
                                name="task_type"
                                value={formData.task_type}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all bg-white"
                            >
                                <option value="Tier I">Tier I</option>
                                <option value="Tier II">Tier II</option>
                                <option value="Audit">Audit</option>
                                <option value="Data Entry">Data Entry</option>
                                <option value="Review">Review</option>
                                <option value="Strategy">Strategy</option>
                                <option value="Analysis">Analysis</option>
                            </select>
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Priority</label>
                            <select
                                name="priority"
                                value={formData.priority}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all bg-white"
                            >
                                <option value="Low">Low</option>
                                <option value="Medium">Medium</option>
                                <option value="High">High</option>
                                <option value="Critical">Critical</option>
                            </select>
                        </div>

                        {/* Workflow Selection */}
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Workflow</label>
                            <select
                                name="workflow_config_id"
                                value={formData.workflow_config_id}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all bg-white"
                            >
                                <option value="">Select Workflow...</option>
                                {workflows.map(wf => (
                                    <option key={wf.config_id} value={wf.config_id}>{wf.workflow_name}</option>
                                ))}
                                <option value="other">Other (Custom)</option>
                            </select>
                        </div>

                        {formData.workflow_config_id === 'other' && (
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-slate-700">Custom Workflow Name</label>
                                <input
                                    type="text"
                                    name="custom_workflow_name"
                                    value={formData.custom_workflow_name}
                                    onChange={handleChange}
                                    required
                                    placeholder="Enter workflow name"
                                    className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                                />
                            </div>
                        )}

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Target Qty</label>
                            <input
                                type="number"
                                name="target_qty"
                                min="1"
                                value={formData.target_qty}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Achieved Qty</label>
                            <input
                                type="number"
                                name="achieved_qty"
                                min="0"
                                value={formData.achieved_qty}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                            />
                        </div>

                        <div className="space-y-2">
                            <label className="text-sm font-medium text-slate-700">Assignee</label>
                            <select
                                name="assigned_user_id"
                                value={formData.assigned_user_id}
                                onChange={handleChange}
                                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all bg-white"
                            >
                                <option value="">Unassigned</option>
                                {users.map(u => (
                                    <option key={u.id} value={u.id}>{u.full_name} ({u.username})</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-700">Description</label>
                        <textarea
                            name="description"
                            value={formData.description}
                            onChange={handleChange}
                            rows="3"
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all resize-none"
                        ></textarea>
                    </div>

                    <div className="flex justify-end gap-3 pt-4 border-t border-slate-100">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-slate-600 font-medium hover:bg-slate-50 rounded-lg transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-lg transition-colors font-medium shadow-lg shadow-primary-600/20 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            {loading ? 'Creating...' : 'Create Task'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateTaskModal;
