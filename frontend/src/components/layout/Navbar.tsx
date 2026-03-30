import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/useAuthStore';
import { useNotificationStore } from '../../store/useNotificationStore';
import { Bell, LogOut, LayoutDashboard } from 'lucide-react';
import { useEffect, useState } from 'react';
import NotificationPanel from '../notifications/NotificationPanel';

export default function Navbar() {
  const { user, logout } = useAuthStore();
  const { unreadCount, fetchNotifications } = useNotificationStore();
  const navigate = useNavigate();
  const [showNotifs, setShowNotifs] = useState(false);

  useEffect(() => {
    if (user) {
      fetchNotifications();
      const interval = setInterval(fetchNotifications, 30000);
      return () => clearInterval(interval);
    }
  }, [user, fetchNotifications]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to={user ? '/dashboard' : '/'} className="navbar-brand">
          <span className="brand-icon">⚡</span>
          <span className="brand-text">Split It Fair</span>
        </Link>

        <div className="navbar-actions">
          {user ? (
            <>
              <Link to="/dashboard" className="nav-link" title="Dashboard">
                <LayoutDashboard size={18} />
              </Link>
              <div className="notif-wrapper">
                <button
                  className="nav-icon-btn"
                  onClick={() => setShowNotifs(!showNotifs)}
                  title="Notifications"
                >
                  <Bell size={18} />
                  {unreadCount > 0 && (
                    <span className="notif-badge">{unreadCount > 9 ? '9+' : unreadCount}</span>
                  )}
                </button>
                {showNotifs && (
                  <NotificationPanel onClose={() => setShowNotifs(false)} />
                )}
              </div>
              <div className="nav-user">
                <span className="nav-user-name">{user.full_name || user.email}</span>
                <span className="nav-user-currency">{user.preferred_currency}</span>
              </div>
              <button className="nav-icon-btn nav-logout" onClick={handleLogout} title="Logout">
                <LogOut size={18} />
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="nav-btn nav-btn-ghost">Login</Link>
              <Link to="/register" className="nav-btn nav-btn-primary">Register</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
