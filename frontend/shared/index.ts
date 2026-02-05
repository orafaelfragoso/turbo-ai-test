/**
 * Shared Module Barrel Export
 *
 * Main entry point for the shared design system.
 * Exports components, utilities, and types.
 */

// Components
export * from '@/shared/components';

// Utilities
export { cn } from '@/shared/lib/cn';
export {
  categoryColors,
  getCategoryColorClass,
  getCategoryTextColor,
  categoryNames,
  type CategoryType,
} from '@/shared/lib/category-colors';
