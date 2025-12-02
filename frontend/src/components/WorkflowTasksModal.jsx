import React, { useState, useEffect } from 'react';
import { X, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import api from '../services/api';

const WorkflowTasksModal = ({ isOpen, onClose, workflow }) => {
    const [tasks, setTasks] = useState([]);
    const [loading, setLoading] = useState(false);
    const [filter, setFilter] = useState('pending'); // 'pending' or 'completed'

    useEffect(() => {
        if (isOpen && workflow) {
            fetchTasks();
        }
    }, [isOpen, workflow]);

    const fetchTasks = async () => {
        setLoading(true);
        try {
            const response = await api.get(`/tasks/?workflow_config_id=${workflow.config_id}&limit=500`);
            setTasks(response.data);
        } catch (error) {
            console.error("Failed to fetch workflow tasks", error);
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen || !workflow) return null;

    // Filter tasks based on toggle
    const pendingTasks = tasks.filter(t => t.status !== 'Completed');
    const completedTasks = tasks.filter(t => t.status === 'Completed');

    const displayedTasks = filter === 'pending' ? pendingTasks : completedTasks;

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-4xl overflow-hidden max-h-[90vh] flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-slate-100 bg-white">
                    <div>
                        <h2 className="text-xl font-bold text-slate-900">{workflow.workflow_name} - Tasks</h2>
                        <p className="text-sm text-slate-500 mt-1">Manage tasks linked to this workflow</p>
                    </div>
                    <button onClick={onClose} className="text-slate-400 hover:text-slate-600 transition-colors">
                        <X size={24} />
                    </button>
                </div>

                {/* Toggle & Stats */}
                <div className="p-6 bg-slate-50 border-b border-slate-100 flex gap-4">
                    <button
                        onClick={() => setFilter('pending')}
                        className={`flex-1 py-3 px-4 rounded-lg border transition-all flex items-center justify-center gap-2 ${filter === 'pending'
                                ? 'bg-white border-primary-500 shadow-sm text-primary-700 ring-1 ring-primary-500'
                                : 'bg-slate-100 border-transparent text-slate-600 hover:bg-white hover:border-slate-300'
                            }`}
                    >
                        <Clock size={18} />
                        <span className="font-medium">Pending / In Progress</span>
                        <span className="bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full text-xs font-bold ml-2">
                            {pendingTasks.length}
                        </span>
                    </button>

                    <button
                        onClick={() => setFilter('completed')}
                        className={`flex-1 py-3 px-4 rounded-lg border transition-all flex items-center justify-center gap-2 ${filter === 'completed'
                                ? 'bg-white border-green-500 shadow-sm text-green-700 ring-1 ring-green-500'
                                : 'bg-slate-100 border-transparent text-slate-600 hover:bg-white hover:border-slate-300'
                            }`}
                    >
                        <CheckCircle size={18} />
                        <span className="font-medium">Completed</span>
                        <span className="bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full text-xs font-bold ml-2">
                            {completedTasks.length}
                        </span>
                    </button>
                </div>

                {/* Task List */}
                <div className="flex-1 overflow-y-auto p-6">
                    {loading ? (
                        <div className="flex justify-center py-12">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
                        </div>
                    ) : displayedTasks.length === 0 ? (
                        <div className="text-center py-12 text-slate-500">
                            <p>No {filter} tasks found for this workflow.</p>
                        </div>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="text-xs font-semibold text-slate-500 uppercase border-b border-slate-200">
                                        <th className="py-3 px-4">Company</th>
                                        <th className="py-3 px-4">Type</th>
                                        <th className="py-3 px-4">Assigned To</th>
                                        <th className="py-3 px-4 text-center">Qty (Target/Achieved)</th>
                                        <th className="py-3 px-4">Status</th>
                                        <th className="py-3 px-4">Date</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {displayedTasks.map(task => (
                                        <tr key={task.task_id} className="hover:bg-slate-50 transition-colors">
                                            <td className="py-3 px-4 font-medium text-slate-900">{task.company_name}</td>
                                            <td className="py-3 px-4 text-slate-600">{task.task_type}</td>
                                            <td className="py-3 px-4 text-slate-600">
                                                {task.assigned_user ? task.assigned_user.full_name : <span className="text-slate-400 italic">Unassigned</span>}
                                            </td>
                                            <td className="py-3 px-4 text-center">
                                                <span className="text-slate-900 font-medium">{task.achieved_qty}</span>
                                                <span className="text-slate-400 mx-1">/</span>
                                                <span className="text-slate-500">{task.target_qty}</span>
                                            </td>
                                            <td className="py-3 px-4">
                                                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${task.status === 'Completed' ? 'bg-green-100 text-green-800' :
                                                        task.status === 'In Progress' ? 'bg-blue-100 text-blue-800' :
                                                            'bg-slate-100 text-slate-800'
                                                    }`}>
                                                    {task.status}
                                                </span>
                                            </td>
                                            <td className="py-3 px-4 text-slate-500 text-sm">
                                                {new Date(task.created_at).toLocaleDateString()}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default WorkflowTasksModal;
