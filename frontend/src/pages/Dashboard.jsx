import React, { useEffect, useState } from 'react';
import { ArrowUpRight, CheckCircle2, Clock, AlertCircle, BarChart2, Users, Activity } from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

const MetricCard = ({ label, value, subtext, icon: Icon, color }) => (
    <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex items-start justify-between mb-4">
            <div className={`p-3 rounded-xl ${color} bg-opacity-10`}>
                <Icon size={24} className={color.replace('bg-', 'text-')} />
            </div>
            {/* Trend or subtext could go here */}
        </div>
        <h3 className="text-3xl font-bold text-slate-900 mb-1">{value}</h3>
        <p className="text-sm text-slate-500 font-medium">{label}</p>
        {subtext && <p className="text-xs text-slate-400 mt-2">{subtext}</p>}
    </div>
);

const Dashboard = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await api.get('/dashboard/stats');
                setStats(response.data);
            } catch (error) {
                console.error("Failed to fetch dashboard stats", error);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, []);

    if (loading) {
        return <div className="p-8 text-center text-slate-500">Loading dashboard...</div>;
    }

    if (!stats) {
        return <div className="p-8 text-center text-red-500">Failed to load dashboard data.</div>;
    }

    const { my_stats, system_stats } = stats || {};

    console.log("Dashboard Stats:", stats);

    if (!my_stats || !system_stats) {
        return <div className="p-8 text-center text-amber-500">Incomplete dashboard data received.</div>;
    }
    const isAdminOrManager = user?.role === 'admin' || user?.role === 'manager';

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-2xl font-bold text-slate-900">Dashboard Overview</h1>
                <p className="text-slate-500 mt-1">Welcome back, {user?.full_name}. Here's your performance today.</p>
            </div>

            {/* My Stats Section */}
            <div>
                <h2 className="text-lg font-bold text-slate-900 mb-4">My Performance (Today)</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <MetricCard
                        label="Assigned"
                        value={my_stats.tasks_assigned_today}
                        icon={Clock}
                        color="bg-blue-500"
                    />
                    <MetricCard
                        label="In Progress"
                        value={my_stats.tasks_in_progress}
                        icon={Activity}
                        color="bg-amber-500"
                    />
                    <MetricCard
                        label="Completed"
                        value={my_stats.tasks_completed_today}
                        icon={CheckCircle2}
                        color="bg-emerald-500"
                    />
                    <MetricCard
                        label="Avg Time"
                        value={`${Number(my_stats.avg_completion_time || 0).toFixed(1)}h`}
                        icon={BarChart2}
                        color="bg-purple-500"
                    />
                </div>
            </div>

            {/* System Stats Section (Admin/Manager Only) */}
            {isAdminOrManager && (
                <div className="mt-8">
                    <h2 className="text-lg font-bold text-slate-900 mb-4">System Overview</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        <MetricCard
                            label="Total Active Tasks"
                            value={system_stats.total_active_tasks}
                            subtext="Pending + In Progress"
                            icon={Activity}
                            color="bg-indigo-500"
                        />
                        {/* Add more system metrics here if needed */}
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        {/* Status Breakdown */}
                        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
                            <h3 className="text-lg font-bold text-slate-900 mb-4">Task Status Breakdown</h3>
                            <div className="space-y-4">
                                {Object.entries(system_stats.status_breakdown).map(([status, count]) => (
                                    <div key={status} className="flex items-center justify-between">
                                        <span className="text-sm font-medium text-slate-600">{status}</span>
                                        <span className="text-sm font-bold text-slate-900">{count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Top Performers */}
                        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6">
                            <h3 className="text-lg font-bold text-slate-900 mb-4">Top Performers (Today)</h3>
                            <div className="space-y-4">
                                {system_stats.top_performers.map((performer, index) => (
                                    <div key={index} className="flex items-center justify-between">
                                        <div className="flex items-center gap-3">
                                            <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-600">
                                                {performer.name.charAt(0)}
                                            </div>
                                            <span className="text-sm font-medium text-slate-900">{performer.name}</span>
                                        </div>
                                        <span className="text-sm font-bold text-emerald-600">{performer.completed} tasks</span>
                                    </div>
                                ))}
                                {system_stats.top_performers.length === 0 && (
                                    <p className="text-sm text-slate-400">No tasks completed today.</p>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Dashboard;
