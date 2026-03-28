import type { ButtonHTMLAttributes, ReactNode } from 'react';

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  icon?: ReactNode;
  loading?: boolean;
  fullWidth?: boolean;
}

const variants: Record<Variant, string> = {
  primary:
    'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20',
  secondary:
    'bg-slate-800/60 hover:bg-slate-700 border border-white/10 text-slate-200',
  ghost:
    'bg-transparent hover:bg-white/5 text-slate-300 hover:text-white',
  danger:
    'bg-rose-600/80 hover:bg-rose-500 text-white shadow-lg shadow-rose-500/20',
};

export default function Button({
  variant = 'primary',
  icon,
  loading,
  fullWidth,
  children,
  className = '',
  disabled,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={`relative inline-flex items-center justify-center gap-2 px-5 py-2.5
        font-semibold rounded-xl transition-all duration-200 active:scale-[0.97]
        disabled:opacity-50 disabled:pointer-events-none
        ${variants[variant]}
        ${fullWidth ? 'w-full' : ''}
        ${className}`}
      {...props}
    >
      {loading ? (
        <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24" fill="none">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      ) : (
        icon
      )}
      {children}
    </button>
  );
}
