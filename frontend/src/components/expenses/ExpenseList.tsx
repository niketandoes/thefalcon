import type { Expense } from '../../types';
import { Receipt, RefreshCw } from 'lucide-react';

interface Props {
  expenses: Expense[];
  showGroup?: boolean;
}

export default function ExpenseList({ expenses, showGroup = false }: Props) {
  const fmt = (n: number) =>
    new Intl.NumberFormat('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(n);

  const fmtDate = (d: string) => new Date(d).toLocaleDateString('en-US', {
    month: 'short', day: 'numeric',
  });

  if (expenses.length === 0) {
    return (
      <div className="empty-state">
        <Receipt size={32} className="empty-icon" />
        <p>No expenses yet</p>
      </div>
    );
  }

  return (
    <div className="expense-list">
      {expenses.map((exp) => (
        <div key={exp.id} className="expense-row">
          <div className="expense-row-left">
            <div className="expense-row-icon">
              <Receipt size={16} />
            </div>
            <div className="expense-row-info">
              <span className="expense-title">{exp.description}</span>
              <span className="expense-meta">
                {fmtDate(exp.expense_date)} · {exp.split_type}
                {exp.is_recurring && (
                  <span className="expense-recurring-badge">
                    <RefreshCw size={10} /> {exp.recurring_frequency}
                  </span>
                )}
              </span>
            </div>
          </div>
          <div className="expense-row-right">
            <span className="expense-amount">{exp.currency} {fmt(exp.amount)}</span>
            <span className="expense-split-count">{exp.splits.length} split{exp.splits.length !== 1 ? 's' : ''}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
