import React from 'react';
import { Link } from 'react-router-dom';
import { Home, AlertCircle } from 'lucide-react';

const NotFound = () => {
    return (
        <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-slate-900 px-4">
            <div className="text-center">
                <div className="flex justify-center mb-6">
                    <div className="w-24 h-24 bg-red-100 dark:bg-red-900/30 rounded-full flex items-center justify-center">
                        <AlertCircle className="w-12 h-12 text-red-600 dark:text-red-400" />
                    </div>
                </div>
                <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-4">Page Not Found</h1>
                <p className="text-lg text-slate-600 dark:text-slate-400 mb-8 max-w-md mx-auto">
                    The page you are looking for doesn't exist or has been moved.
                </p>
                <Link
                    to="/"
                    className="inline-flex items-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium transition-colors shadow-lg shadow-primary-600/20"
                >
                    <Home size={20} />
                    Back to Dashboard
                </Link>
            </div>
        </div>
    );
};

export default NotFound;
