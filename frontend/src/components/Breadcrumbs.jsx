import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { ChevronRight, Home } from 'lucide-react';

const Breadcrumbs = () => {
    const location = useLocation();
    const pathnames = location.pathname.split('/').filter((x) => x);

    if (pathnames.length === 0) return null;

    return (
        <nav className="flex items-center text-sm text-slate-500 dark:text-slate-400 mb-4">
            <Link to="/" className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                <Home size={16} />
            </Link>
            {pathnames.map((value, index) => {
                const to = `/${pathnames.slice(0, index + 1).join('/')}`;
                const isLast = index === pathnames.length - 1;
                const label = value.charAt(0).toUpperCase() + value.slice(1);

                return (
                    <div key={to} className="flex items-center">
                        <ChevronRight size={16} className="mx-2 text-slate-400" />
                        {isLast ? (
                            <span className="font-medium text-slate-900 dark:text-white">
                                {label}
                            </span>
                        ) : (
                            <Link to={to} className="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">
                                {label}
                            </Link>
                        )}
                    </div>
                );
            })}
        </nav>
    );
};

export default Breadcrumbs;
