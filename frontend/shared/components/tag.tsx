import { type ComponentProps } from 'react';
import { type CategoryType, categoryNames } from '@/shared/lib/category-colors';
import { Dot } from '@/shared/components/dot';
import { cn } from '@/shared/lib/cn';

interface TagProps extends ComponentProps<'div'> {
  category: CategoryType;
  showLabel?: boolean;
}

/**
 * Tag Component
 *
 * Displays a category with its colored dot and optional label.
 * Used in sidebars, cards, and category lists.
 */
export function Tag({ category, showLabel = true, className, ...props }: TagProps) {
  return (
    <div className={cn('inline-flex items-center gap-2', className)} {...props}>
      <Dot category={category} size="md" />
      {showLabel && (
        <span className="font-sans text-xs font-normal text-[rgb(var(--color-text-primary))]">
          {categoryNames[category]}
        </span>
      )}
    </div>
  );
}
