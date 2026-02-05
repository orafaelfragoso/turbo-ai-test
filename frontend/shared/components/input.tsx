import { type ComponentProps, type ReactNode } from 'react';
import { cn } from '@/shared/lib/cn';

interface InputProps extends ComponentProps<'input'> {
  icon?: ReactNode;
}

/**
 * Input Component
 *
 * A stateless text/password input component.
 * Supports optional icon (typically for password visibility toggle).
 */
export function Input({ className, icon, type = 'text', ...props }: InputProps) {
  return (
    <div className="relative w-full">
      <input
        type={type}
        className={cn(
          'w-full px-4 py-3 rounded-md',
          'bg-transparent',
          'border border-[rgb(var(--color-accent))]',
          'text-[rgb(var(--color-text-primary))] placeholder:text-[rgb(var(--color-accent))]/60',
          'font-sans text-xs font-normal',
          'outline-none',
          'disabled:opacity-50 disabled:cursor-not-allowed',
          icon ? 'pr-12' : '',
          className
        )}
        {...props}
      />
      {icon && (
        <div className="absolute right-4 top-1/2 -translate-y-1/2 text-[rgb(var(--color-accent))]">
          {icon}
        </div>
      )}
    </div>
  );
}
