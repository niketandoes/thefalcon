import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from './store/useAuthStore';
import Navbar from './components/layout/Navbar';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import Dashboard from './pages/Dashboard';
import GroupDashboard from './pages/GroupDashboard';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore();
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

function PublicOnlyRoute({ children }: { children: React.ReactNode }) {
  const { token } = useAuthStore();
  if (token) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}

export default function App() {
  const { token, fetchMe, user } = useAuthStore();

  useEffect(() => {
    if (token && !user) {
      fetchMe();
    }
  }, [token, user, fetchMe]);

  return (
    <BrowserRouter>
      <div className="app-shell">
        <Navbar />
        <main className="app-main">
          <Routes>
            <Route path="/" element={
              <PublicOnlyRoute><LandingPage /></PublicOnlyRoute>
            } />
            <Route path="/login" element={
              <PublicOnlyRoute><LoginPage /></PublicOnlyRoute>
            } />
            <Route path="/register" element={
              <PublicOnlyRoute><RegisterPage /></PublicOnlyRoute>
            } />
            <Route path="/dashboard" element={
              <ProtectedRoute><Dashboard /></ProtectedRoute>
            } />
            <Route path="/groups/:groupId" element={
              <ProtectedRoute><GroupDashboard /></ProtectedRoute>
            } />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
