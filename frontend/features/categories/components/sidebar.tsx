'use client';

import { type CategoryType, categoryNames } from '@/shared/lib/category-colors';
import { Tag } from '@/shared/components';
import { cn } from '@/shared/lib/cn';
import { useCategoryFilter } from '@/features/categories/hooks';

// Sample categories data - in real app, this would come from API
const categories: { category: CategoryType; count: number }[] = [
  { category: 'random-thoughts', count: 3 },
  { category: 'school', count: 3 },
  { category: 'personal', count: 1 },
];

/**
 * Sidebar Component (Connected)
 *
 * Self-contained component that manages category selection state
 * and syncs with URL query params.
 */
function SidebarConnected() {
  const { selected, select } = useCategoryFilter();

  return (
    <SidebarRoot
      categories={categories}
      selectedCategory={selected}
      onSelectCategory={select}
    />
  );
}

/**
 * SidebarRoot Component (Presentational)
 *
 * Displays a list of categories with note counts and allows filtering.
 */
interface SidebarRootProps {
  /** Array of categories with their note counts */
  categories: { category: CategoryType; count: number }[];
  /** Currently selected category (undefined for "All Categories") */
  selectedCategory?: CategoryType | 'all';
  /** Callback when a category is selected */
  onSelectCategory?: (category: CategoryType | 'all') => void;
}

function SidebarRoot({ categories, selectedCategory = 'all', onSelectCategory }: SidebarRootProps) {
  return (
    <aside className="w-56 shrink-0 py-4">
      <nav className="flex flex-col gap-1">
        {/* All Categories */}
        <SidebarItem
          label="All Categories"
          isSelected={selectedCategory === 'all'}
          onClick={() => onSelectCategory?.('all')}
        />

        {/* Individual Categories */}
        {categories.map(({ category, count }) => (
          <SidebarItem
            key={category}
            category={category}
            label={categoryNames[category]}
            count={count}
            isSelected={selectedCategory === category}
            onClick={() => onSelectCategory?.(category)}
          />
        ))}
      </nav>
    </aside>
  );
}

/**
 * SidebarItem Component
 *
 * Generic item that handles both header and category items.
 */
interface SidebarItemProps {
  /** Display label */
  label: string;
  /** Optional count to display */
  count?: number;
  /** Optional category for tag display */
  category?: CategoryType;
  /** Whether this item is selected */
  isSelected?: boolean;
  /** Click handler */
  onClick?: () => void;
}

function SidebarItem({ label, count, category, isSelected, onClick }: SidebarItemProps) {
  // Header style (no hover, always bold) when no category is provided
  const isHeader = !category;

  return (
    <button
      onClick={onClick}
      className={cn(
        'flex items-center gap-2',
        'w-full px-4 py-2',
        'transition-colors duration-200',
        'text-left rounded',
        'focus-visible:outline-none',
        !isHeader && 'hover:bg-[rgb(var(--color-accent))]/20'
      )}
    >
      {category ? (
        <>
          <Tag category={category} showLabel className={isSelected ? '[&>span]:font-bold' : ''} />
          <div className="flex-1" />
          {count !== undefined && (
            <span
              className={cn(
                'font-sans text-xs text-[rgb(var(--color-text-primary))]',
                isSelected ? 'font-bold' : 'font-normal'
              )}
            >
              {count}
            </span>
          )}
        </>
      ) : (
        <span className="font-sans text-xs font-bold text-[rgb(var(--color-text-primary))]">
          {label}
        </span>
      )}
    </button>
  );
}

// Export with compound component pattern
export const Sidebar = Object.assign(SidebarConnected, {
  Root: SidebarRoot,
  Item: SidebarItem,
});
