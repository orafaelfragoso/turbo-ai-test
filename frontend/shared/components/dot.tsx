import { type ComponentProps } from 'react';
import { cn } from '@/shared/lib/cn';

interface DotProps extends ComponentProps<'span'> {
  /** Hex color code for the category */
  color: string;
  /** Size of the dot */
  size?: 'sm' | 'md';
}

/**
 * Dot Component
 *
 * A small colored circle indicator representing a category.
 * Used in tags, selectors, and cards.
 */
export function Dot({ color, size = 'sm', className, ...props }: DotProps) {
  const sizeClass = size === 'md' ? 'size-3' : 'size-2.5';

  return (
    <span
      className={cn('inline-block rounded-full shrink-0', sizeClass, className)}
      style={{ backgroundColor: color }}
      aria-hidden="true"
      {...props}
    />
  );
}
