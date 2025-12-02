import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import { ArrowLeft, Clock, User, Tag, FileText, MessageSquare, Send } from 'lucide-react';
import clsx from 'clsx';

const TaskDetails = () => {
    const { taskId } = useParams();
    const navigate = useNavigate();
    const [task, setTask] = useState(null);
    const [comments, setComments] = useState([]);
    const [history, setHistory] = useState([]);
    const [newComment, setNewComment] = useState('');
    const [loading, setLoading] = useState(true);

    const fetchTaskData = async () => {
        try {
            const [taskRes, commentsRes, historyRes] = await Promise.all([
                api.get(`/tasks/${taskId}`),
                api.get(`/tasks/${taskId}/comments`),
                api.get(`/tasks/${taskId}/history`)
            ]);
            setTask(taskRes.data);
            setComments(commentsRes.data);
            setHistory(historyRes.data);
        } catch (error) {
            console.error("Failed to fetch task details", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTaskData();
    }, [taskId]);

    const handleStatusChange = async (newStatus) => {
        try {
            await api.put(`/tasks/${taskId}`, { status: newStatus });
            fetchTaskData(); // Refresh data
        } catch (error) {
            console.error("Failed to update status", error);
        }
    };

    const handlePostComment = async (e) => {
        e.preventDefault();
        if (!newComment.trim()) return;
        try {
            await api.post(`/tasks/${taskId}/comments`, { comment_text: newComment, is_internal: false });
            setNewComment('');
            fetchTaskData();
        } catch (error) {
            console.error("Failed to post comment", error);
        }
    };

    if (loading) return <div className="p-6">Loading...</div>;
    if (!task) return <div className="p-6">Task not found</div>;

    return (
        <div className="p-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center">
                    <button onClick={() => navigate('/tasks')} className="mr-4 p-2 hover:bg-slate-100 rounded-full">
                        <ArrowLeft className="w-5 h-5 text-slate-600" />
                    </button>
                    <div>
                        <h1 className="text-2xl font-bold text-slate-900">{task.company_name}</h1>
                        <p className="text-slate-500 text-sm">Task ID: #{task.task_id} • {task.document_type}</p>
                    </div>
                </div>
                <div className="flex space-x-3">
                    <select
                        value={task.status}
                        onChange={(e) => handleStatusChange(e.target.value)}
                        className={clsx(
                            "px-3 py-1.5 rounded-full text-sm font-medium border-none focus:ring-2 focus:ring-offset-2",
                            task.status === 'Completed' ? "bg-green-100 text-green-800" :
                                task.status === 'In Progress' ? "bg-blue-100 text-blue-800" :
                                    "bg-yellow-100 text-yellow-800"
                        )}
                    >
                        <option value="Pending">Pending</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Under Review">Under Review</option>
                        <option value="Completed">Completed</option>
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Content */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Details Card */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-semibold mb-4 flex items-center">
                            <FileText className="w-5 h-5 mr-2 text-slate-500" />
                            Description
                        </h3>
                        <p className="text-slate-700 whitespace-pre-wrap">{task.description || "No description provided."}</p>
                    </div>

                    {/* Comments Section */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-semibold mb-4 flex items-center">
                            <MessageSquare className="w-5 h-5 mr-2 text-slate-500" />
                            Comments
                        </h3>

                        <div className="space-y-4 mb-6 max-h-96 overflow-y-auto">
                            {comments.length === 0 ? (
                                <p className="text-slate-400 text-sm italic">No comments yet.</p>
                            ) : (
                                comments.map(comment => (
                                    <div key={comment.comment_id} className="bg-slate-50 p-3 rounded-lg">
                                        <div className="flex justify-between text-xs text-slate-500 mb-1">
                                            <span className="font-medium text-slate-700">User {comment.user_id}</span> {/* Ideally resolve name */}
                                            <span>{new Date(comment.created_at).toLocaleString()}</span>
                                        </div>
                                        <p className="text-slate-800 text-sm">{comment.comment_text}</p>
                                    </div>
                                ))
                            )}
                        </div>

                        <form onSubmit={handlePostComment} className="flex gap-2">
                            <input
                                type="text"
                                className="flex-1 px-3 py-2 border border-slate-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                                placeholder="Add a comment..."
                                value={newComment}
                                onChange={(e) => setNewComment(e.target.value)}
                            />
                            <button
                                type="submit"
                                className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700 flex items-center"
                            >
                                <Send className="w-4 h-4" />
                            </button>
                        </form>
                    </div>
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                    {/* Info Card */}
                    <div className="bg-white rounded-lg shadow p-6 space-y-4">
                        <h3 className="text-lg font-semibold mb-2">Details</h3>

                        <div className="flex items-center justify-between py-2 border-b border-slate-100">
                            <span className="text-slate-500 text-sm flex items-center"><Tag className="w-4 h-4 mr-2" /> Priority</span>
                            <span className={clsx(
                                "px-2 py-1 rounded text-xs font-medium",
                                task.priority === 'Critical' ? "bg-red-100 text-red-800" :
                                    task.priority === 'High' ? "bg-orange-100 text-orange-800" :
                                        "bg-slate-100 text-slate-800"
                            )}>{task.priority}</span>
                        </div>

                        <div className="flex items-center justify-between py-2 border-b border-slate-100">
                            <span className="text-slate-500 text-sm flex items-center"><User className="w-4 h-4 mr-2" /> Assignee</span>
                            <span className="text-sm font-medium text-slate-900">{task.assigned_user_id ? "Assigned" : "Unassigned"}</span>
                        </div>

                        <div className="flex items-center justify-between py-2 border-b border-slate-100">
                            <span className="text-slate-500 text-sm flex items-center"><Clock className="w-4 h-4 mr-2" /> Due Date</span>
                            <span className="text-sm text-slate-900">{task.due_date ? new Date(task.due_date).toLocaleDateString() : "None"}</span>
                        </div>
                    </div>

                    {/* History Card */}
                    <div className="bg-white rounded-lg shadow p-6">
                        <h3 className="text-lg font-semibold mb-4 flex items-center">
                            <Clock className="w-5 h-5 mr-2 text-slate-500" />
                            Audit Log
                        </h3>
                        <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
                            {history.map((item, index) => (
                                <div key={item.history_id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                                    {/* Icon */}
                                    <div className="flex items-center justify-center w-10 h-10 rounded-full border border-white bg-slate-50 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10">
                                        <div className="w-2.5 h-2.5 bg-primary-500 rounded-full ring-2 ring-white"></div>
                                    </div>

                                    {/* Content */}
                                    <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] bg-white p-4 rounded-xl border border-slate-100 shadow-sm">
                                        <div className="flex items-center justify-between space-x-2 mb-1">
                                            <div className="font-bold text-slate-900 text-sm">
                                                {item.action || 'Update'}
                                                <span className="font-normal text-slate-500"> - {item.field_name}</span>
                                            </div>
                                            <time className="font-caveat font-medium text-xs text-slate-500">
                                                {new Date(item.changed_at).toLocaleString()}
                                            </time>
                                        </div>
                                        <div className="text-slate-600 text-sm">
                                            {item.old_value && item.new_value ? (
                                                <>
                                                    Changed from <span className="font-medium text-red-600 bg-red-50 px-1 rounded">{item.old_value}</span> to <span className="font-medium text-emerald-600 bg-emerald-50 px-1 rounded">{item.new_value}</span>
                                                </>
                                            ) : (
                                                <span>Updated value to <span className="font-medium text-slate-900">{item.new_value}</span></span>
                                            )}
                                        </div>
                                        <div className="mt-2 flex items-center gap-2 text-xs text-slate-400">
                                            <User size={12} />
                                            <span>{item.user ? item.user.full_name : 'System'}</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                            {history.length === 0 && (
                                <div className="text-center py-4 text-slate-400 italic text-sm">No history available for this task.</div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TaskDetails;
