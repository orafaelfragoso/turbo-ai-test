import { type ComponentProps } from 'react';
import { Tag } from '@/shared/components/tag';
import { cn } from '@/shared/lib/cn';

interface SelectorProps extends Omit<ComponentProps<'button'>, 'type'> {
  category: { name: string; color: string };
  isOpen?: boolean;
}

/**
 * Selector Component
 *
 * A dropdown trigger button displaying the current category with a chevron.
 * Used in editors and forms for category selection.
 */
export function Selector({ category, isOpen = false, className, ...props }: SelectorProps) {
  return (
    <button
      type="button"
      className={cn(
        'flex items-center gap-2 justify-between',
        'px-4 py-2 rounded-md',
        'border border-[rgb(var(--color-accent))]',
        'bg-transparent',
        'transition-all duration-200',
        'hover:bg-[rgb(var(--color-accent))]/20',
        'focus-visible:outline-none',
        'min-w-48',
        className
      )}
      {...props}
    >
      <Tag name={category.name} color={category.color} />
      <ChevronIcon isOpen={isOpen} />
    </button>
  );
}

/**
 * ChevronIcon Component (internal)
 * Simple chevron that rotates based on open state
 */
function ChevronIcon({ isOpen }: { isOpen: boolean }) {
  return (
    <svg
      className={cn('size-3', isOpen && 'rotate-180')}
      fill="none"
      viewBox="0 0 24 24"
      aria-hidden="true"
    >
      <path
        d="M4 8L12 16L20 8"
        stroke="rgb(var(--color-accent))"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/**
 * SelectorDropdown Component
 *
 * The dropdown menu for category selection
 */
interface SelectorDropdownProps {
  categories: Array<{ id: number; name: string; color: string }>;
  onSelect: (id: number, name: string, color: string) => void;
  className?: string;
}

export function SelectorDropdown({ categories, onSelect, className }: SelectorDropdownProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-start',
        'bg-[rgb(var(--color-surface))] rounded-lg',
        'overflow-hidden',
        className
      )}
    >
      {categories.map((category) => (
        <button
          key={category.id}
          type="button"
          onClick={() => onSelect(category.id, category.name, category.color)}
          className={cn(
            'flex items-center gap-2',
            'w-full px-4 py-4',
            'transition-colors duration-200',
            'hover:bg-[rgb(var(--color-accent))]/20'
          )}
        >
          <Tag name={category.name} color={category.color} />
        </button>
      ))}
    </div>
  );
}
