/**
 * Utility for merging class names
 * Simple implementation for combining Tailwind classes
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}
