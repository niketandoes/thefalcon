import type { GroupDebt } from '../../types';
import { useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';

interface Props {
  debts: GroupDebt[];
}

export default function GroupDebtList({ debts }: Props) {
  const navigate = useNavigate();
  const fmt = (n: number) =>
    new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n);

  if (debts.length === 0) {
    return <p className="empty-state">No group debts yet.</p>;
  }

  return (
    <div className="debt-list">
      {debts.map((d) => {
        const net = d.you_are_owed - d.you_owe;
        return (
          <div
            key={d.group_id}
            className="debt-row"
            onClick={() => navigate(`/groups/${d.group_id}`)}
          >
            <div className="debt-row-info">
              <span className="debt-group-name">{d.group_name}</span>
              <div className="debt-row-details">
                {d.you_owe > 0 && (
                  <span className="debt-tag debt-tag-owe">Owe ${fmt(d.you_owe)}</span>
                )}
                {d.you_are_owed > 0 && (
                  <span className="debt-tag debt-tag-owed">Owed ${fmt(d.you_are_owed)}</span>
                )}
              </div>
            </div>
            <div className="debt-row-right">
              <span className={`debt-net ${net >= 0 ? 'positive' : 'negative'}`}>
                {net >= 0 ? '+' : ''}${fmt(net)}
              </span>
              <ArrowRight size={16} className="debt-arrow" />
            </div>
          </div>
        );
      })}
    </div>
  );
}
