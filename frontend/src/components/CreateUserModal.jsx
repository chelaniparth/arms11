import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { X, Save } from 'lucide-react';

const CreateUserModal = ({ isOpen, onClose, onUserSaved, userToEdit = null }) => {
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({
        full_name: '',
        email: '',
        username: '',
        password: '',
        role: 'analyst',
        is_active: true
    });

    useEffect(() => {
        if (isOpen) {
            if (userToEdit) {
                setFormData({
                    full_name: userToEdit.full_name,
                    email: userToEdit.email,
                    username: userToEdit.username,
                    password: '', // Don't populate password for edit
                    role: userToEdit.role,
                    is_active: userToEdit.is_active
                });
            } else {
                setFormData({
                    full_name: '',
                    email: '',
                    username: '',
                    password: '',
                    role: 'analyst',
                    is_active: true
                });
            }
        }
    }, [isOpen, userToEdit]);

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
        try {
            if (userToEdit) {
                // Update existing user
                const payload = { ...formData };
                if (!payload.password) delete payload.password; // Don't send empty password
                delete payload.username; // Username cannot be changed

                await api.put(`/users/${userToEdit.id}`, payload);
            } else {
                // Create new user
                await api.post('/users/', formData);
            }
            onUserSaved();
            onClose();
        } catch (error) {
            console.error("Failed to save user", error);
            alert(error.response?.data?.detail || "Failed to save user");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
            <div className="bg-white rounded-xl shadow-xl w-full max-w-lg">
                <div className="flex items-center justify-between p-6 border-b border-slate-100">
                    <h2 className="text-xl font-bold text-slate-900">
                        {userToEdit ? 'Edit User' : 'Add New User'}
                    </h2>
                    <button onClick={onClose} className="p-2 hover:bg-slate-100 rounded-full text-slate-500 transition-colors">
                        <X size={20} />
                    </button>
                </div>

                <form onSubmit={handleSubmit} className="p-6 space-y-4">
                    {/* Full Name */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Full Name</label>
                        <input
                            type="text"
                            name="full_name"
                            required
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all"
                            value={formData.full_name}
                            onChange={handleChange}
                        />
                    </div>

                    {/* Email */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                        <input
                            type="email"
                            name="email"
                            required
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all"
                            value={formData.email}
                            onChange={handleChange}
                        />
                    </div>

                    {/* Username */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
                        <input
                            type="text"
                            name="username"
                            required
                            disabled={!!userToEdit}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all disabled:bg-slate-100 disabled:text-slate-500"
                            value={formData.username}
                            onChange={handleChange}
                        />
                    </div>

                    {/* Password */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                            {userToEdit ? 'Password (leave blank to keep current)' : 'Password'}
                        </label>
                        <input
                            type="password"
                            name="password"
                            required={!userToEdit}
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all"
                            value={formData.password}
                            onChange={handleChange}
                        />
                    </div>

                    {/* Role */}
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Role</label>
                        <select
                            name="role"
                            className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary-100 focus:border-primary-500 transition-all"
                            value={formData.role}
                            onChange={handleChange}
                        >
                            <option value="analyst">Analyst</option>
                            <option value="manager">Manager</option>
                            <option value="admin">Admin</option>
                        </select>
                    </div>

                    {/* Active Status */}
                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            name="is_active"
                            id="is_active"
                            className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-slate-300 rounded"
                            checked={formData.is_active}
                            onChange={handleChange}
                        />
                        <label htmlFor="is_active" className="ml-2 block text-sm text-slate-900">
                            Active Account
                        </label>
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
                            disabled={loading}
                            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors shadow-lg shadow-primary-600/20"
                        >
                            <Save className="w-4 h-4 mr-2" />
                            {loading ? 'Saving...' : 'Save User'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateUserModal;
