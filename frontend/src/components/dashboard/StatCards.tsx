import type { DashboardStats } from '../../types';
import { TrendingDown, TrendingUp, Scale } from 'lucide-react';

interface Props {
  stats: DashboardStats;
}

export default function StatCards({ stats }: Props) {
  const fmt = (n: number) =>
    new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n);

  return (
    <div className="stat-cards">
      <div className="stat-card stat-owe">
        <div className="stat-card-icon">
          <TrendingDown size={22} />
        </div>
        <div className="stat-card-body">
          <span className="stat-label">You Owe</span>
          <span className="stat-value">${fmt(stats.total_to_pay)}</span>
        </div>
      </div>

      <div className="stat-card stat-owed">
        <div className="stat-card-icon">
          <TrendingUp size={22} />
        </div>
        <div className="stat-card-body">
          <span className="stat-label">Owed to You</span>
          <span className="stat-value">${fmt(stats.total_owed_to_you)}</span>
        </div>
      </div>

      <div className={`stat-card ${stats.net_balance >= 0 ? 'stat-positive' : 'stat-negative'}`}>
        <div className="stat-card-icon">
          <Scale size={22} />
        </div>
        <div className="stat-card-body">
          <span className="stat-label">Net Balance</span>
          <span className="stat-value">
            {stats.net_balance >= 0 ? '+' : '-'}${fmt(Math.abs(stats.net_balance))}
          </span>
        </div>
      </div>
    </div>
  );
}
