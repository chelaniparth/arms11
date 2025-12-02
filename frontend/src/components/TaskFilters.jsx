import React from 'react';
import { X, Calendar } from 'lucide-react';
import clsx from 'clsx';

const FilterSection = ({ title, children }) => (
    <div className="space-y-2">
        <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{title}</h3>
        <div className="flex flex-wrap gap-2">
            {children}
        </div>
    </div>
);

const FilterChip = ({ label, active, onClick, colorClass }) => (
    <button
        onClick={onClick}
        className={clsx(
            "px-3 py-1.5 rounded-lg text-sm font-medium transition-all border",
            active
                ? clsx("border-transparent shadow-sm", colorClass)
                : "bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:border-slate-300 dark:hover:border-slate-600"
        )}
    >
        {label}
    </button>
);

const TaskFilters = ({ filters, onFilterChange, onClearFilters }) => {
    const statuses = ['Pending', 'In Progress', 'Completed', 'Under Review', 'Critical'];
    const priorities = ['Low', 'Medium', 'High', 'Critical'];

    const toggleStatus = (status) => {
        const newStatuses = filters.status.includes(status)
            ? filters.status.filter(s => s !== status)
            : [...filters.status, status];
        onFilterChange({ ...filters, status: newStatuses });
    };

    const togglePriority = (priority) => {
        const newPriorities = filters.priority.includes(priority)
            ? filters.priority.filter(p => p !== priority)
            : [...filters.priority, priority];
        onFilterChange({ ...filters, priority: newPriorities });
    };

    const handleDateChange = (e) => {
        onFilterChange({ ...filters, dateRange: { ...filters.dateRange, [e.target.name]: e.target.value } });
    };

    const hasActiveFilters = filters.status.length > 0 || filters.priority.length > 0 || filters.dateRange.start || filters.dateRange.end;

    return (
        <div className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700 p-4 space-y-6 animate-in slide-in-from-top-2 duration-200">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Status Filters */}
                <FilterSection title="Status">
                    {statuses.map(status => (
                        <FilterChip
                            key={status}
                            label={status}
                            active={filters.status.includes(status)}
                            onClick={() => toggleStatus(status)}
                            colorClass="bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300"
                        />
                    ))}
                </FilterSection>

                {/* Priority Filters */}
                <FilterSection title="Priority">
                    {priorities.map(priority => (
                        <FilterChip
                            key={priority}
                            label={priority}
                            active={filters.priority.includes(priority)}
                            onClick={() => togglePriority(priority)}
                            colorClass="bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300"
                        />
                    ))}
                </FilterSection>

                {/* Date Range */}
                <FilterSection title="Date Range">
                    <div className="flex items-center gap-2 w-full">
                        <div className="relative flex-1">
                            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                            <input
                                type="date"
                                name="start"
                                value={filters.dateRange.start}
                                onChange={handleDateChange}
                                className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            />
                        </div>
                        <span className="text-slate-400">-</span>
                        <div className="relative flex-1">
                            <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
                            <input
                                type="date"
                                name="end"
                                value={filters.dateRange.end}
                                onChange={handleDateChange}
                                className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-slate-200 dark:border-slate-600 bg-white dark:bg-slate-700 text-sm text-slate-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                            />
                        </div>
                    </div>
                </FilterSection>
            </div>

            {hasActiveFilters && (
                <div className="flex justify-end pt-2 border-t border-slate-200 dark:border-slate-700">
                    <button
                        onClick={onClearFilters}
                        className="flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200 transition-colors"
                    >
                        <X size={16} />
                        Clear all filters
                    </button>
                </div>
            )}
        </div>
    );
};

export default TaskFilters;
