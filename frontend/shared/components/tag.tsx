import { type ComponentProps } from 'react';
import { Dot } from '@/shared/components/dot';
import { cn } from '@/shared/lib/cn';

interface TagProps extends ComponentProps<'div'> {
  /** Category name to display */
  name: string;
  /** Hex color code for the category */
  color: string;
  /** Whether to show the label text */
  showLabel?: boolean;
}

/**
 * Tag Component
 *
 * Displays a category with its colored dot and optional label.
 * Used in sidebars, cards, and category lists.
 */
export function Tag({ name, color, showLabel = true, className, ...props }: TagProps) {
  return (
    <div className={cn('inline-flex items-center gap-2', className)} {...props}>
      <Dot color={color} size="md" />
      {showLabel && (
        <span className="font-sans text-xs font-normal text-[rgb(var(--color-text-primary))]">
          {name}
        </span>
      )}
    </div>
  );
}
