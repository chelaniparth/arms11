import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, AlertCircle, CheckCircle, ArrowLeft } from 'lucide-react';
import api from '../services/api';
import clsx from 'clsx';
import { useAuth } from '../context/AuthContext';

const TaskBulkUpload = () => {
    const navigate = useNavigate();
    const { user: currentUser } = useAuth();
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (currentUser && currentUser.role !== 'admin' && currentUser.role !== 'manager') {
            navigate('/tasks');
        }
    }, [currentUser, navigate]);

    const handleFileChange = (e) => {
        if (e.target.files[0]) {
            setFile(e.target.files[0]);
            setError(null);
            setResult(null);
        }
    };

    const handleUpload = async () => {
        if (!file) {
            setError("Please select a file first.");
            return;
        }

        setUploading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('/tasks/upload', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setResult(response.data);
        } catch (err) {
            console.error("Upload failed", err);
            setError(err.response?.data?.detail || "Failed to upload file. Please try again.");
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex items-center gap-4">
                <button
                    onClick={() => navigate('/tasks')}
                    className="p-2 hover:bg-slate-100 rounded-lg text-slate-500 transition-colors"
                >
                    <ArrowLeft size={20} />
                </button>
                <div>
                    <h1 className="text-2xl font-bold text-slate-900">Bulk Task Upload</h1>
                    <p className="text-slate-500">Import tasks from a CSV file.</p>
                </div>
            </div>

            <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-8">
                <div className="flex flex-col items-center justify-center border-2 border-dashed border-slate-300 rounded-xl p-12 bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer relative">
                    <input
                        type="file"
                        accept=".csv"
                        onChange={handleFileChange}
                        className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                    />
                    <div className="w-16 h-16 bg-primary-50 text-primary-600 rounded-full flex items-center justify-center mb-4">
                        <Upload size={32} />
                    </div>
                    <p className="text-lg font-medium text-slate-900 mb-1">
                        {file ? file.name : "Click to upload or drag and drop"}
                    </p>
                    <p className="text-sm text-slate-500">CSV files only (max 10MB)</p>
                </div>

                {file && (
                    <div className="mt-6 flex justify-end">
                        <button
                            onClick={handleUpload}
                            disabled={uploading}
                            className={clsx(
                                "flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-colors shadow-lg shadow-primary-600/20",
                                uploading
                                    ? "bg-slate-100 text-slate-400 cursor-not-allowed"
                                    : "bg-primary-600 hover:bg-primary-700 text-white"
                            )}
                        >
                            {uploading ? 'Uploading...' : 'Upload Tasks'}
                        </button>
                    </div>
                )}

                {error && (
                    <div className="mt-6 p-4 bg-red-50 text-red-700 rounded-xl flex items-start gap-3">
                        <AlertCircle className="shrink-0 mt-0.5" size={20} />
                        <div>
                            <p className="font-medium">Upload Failed</p>
                            <p className="text-sm mt-1">{error}</p>
                        </div>
                    </div>
                )}

                {result && (
                    <div className="mt-8 space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <div className="grid grid-cols-3 gap-4">
                            <div className="p-4 bg-slate-50 rounded-xl border border-slate-200 text-center">
                                <p className="text-sm text-slate-500 mb-1">Total Processed</p>
                                <p className="text-2xl font-bold text-slate-900">{result.total_processed}</p>
                            </div>
                            <div className="p-4 bg-emerald-50 rounded-xl border border-emerald-100 text-center">
                                <p className="text-sm text-emerald-600 mb-1">Successful</p>
                                <p className="text-2xl font-bold text-emerald-700">{result.success_count}</p>
                            </div>
                            <div className="p-4 bg-red-50 rounded-xl border border-red-100 text-center">
                                <p className="text-sm text-red-600 mb-1">Failed</p>
                                <p className="text-2xl font-bold text-red-700">{result.failed_count}</p>
                            </div>
                        </div>

                        {result.errors.length > 0 && (
                            <div className="border border-red-100 rounded-xl overflow-hidden">
                                <div className="bg-red-50 px-4 py-3 border-b border-red-100 flex items-center gap-2">
                                    <AlertCircle size={16} className="text-red-600" />
                                    <h3 className="font-medium text-red-900">Error Log</h3>
                                </div>
                                <div className="max-h-60 overflow-y-auto bg-white p-4 space-y-2">
                                    {result.errors.map((err, index) => (
                                        <div key={index} className="text-sm text-red-600 font-mono bg-red-50/50 p-2 rounded">
                                            {err}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {result.success_count > 0 && (
                            <div className="flex justify-center">
                                <button
                                    onClick={() => navigate('/tasks')}
                                    className="text-primary-600 font-medium hover:underline"
                                >
                                    View Created Tasks
                                </button>
                            </div>
                        )}
                    </div>
                )}
            </div>

            <div className="bg-blue-50 border border-blue-100 rounded-xl p-6">
                <h3 className="font-medium text-blue-900 mb-2 flex items-center gap-2">
                    <FileText size={18} />
                    CSV Format Guide
                </h3>
                <p className="text-sm text-blue-700 mb-4">
                    Your CSV file must include the following headers:
                </p>
                <div className="bg-white border border-blue-200 rounded-lg p-3 font-mono text-xs text-slate-600 overflow-x-auto">
                    company_name,document_type,task_type,priority,description,notes
                </div>
                <p className="text-xs text-blue-600 mt-2">
                    * Required fields: company_name, document_type, task_type
                </p>
            </div>
        </div>
    );
};

export default TaskBulkUpload;
