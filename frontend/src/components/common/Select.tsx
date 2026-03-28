import { type SelectHTMLAttributes, forwardRef } from 'react';

interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  options: { value: string; label: string }[];
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ label, error, options, className = '', ...props }, ref) => {
    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label className="text-sm font-medium text-slate-300" htmlFor={props.id}>
            {label}
          </label>
        )}
        <select
          ref={ref}
          className={`w-full px-4 py-3 bg-slate-800/60 border border-white/10 rounded-xl text-white
            focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500/50
            transition-all duration-200 appearance-none cursor-pointer
            ${error ? 'border-rose-500/50 focus:ring-rose-500/50' : ''}
            ${className}`}
          {...props}
        >
          {options.map((opt) => (
            <option key={opt.value} value={opt.value} className="bg-slate-800 text-white">
              {opt.label}
            </option>
          ))}
        </select>
        {error && <p className="text-xs text-rose-400 mt-0.5">{error}</p>}
      </div>
    );
  }
);

Select.displayName = 'Select';
export default Select;
