import { type ComponentProps } from 'react';
import { type CategoryType, getCategoryDotClass } from '@/shared/lib/category-colors';
import { cn } from '@/shared/lib/cn';

interface DotProps extends ComponentProps<'span'> {
  category: CategoryType;
  size?: 'sm' | 'md';
}

/**
 * Dot Component
 *
 * A small colored circle indicator representing a category.
 * Used in tags, selectors, and cards.
 */
export function Dot({ category, size = 'sm', className, ...props }: DotProps) {
  return (
    <span
      className={cn(
        'inline-block rounded-full shrink-0 size-2.5',
        getCategoryDotClass(category),
        className
      )}
      aria-hidden="true"
      {...props}
    />
  );
}
