import { useNotificationStore } from '../../store/useNotificationStore';
import { useGroupStore } from '../../store/useGroupStore';
import { Bell, Check, X, UserPlus, Receipt } from 'lucide-react';
import { useState } from 'react';
import type { Notification } from '../../types';

interface Props {
  onClose: () => void;
}

export default function NotificationPanel({ onClose }: Props) {
  const { notifications, respondToInvite, markAsRead, fetchNotifications } = useNotificationStore();
  const { fetchGroups } = useGroupStore();
  const [processing, setProcessing] = useState<string | null>(null);

  const handleInviteAction = async (notif: Notification, action: 'accept' | 'reject') => {
    if (!notif.group_id) return;
    setProcessing(notif.id);
    try {
      await respondToInvite(notif.group_id, action);
      await fetchGroups();
      await fetchNotifications();
    } catch { /* handled */ }
    setProcessing(null);
  };

  const handleMarkRead = async (notif: Notification) => {
    if (!notif.is_read) {
      await markAsRead(notif.id);
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case 'GROUP_INVITE': return <UserPlus size={16} />;
      case 'EXPENSE_ADDED': return <Receipt size={16} />;
      default: return <Bell size={16} />;
    }
  };

  const formatTime = (dateStr: string) => {
    const d = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    const hrs = Math.floor(mins / 60);
    if (hrs < 24) return `${hrs}h ago`;
    const days = Math.floor(hrs / 24);
    return `${days}d ago`;
  };

  return (
    <div className="notif-panel">
      <div className="notif-panel-header">
        <h3>Notifications</h3>
        <button className="notif-close" onClick={onClose}><X size={16} /></button>
      </div>
      <div className="notif-panel-body">
        {notifications.length === 0 ? (
          <div className="notif-empty">
            <Bell size={24} className="notif-empty-icon" />
            <p>No notifications yet</p>
          </div>
        ) : (
          notifications.map((notif) => (
            <div
              key={notif.id}
              className={`notif-item ${notif.is_read ? 'read' : 'unread'}`}
              onClick={() => handleMarkRead(notif)}
            >
              <div className="notif-item-icon">{getIcon(notif.type)}</div>
              <div className="notif-item-content">
                <span className="notif-item-title">{notif.title}</span>
                <p className="notif-item-msg">{notif.message}</p>
                <span className="notif-item-time">{formatTime(notif.created_at)}</span>
              </div>
              {notif.type === 'GROUP_INVITE' && !notif.is_read && notif.group_id && (
                <div className="notif-item-actions">
                  <button
                    className="notif-accept"
                    disabled={processing === notif.id}
                    onClick={(e) => { e.stopPropagation(); handleInviteAction(notif, 'accept'); }}
                    title="Accept"
                  >
                    <Check size={14} />
                  </button>
                  <button
                    className="notif-reject"
                    disabled={processing === notif.id}
                    onClick={(e) => { e.stopPropagation(); handleInviteAction(notif, 'reject'); }}
                    title="Reject"
                  >
                    <X size={14} />
                  </button>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
