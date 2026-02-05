/**
 * Category Color Mapping Utility
 * Maps category slugs to their corresponding color values
 */

export type CategoryType = 'personal' | 'school' | 'random-thoughts' | 'drama';

/**
 * Category display names
 */
export const categoryNames: Record<CategoryType, string> = {
  'personal': 'Personal',
  'school': 'School',
  'random-thoughts': 'Random Thoughts',
  'drama': 'Drama',
} as const;

/**
 * Get category background color class for cards
 */
export function getCategoryColorClass(category: CategoryType): string {
  const colorMap: Record<CategoryType, string> = {
    'personal': 'bg-[rgb(var(--color-category-personal))]/20',
    'school': 'bg-[rgb(var(--color-category-accent))]/20',
    'random-thoughts': 'bg-[rgb(var(--color-category-thoughts))]/20',
    'drama': 'bg-[rgb(var(--color-category-school))]/20',
  };

  return colorMap[category];
}

/**
 * Get category border color class for cards
 */
export function getCategoryBorderClass(category: CategoryType): string {
  const colorMap: Record<CategoryType, string> = {
    'personal': 'border-[rgb(var(--color-category-personal))]',
    'school': 'border-[rgb(var(--color-category-accent))]',
    'random-thoughts': 'border-[rgb(var(--color-category-thoughts))]',
    'drama': 'border-[rgb(var(--color-category-school))]',
  };

  return colorMap[category];
}

/**
 * Get category dot color class
 */
export function getCategoryDotClass(category: CategoryType): string {
  const colorMap: Record<CategoryType, string> = {
    'personal': 'bg-[rgb(var(--color-category-personal))]',
    'school': 'bg-[rgb(var(--color-category-accent))]',
    'random-thoughts': 'bg-[rgb(var(--color-category-thoughts))]',
    'drama': 'bg-[rgb(var(--color-category-school))]',
  };

  return colorMap[category];
}
