import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { Plus, Filter, MoreHorizontal, Search, Edit2, Trash2 } from 'lucide-react';
import clsx from 'clsx';
import CreateUserModal from '../components/CreateUserModal';
import { useAuth } from '../context/AuthContext';

const RoleBadge = ({ role }) => {
    const styles = {
        'admin': 'bg-purple-50 text-purple-600',
        'manager': 'bg-blue-50 text-blue-600',
        'analyst': 'bg-slate-100 text-slate-600',
    };

    return (
        <span className={clsx("px-2.5 py-1 rounded-full text-xs font-medium capitalize", styles[role] || styles['analyst'])}>
            {role}
        </span>
    );
};

const Team = () => {
    const { user: currentUser } = useAuth();
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [userToEdit, setUserToEdit] = useState(null);

    const fetchUsers = async () => {
        setLoading(true);
        try {
            const response = await api.get('/users/');
            let fetchedUsers = response.data;

            // Custom Sort: Nisrag first, then Komal, then others
            fetchedUsers.sort((a, b) => {
                const isNisragA = a.full_name.toLowerCase().includes('nisrag') || a.username.toLowerCase().includes('nisrag');
                const isNisragB = b.full_name.toLowerCase().includes('nisrag') || b.username.toLowerCase().includes('nisrag');

                if (isNisragA && !isNisragB) return -1;
                if (!isNisragA && isNisragB) return 1;

                const isKomalA = a.full_name.toLowerCase().includes('komal') || a.username.toLowerCase().includes('komal');
                const isKomalB = b.full_name.toLowerCase().includes('komal') || b.username.toLowerCase().includes('komal');

                if (isKomalA && !isKomalB) return -1;
                if (!isKomalA && isKomalB) return 1;

                return 0;
            });

            setUsers(fetchedUsers);
        } catch (error) {
            console.error("Failed to fetch users", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleUserSaved = () => {
        fetchUsers();
    };

    const handleEditClick = (user) => {
        setUserToEdit(user);
        setIsCreateModalOpen(true);
    };

    const handleCreateClick = () => {
        setUserToEdit(null);
        setIsCreateModalOpen(true);
    };

    const handleDeleteClick = async (userId) => {
        if (window.confirm("Are you sure you want to delete this user?")) {
            try {
                await api.delete(`/users/${userId}`);
                fetchUsers();
            } catch (error) {
                console.error("Failed to delete user", error);
                alert("Failed to delete user");
            }
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Team Members</h1>
                    <p className="text-slate-500 mt-1">Manage your team and their roles.</p>
                </div>
                <button
                    onClick={handleCreateClick}
                    className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors font-medium shadow-lg shadow-primary-600/20"
                >
                    <Plus size={18} />
                    Add Member
                </button>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
                <div className="p-4 border-b border-slate-100 flex items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                        <button className="flex items-center gap-2 px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-50 rounded-lg border border-slate-200">
                            <Filter size={16} />
                            Filter
                        </button>
                        <div className="h-6 w-px bg-slate-200"></div>
                        <span className="text-sm text-slate-500">{users.length} members found</span>
                    </div>
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                        <input
                            type="text"
                            placeholder="Search members..."
                            className="pl-9 pr-4 py-1.5 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-100 focus:border-primary-500 w-64"
                        />
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-slate-50 text-slate-500 font-medium">
                            <tr>
                                <th className="px-6 py-4">Name</th>
                                <th className="px-6 py-4">Role</th>
                                <th className="px-6 py-4">Status</th>
                                <th className="px-6 py-4">Last Active</th>
                                <th className="px-6 py-4 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                            {loading ? (
                                <tr>
                                    <td colSpan="5" className="px-6 py-12 text-center text-slate-400">
                                        Loading team members...
                                    </td>
                                </tr>
                            ) : users.length === 0 ? (
                                <tr>
                                    <td colSpan="5" className="px-6 py-12 text-center text-slate-400">
                                        No team members found.
                                    </td>
                                </tr>
                            ) : (
                                users.map((user) => (
                                    <tr key={user.id} className="hover:bg-slate-50 transition-colors">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 rounded-full bg-slate-200 flex items-center justify-center text-slate-500 font-medium text-xs">
                                                    {user.full_name.charAt(0)}
                                                </div>
                                                <div>
                                                    <div className="font-medium text-slate-900">{user.full_name}</div>
                                                    <div className="text-xs text-slate-500">{user.email}</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <RoleBadge role={user.role} />
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={clsx(
                                                "inline-flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium",
                                                user.is_active ? "text-emerald-700 bg-emerald-50" : "text-slate-600 bg-slate-100"
                                            )}>
                                                <span className={clsx("w-1.5 h-1.5 rounded-full", user.is_active ? "bg-emerald-500" : "bg-slate-400")}></span>
                                                {user.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-slate-500">
                                            {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex items-center justify-end gap-2">
                                                <button
                                                    onClick={() => handleEditClick(user)}
                                                    className="p-1.5 text-slate-400 hover:text-primary-600 hover:bg-primary-50 rounded transition-colors"
                                                    title="Edit User"
                                                >
                                                    <Edit2 size={16} />
                                                </button>
                                                {currentUser?.role === 'admin' && user.id !== currentUser.id && (
                                                    <button
                                                        onClick={() => handleDeleteClick(user.id)}
                                                        className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                                                        title="Delete User"
                                                    >
                                                        <Trash2 size={16} />
                                                    </button>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <CreateUserModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onUserSaved={handleUserSaved}
                userToEdit={userToEdit}
            />
        </div>
    );
};

export default Team;
