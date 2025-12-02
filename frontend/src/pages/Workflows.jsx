import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { Plus, Settings, Activity, Clock, Target, User, BarChart2, Users, List } from 'lucide-react';
import clsx from 'clsx';
import { useAuth } from '../context/AuthContext';
import AssignPOCModal from '../components/AssignPOCModal';
import WorkflowVolumeModal from '../components/WorkflowVolumeModal';
import WorkflowTasksModal from '../components/WorkflowTasksModal';

const Workflows = () => {
    const { user } = useAuth();
    const [workflows, setWorkflows] = useState([]);
    const [volumes, setVolumes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    // Modals
    const [assignPOCModalOpen, setAssignPOCModalOpen] = useState(false);
    const [volumeModalOpen, setVolumeModalOpen] = useState(false);
    const [tasksModalOpen, setTasksModalOpen] = useState(false);
    const [selectedWorkflow, setSelectedWorkflow] = useState(null);

    const isAdminOrManager = user?.role === 'admin' || user?.role === 'manager';

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        setLoading(true);
        try {
            const [workflowsRes, volumesRes] = await Promise.all([
                api.get('/workflows/'),
                api.get('/workflows/volume?limit=20')
            ]);
            setWorkflows(Array.isArray(workflowsRes.data) ? workflowsRes.data : []);
            setVolumes(Array.isArray(volumesRes.data) ? volumesRes.data : []);

            if (!Array.isArray(workflowsRes.data)) console.error("API Error: /workflows did not return an array", workflowsRes.data);
            if (!Array.isArray(volumesRes.data)) console.error("API Error: /workflows/volume did not return an array", volumesRes.data);
        } catch (err) {
            setError("Failed to load data.");
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleAssignPOC = (workflow) => {
        setSelectedWorkflow(workflow);
        setAssignPOCModalOpen(true);
    };

    const handleRecordVolume = (workflow) => {
        setSelectedWorkflow(workflow);
        setVolumeModalOpen(true);
    };

    const handleViewTasks = (workflow) => {
        setSelectedWorkflow(workflow);
        setTasksModalOpen(true);
    };

    if (loading) return <div className="p-8 text-center text-slate-500">Loading workflows...</div>;
    if (error) return <div className="p-8 text-center text-red-500">{error}</div>;

    return (
        <div className="max-w-6xl mx-auto space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Workflows</h1>
                    <p className="text-slate-500 mt-1">Manage workflow configurations, POCs, and daily volumes.</p>
                </div>
                {isAdminOrManager && (
                    <Link to="/workflows/new" className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors font-medium shadow-lg shadow-primary-600/20">
                        <Plus size={18} />
                        New Workflow
                    </Link>
                )}
            </div>

            {/* Workflows Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {workflows.map((workflow) => (
                    <div key={workflow.config_id} className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition-shadow p-6 space-y-4 flex flex-col">
                        <div className="flex items-start justify-between">
                            <div>
                                <h3 className="font-semibold text-lg text-slate-900">{workflow.workflow_name}</h3>
                                <span className={clsx(
                                    "inline-flex items-center px-2 py-0.5 rounded text-xs font-medium mt-1",
                                    workflow.is_active ? "bg-emerald-50 text-emerald-700" : "bg-slate-100 text-slate-600"
                                )}>
                                    {workflow.is_active ? "Active" : "Inactive"}
                                </span>
                            </div>
                            <div className="flex gap-2">
                                <button
                                    onClick={() => handleViewTasks(workflow)}
                                    className="p-2 bg-slate-50 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors"
                                    title="View Tasks"
                                >
                                    <List size={20} />
                                </button>
                                <button
                                    onClick={() => handleRecordVolume(workflow)}
                                    className="p-2 bg-slate-50 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors"
                                    title="Record Daily Volume"
                                >
                                    <BarChart2 size={20} />
                                </button>
                                {isAdminOrManager && (
                                    <button
                                        onClick={() => handleAssignPOC(workflow)}
                                        className="p-2 bg-slate-50 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors"
                                        title="Assign POCs"
                                    >
                                        <Users size={20} />
                                    </button>
                                )}
                            </div>
                        </div>

                        <div className="space-y-3 pt-2 flex-grow">
                            <div className="flex items-center gap-3 text-sm text-slate-600">
                                <Activity size={16} className="text-slate-400" />
                                <span>Type: <span className="font-medium text-slate-900">{workflow.workflow_type}</span></span>
                            </div>

                            {/* POC Display */}
                            <div className="pt-2 border-t border-slate-50 space-y-2">
                                <div className="flex items-center gap-2 text-sm">
                                    <User size={14} className="text-primary-500" />
                                    <span className="text-slate-500">Primary:</span>
                                    <span className="font-medium text-slate-900">
                                        {workflow.primary_poc ? workflow.primary_poc.full_name : <span className="text-slate-400 italic">Unassigned</span>}
                                    </span>
                                </div>
                                <div className="flex items-center gap-2 text-sm">
                                    <User size={14} className="text-slate-400" />
                                    <span className="text-slate-500">Secondary:</span>
                                    <span className="font-medium text-slate-900">
                                        {workflow.secondary_poc ? workflow.secondary_poc.full_name : <span className="text-slate-400 italic">Unassigned</span>}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="pt-4 border-t border-slate-100 flex justify-end">
                            <Link to={`/workflows/${workflow.config_id}`} className="text-sm font-medium text-primary-600 hover:text-primary-700">
                                Edit Configuration &rarr;
                            </Link>
                        </div>
                    </div>
                ))}
            </div>

            {/* Recent Volume Log */}
            <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-6 border-b border-slate-100">
                    <h2 className="text-lg font-bold text-slate-900">Recent Daily Volumes</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-slate-50 text-slate-600 font-medium border-b border-slate-200">
                            <tr>
                                <th className="px-6 py-3">Date</th>
                                <th className="px-6 py-3">Workflow Type</th>
                                <th className="px-6 py-3">Quantity</th>
                                <th className="px-6 py-3">Analyst</th>
                                <th className="px-6 py-3">Recorded At</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {volumes.map((vol) => (
                                <tr key={vol.volume_id} className="hover:bg-slate-50 transition-colors">
                                    <td className="px-6 py-4 font-medium text-slate-900">{vol.date}</td>
                                    <td className="px-6 py-4 text-slate-600">{vol.workflow_type}</td>
                                    <td className="px-6 py-4 font-bold text-slate-900">{vol.quantity}</td>
                                    <td className="px-6 py-4 text-slate-600">
                                        {vol.analyst ? vol.analyst.full_name : 'Unknown'}
                                    </td>
                                    <td className="px-6 py-4 text-slate-400 text-xs">
                                        {new Date(vol.recorded_at).toLocaleString()}
                                    </td>
                                </tr>
                            ))}
                            {volumes.length === 0 && (
                                <tr>
                                    <td colSpan="5" className="px-6 py-8 text-center text-slate-500">
                                        No volume data recorded yet.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Modals */}
            <AssignPOCModal
                isOpen={assignPOCModalOpen}
                onClose={() => setAssignPOCModalOpen(false)}
                workflow={selectedWorkflow}
                onUpdate={fetchData}
            />
            <WorkflowVolumeModal
                isOpen={volumeModalOpen}
                onClose={() => setVolumeModalOpen(false)}
                workflow={selectedWorkflow}
                onUpdate={fetchData}
            />
            <WorkflowTasksModal
                isOpen={tasksModalOpen}
                onClose={() => setTasksModalOpen(false)}
                workflow={selectedWorkflow}
            />
        </div>
    );
};

export default Workflows;
