/**
 * Category Color Utility
 * Uses hex colors directly from the backend for Tailwind classes
 */

/**
 * Legacy CategoryType for static color references
 * Used for UI components that need predefined colors
 */
export type CategoryType = 'personal' | 'school' | 'random-thoughts' | 'drama';

/**
 * Category display names (legacy)
 */
export const categoryNames: Record<CategoryType, string> = {
  personal: 'Personal',
  school: 'School',
  'random-thoughts': 'Random Thoughts',
  drama: 'Drama',
} as const;

/**
 * Get category background color class for cards from hex color
 * Uses the hex color directly from the backend
 */
export function getCategoryColorClass(color: string): string {
  // Use the hex color directly from backend with opacity
  return `bg-[${color}]/20`;
}

/**
 * Get category border color class for cards from hex color
 * Uses the hex color directly from the backend
 */
export function getCategoryBorderClass(color: string): string {
  // Use the hex color directly from backend
  return `border-[${color}]`;
}

/**
 * Get category dot color class from hex color
 * Uses the hex color directly from the backend
 */
export function getCategoryDotClass(color: string): string {
  // Use the hex color directly from backend
  return `bg-[${color}]`;
}
