
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import DashboardLayout from './layouts/DashboardLayout';
import Dashboard from './pages/Dashboard';
import Tasks from './pages/Tasks';
import Login from './pages/Login';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider, useAuth } from './context/AuthContext';

import TaskDetails from './pages/TaskDetails';
import TaskBulkUpload from './pages/TaskBulkUpload';
import Workflows from './pages/Workflows';
import WorkflowEditor from './pages/WorkflowEditor';
import Team from './pages/Team';
import NotFound from './pages/NotFound';

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  if (loading) return <div>Loading...</div>;
  if (!user) return <Navigate to="/login" />;
  return children;
};

function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/" element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }>
              <Route index element={<Dashboard />} />
              <Route path="tasks" element={<Tasks />} />
              <Route path="tasks/upload" element={<TaskBulkUpload />} />
              <Route path="tasks/:taskId" element={<TaskDetails />} />
              <Route path="workflows" element={<Workflows />} />
              <Route path="workflows/new" element={<WorkflowEditor />} />
              <Route path="workflows/:configId" element={<WorkflowEditor />} />
              <Route path="users" element={<Team />} />
              {/* Add other routes here */}
            </Route>
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
