import type { ReactNode } from 'react';

interface StatCardProps {
  icon: ReactNode;
  label: string;
  value: string;
  accentColor?: string; // tailwind color class fragment, e.g. "emerald" | "rose" | "amber"
  subtitle?: string;
}

export default function StatCard({
  icon,
  label,
  value,
  accentColor = 'indigo',
  subtitle,
}: StatCardProps) {
  const bgMap: Record<string, string> = {
    indigo: 'bg-indigo-500/10',
    emerald: 'bg-emerald-500/10',
    rose: 'bg-rose-500/10',
    amber: 'bg-amber-500/10',
    sky: 'bg-sky-500/10',
  };
  const textMap: Record<string, string> = {
    indigo: 'text-indigo-400',
    emerald: 'text-emerald-400',
    rose: 'text-rose-400',
    amber: 'text-amber-400',
    sky: 'text-sky-400',
  };

  return (
    <div className="bg-slate-900 border border-white/5 p-6 rounded-2xl flex items-center gap-4 hover:border-white/10 transition-colors">
      <div className={`p-4 rounded-2xl ${bgMap[accentColor] || bgMap.indigo}`}>
        <span className={textMap[accentColor] || textMap.indigo}>{icon}</span>
      </div>
      <div>
        <p className="text-sm font-medium text-slate-400">{label}</p>
        <h2 className="text-2xl lg:text-3xl font-bold text-white">{value}</h2>
        {subtitle && <p className="text-xs text-slate-500 mt-0.5">{subtitle}</p>}
      </div>
    </div>
  );
}
