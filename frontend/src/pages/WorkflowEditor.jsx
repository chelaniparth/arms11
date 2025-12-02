import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../services/api';
import { ArrowLeft, Save, Trash2 } from 'lucide-react';

const WorkflowEditor = () => {
    const navigate = useNavigate();
    const { configId } = useParams();
    const isNew = !configId;

    const [formData, setFormData] = useState({
        workflow_name: '',
        workflow_type: 'Pending',
        target_metric: '',
        measurement_unit: '',
        monthly_target: '',
        priority: 'Medium',
        sla_hours: 72,
        quality_required: true,
        is_active: true
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!isNew) {
            fetchWorkflow();
        }
    }, [configId]);

    const fetchWorkflow = async () => {
        try {
            const response = await api.get('/workflows/');
            // Find the specific workflow from the list since we don't have a single get endpoint yet or use filter
            // Ideally we should have GET /workflows/{id}
            const workflow = response.data.find(w => w.config_id === parseInt(configId));
            if (workflow) {
                setFormData(workflow);
            } else {
                setError("Workflow not found");
            }
        } catch (err) {
            setError("Failed to load workflow details.");
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            if (isNew) {
                await api.post('/workflows/', formData);
            } else {
                await api.put(`/workflows/${configId}`, formData);
            }
            navigate('/workflows');
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to save workflow.");
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async () => {
        if (!window.confirm("Are you sure you want to delete this workflow?")) return;

        try {
            await api.delete(`/workflows/${configId}`);
            navigate('/workflows');
        } catch (err) {
            setError(err.response?.data?.detail || "Failed to delete workflow.");
        }
    };

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <div className="flex items-center gap-4">
                <button
                    onClick={() => navigate('/workflows')}
                    className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors"
                >
                    <ArrowLeft size={20} />
                </button>
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">{isNew ? 'Create Workflow' : 'Edit Workflow'}</h1>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8 space-y-6">
                {error && (
                    <div className="p-4 bg-red-50 text-red-700 rounded-xl text-sm">
                        {error}
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-700">Workflow Name</label>
                        <input
                            type="text"
                            name="workflow_name"
                            value={formData.workflow_name}
                            onChange={handleChange}
                            required
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                            placeholder="e.g., Monthly Audit"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-700">Type</label>
                        <select
                            name="workflow_type"
                            value={formData.workflow_type}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all bg-white"
                        >
                            <option value="Pending">Pending</option>
                            <option value="Credit Application">Credit Application</option>
                            <option value="Trade Reference">Trade Reference</option>
                            <option value="UCC">UCC</option>
                            <option value="Judgements">Judgements</option>
                            <option value="Liens">Liens</option>
                            <option value="Chapter11">Chapter 11</option>
                            <option value="Chapter7">Chapter 7</option>
                            <option value="Aging Tracker">Aging Tracker</option>
                            <option value="QSR">QSR</option>
                            <option value="Trade Tapes">Trade Tapes</option>
                            <option value="MLP">MLP</option>
                            <option value="PACA">PACA</option>
                            <option value="TNT">TNT</option>
                            <option value="CRA">CRA</option>
                            <option value="MSA">MSA</option>
                            <option value="Bond Watch">Bond Watch</option>
                            <option value="Track Ratings">Track Ratings</option>
                            <option value="Volume">Volume</option>
                            <option value="Target">Target</option>
                        </select>
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-700">Default Priority</label>
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

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-700">SLA (Hours)</label>
                        <input
                            type="number"
                            name="sla_hours"
                            value={formData.sla_hours}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-700">Target Metric Name</label>
                        <input
                            type="text"
                            name="target_metric"
                            value={formData.target_metric || ''}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                            placeholder="e.g., Completion Rate"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-700">Measurement Unit</label>
                        <input
                            type="text"
                            name="measurement_unit"
                            value={formData.measurement_unit || ''}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                            placeholder="e.g., Files"
                        />
                    </div>

                    <div className="space-y-2">
                        <label className="text-sm font-medium text-slate-700">Monthly Target</label>
                        <input
                            type="text"
                            name="monthly_target"
                            value={formData.monthly_target || ''}
                            onChange={handleChange}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                            placeholder="e.g., 100%"
                        />
                    </div>
                </div>

                <div className="flex items-center gap-6 pt-4 border-t border-slate-100">
                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            name="is_active"
                            checked={formData.is_active}
                            onChange={handleChange}
                            className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500 border-gray-300"
                        />
                        <span className="text-sm font-medium text-slate-700">Active Workflow</span>
                    </label>

                    <label className="flex items-center gap-2 cursor-pointer">
                        <input
                            type="checkbox"
                            name="quality_required"
                            checked={formData.quality_required}
                            onChange={handleChange}
                            className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500 border-gray-300"
                        />
                        <span className="text-sm font-medium text-slate-700">Quality Check Required</span>
                    </label>
                </div>

                <div className="flex items-center justify-between pt-6">
                    {!isNew && (
                        <button
                            type="button"
                            onClick={handleDelete}
                            className="flex items-center gap-2 text-red-600 hover:text-red-700 font-medium px-4 py-2 rounded-lg hover:bg-red-50 transition-colors"
                        >
                            <Trash2 size={18} />
                            Delete
                        </button>
                    )}
                    <div className="flex gap-3 ml-auto">
                        <button
                            type="button"
                            onClick={() => navigate('/workflows')}
                            className="px-4 py-2 text-slate-600 font-medium hover:bg-slate-50 rounded-lg transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-6 py-2 rounded-lg transition-colors font-medium shadow-lg shadow-primary-600/20 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Save size={18} />
                            {loading ? 'Saving...' : 'Save Workflow'}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
};

export default WorkflowEditor;
