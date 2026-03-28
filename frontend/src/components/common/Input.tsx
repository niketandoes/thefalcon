import { type InputHTMLAttributes, forwardRef } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, icon, className = '', ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label className="text-sm font-medium text-slate-300" htmlFor={props.id}>
            {label}
          </label>
        )}
        <div className="relative">
          {icon && (
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">
              {icon}
            </span>
          )}
          <input
            ref={ref}
            className={`w-full px-4 py-3 bg-slate-800/60 border border-white/10 rounded-xl text-white
              placeholder:text-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50
              focus:border-indigo-500/50 transition-all duration-200
              ${icon ? 'pl-10' : ''}
              ${error ? 'border-rose-500/50 focus:ring-rose-500/50' : ''}
              ${className}`}
            {...props}
          />
        </div>
        {error && <p className="text-xs text-rose-400 mt-0.5">{error}</p>}
      </div>
    );
  }
);

Input.displayName = 'Input';
export default Input;
