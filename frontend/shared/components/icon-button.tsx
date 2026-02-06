import { type ComponentProps, type ReactNode } from 'react';
import { cn } from '@/shared/lib/cn';

interface IconButtonProps extends ComponentProps<'button'> {
  icon: ReactNode;
  'aria-label': string;
}

/**
 * IconButton Component
 *
 * A minimal icon-only button for actions like close, delete, etc.
 * Requires aria-label for accessibility.
 *
 * @example
 * <IconButton icon={<XIcon />} aria-label="Close" onClick={handleClose} />
 */
export function IconButton({ icon, className, type = 'button', ...props }: IconButtonProps) {
  return (
    <button
      type={type}
      className={cn(
        'size-10 rounded-full underline-none',
        'flex items-center justify-center',
        'bg-[rgb(var(--color-text-primary))]',
        'text-[rgb(var(--color-surface))]',
        'transition-all duration-200',
        'hover:opacity-90',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[rgb(var(--color-accent))] focus-visible:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        className
      )}
      {...props}
    >
      {icon}
    </button>
  );
}
