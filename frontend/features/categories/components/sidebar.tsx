import { Tag } from '@/shared/components';
import { Link } from '@/shared/components';
import { cn } from '@/shared/lib/cn';
import type { Category } from '@/shared/lib/api/schemas';

/**
 * Sidebar Component (Server Component)
 *
 * Displays a list of categories with note counts and allows filtering via links.
 */
interface SidebarConnectedProps {
  categories: Category[];
  selectedCategoryId?: number;
}

function SidebarConnected({ categories, selectedCategoryId }: SidebarConnectedProps) {
  return <SidebarRoot categories={categories} selectedCategoryId={selectedCategoryId} />;
}

/**
 * SidebarRoot Component (Presentational)
 *
 * Displays a list of categories with their note counts and allows filtering.
 */
interface SidebarRootProps {
  /** Array of categories with their note counts */
  categories: Category[];
  /** Currently selected category ID (undefined for "All Categories") */
  selectedCategoryId?: number;
}

function SidebarRoot({ categories, selectedCategoryId }: SidebarRootProps) {
  const isAllSelected = selectedCategoryId === undefined;

  return (
    <aside className="w-56 shrink-0 py-4">
      <nav className="flex flex-col gap-1">
        {/* All Categories */}
        <Link href="/">
          <SidebarItem label="All Categories" isSelected={isAllSelected} />
        </Link>

        {/* Individual Categories */}
        {categories.map((category) => (
          <Link key={category.id} href={`/?category_id=${category.id}`}>
            <SidebarItem
              label={category.name}
              color={category.color}
              count={category.note_count}
              isSelected={selectedCategoryId === category.id}
            />
          </Link>
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
  /** Optional hex color code for category display */
  color?: string;
  /** Whether this item is selected */
  isSelected?: boolean;
}

function SidebarItem({ label, count, color, isSelected }: SidebarItemProps) {
  // Header style (no hover, always bold) when no color is provided
  const isHeader = !color;

  return (
    <div
      className={cn(
        'flex items-center gap-2',
        'w-full px-4 py-2',
        'transition-colors duration-200',
        'text-left rounded',
        'focus-visible:outline-none',
        !isHeader && 'hover:bg-[rgb(var(--color-accent))]/20'
      )}
    >
      {color ? (
        <>
          <Tag
            name={label}
            color={color}
            showLabel
            className={isSelected ? '[&>span]:font-bold' : ''}
          />
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
    </div>
  );
}

// Export with compound component pattern
export const Sidebar = Object.assign(SidebarConnected, {
  Root: SidebarRoot,
  Item: SidebarItem,
});
