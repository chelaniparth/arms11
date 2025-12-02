import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, CheckSquare, Settings, Users, FileText, Bell, Search, PlusCircle, GitBranch, Sun, Moon } from 'lucide-react';
import clsx from 'clsx';
import { useAuth } from '../context/AuthContext';
import NotificationBell from '../components/NotificationBell';

import { useTheme } from '../context/ThemeContext';
import Breadcrumbs from '../components/Breadcrumbs';

const SidebarItem = ({ icon: Icon, label, to, active }) => (
    <Link
        to={to}
        className={clsx(
            "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group",
            active
                ? "bg-primary-50 text-primary-600 shadow-sm dark:bg-primary-900/20 dark:text-primary-400"
                : "text-slate-500 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-200"
        )}
    >
        <Icon size={20} className={clsx("transition-colors", active ? "text-primary-600 dark:text-primary-400" : "text-slate-400 group-hover:text-slate-600 dark:text-slate-500 dark:group-hover:text-slate-300")} />
        <span className="font-medium">{label}</span>
    </Link>
);

const DashboardLayout = () => {
    const location = useLocation();
    const { user } = useAuth();
    const { theme, toggleTheme } = useTheme();

    return (
        <div className="flex h-screen bg-slate-50 dark:bg-slate-900 overflow-hidden font-sans transition-colors duration-200">
            {/* Sidebar */}
            <aside className="w-64 bg-white dark:bg-slate-800 border-r border-slate-200 dark:border-slate-700 flex flex-col z-10 transition-colors duration-200">
                <div className="p-6 border-b border-slate-100 dark:border-slate-700">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-primary-500 to-primary-600 flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-primary-500/30">
                            A
                        </div>
                        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-700 dark:from-white dark:to-slate-300">
                            ARMS
                        </span>
                    </div>
                </div>

                <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 px-4 mt-2">
                        Overview
                    </div>
                    <SidebarItem icon={LayoutDashboard} label="Dashboard" to="/" active={location.pathname === '/'} />
                    <SidebarItem icon={CheckSquare} label="Tasks" to="/tasks" active={location.pathname.startsWith('/tasks')} />
                    <SidebarItem icon={GitBranch} label="Workflows" to="/workflows" active={location.pathname.startsWith('/workflows')} />

                    <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-4 px-4 mt-6">
                        Management
                    </div>
                    <SidebarItem icon={Users} label="Team" to="/users" active={location.pathname.startsWith('/users')} />
                    <SidebarItem icon={Settings} label="Settings" to="/settings" active={location.pathname.startsWith('/settings')} />
                </nav>

                <div className="p-4 border-t border-slate-100 dark:border-slate-700 space-y-2">
                    <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-50 dark:bg-slate-700/50 border border-slate-100 dark:border-slate-700">
                        <div className="w-10 h-10 rounded-full bg-slate-200 dark:bg-slate-600 flex items-center justify-center text-slate-500 dark:text-slate-300 font-medium">
                            {user?.full_name ? user.full_name.charAt(0) : 'U'}
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-slate-900 dark:text-white truncate">{user?.full_name || 'User'}</p>
                            <p className="text-xs text-slate-500 dark:text-slate-400 truncate">{user?.role || 'Analyst'}</p>
                        </div>
                    </div>
                    <button
                        onClick={() => {
                            localStorage.removeItem('token');
                            window.location.href = '/login';
                        }}
                        className="w-full flex items-center justify-center gap-2 p-2 text-sm font-medium text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                    >
                        Sign Out
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
                {/* Header */}
                <header className="h-16 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 flex items-center justify-between px-8 z-10 transition-colors duration-200">
                    <div className="flex items-center gap-4 flex-1 max-w-xl">
                        <div className="relative w-full">
                            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
                            <input
                                type="text"
                                placeholder="Search tasks, workflows..."
                                className="w-full pl-10 pr-4 py-2 rounded-lg border border-slate-200 dark:border-slate-600 dark:bg-slate-700 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-100 dark:focus:ring-primary-900 focus:border-primary-500 transition-all text-sm"
                            />
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <button
                            onClick={toggleTheme}
                            className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                            title={theme === 'dark' ? "Switch to Light Mode" : "Switch to Dark Mode"}
                        >
                            {theme === 'dark' ? <Sun size={20} /> : <Moon size={20} />}
                        </button>
                        <NotificationBell />
                    </div>
                </header>

                {/* Page Content */}
                <div className="flex-1 overflow-y-auto p-8">
                    <Breadcrumbs />
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default DashboardLayout;
