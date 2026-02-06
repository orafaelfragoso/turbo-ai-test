import { type ComponentProps } from 'react';
import { cn } from '@/shared/lib/cn';

type ButtonVariant = 'contained' | 'blocked';

interface ButtonProps extends ComponentProps<'button'> {
  variant?: ButtonVariant;
}

/**
 * Button Component
 *
 * A stateless button component with two variants:
 * - contained: For icon buttons (inline width)
 * - blocked: For form buttons (full width)
 */
export function Button({
  variant = 'blocked',
  className,
  children,
  type = 'button',
  ...props
}: ButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        'px-4 py-3 rounded-full underline-none',
        'font-sans text-base font-bold',
        'bg-transparent border border-[rgb(var(--color-accent))]',
        'text-[rgb(var(--color-accent))]',
        'transition-colors duration-200',
        'hover:bg-[rgb(var(--color-accent))]/20',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variant === 'blocked' && 'w-full',
        className
      )}
      {...props}
    >
      {children}
    </button>
  );
}
