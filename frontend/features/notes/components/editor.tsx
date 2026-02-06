'use client';

import { type ReactNode } from 'react';
import { Selector, IconButton, CloseIcon, QuoteIcon } from '@/shared/components';
import { Tag } from '@/shared/components';
import { cn } from '@/shared/lib/cn';
import { useNoteEditor } from '@/features/notes/hooks';
import { useCategoriesQuery } from '@/features/categories/hooks';

/**
 * Convert hex color to rgba with opacity
 */
function hexToRgba(hex: string, opacity: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

interface EditorConnectedProps {
  /** Note ID - 'new' for creating a new note */
  noteId: string;
  /** Initial note data - for editing existing notes */
  initialData?: {
    title: string;
    content: string;
    categoryId?: number;
    categoryName?: string;
    categoryColor?: string;
    lastEdited?: string;
  };
}

/**
 * Editor Component (Client Component)
 *
 * Self-contained component that manages note editing state.
 */
function EditorConnected({ noteId, initialData }: EditorConnectedProps) {
  const {
    title,
    setTitle,
    content,
    setContent,
    categoryId,
    categoryColor,
    selectCategory,
    isCategoryOpen,
    toggleCategoryDropdown,
    close,
    lastEdited,
  } = useNoteEditor(noteId, initialData);

  // Fetch categories for the dropdown
  const { data: categories = [], isLoading, isError } = useCategoriesQuery();

  // Find selected category for display
  const selectedCategory = categories.find((cat) => cat.id === categoryId);

  return (
    <EditorRoot
      categoryName={selectedCategory?.name || initialData?.categoryName || 'Random Thoughts'}
      categoryColor={selectedCategory?.color || categoryColor}
      title={title}
      content={content}
      lastEdited={lastEdited}
      onCategoryClick={toggleCategoryDropdown}
      isCategoryOpen={isCategoryOpen}
      onClose={close}
      onTitleChange={setTitle}
      onContentChange={setContent}
      categoryDropdown={
        isCategoryOpen && (
          <EditorDropdown
            categories={categories}
            selectedCategoryId={categoryId}
            onSelect={(id, color) => selectCategory(id, color)}
            isLoading={isLoading}
            isError={isError}
          />
        )
      }
    />
  );
}

/**
 * EditorRoot Component (Presentational)
 *
 * Full-page note editor with category selector, title, and content
 */
interface EditorRootProps {
  categoryName: string;
  categoryColor: string;
  title: string;
  content: string;
  lastEdited?: string;
  onCategoryClick?: () => void;
  isCategoryOpen?: boolean;
  onClose?: () => void;
  onTitleChange?: (title: string) => void;
  onContentChange?: (content: string) => void;
  categoryDropdown?: ReactNode;
}

function EditorRoot({
  categoryName,
  categoryColor,
  title,
  content,
  lastEdited,
  onCategoryClick,
  isCategoryOpen = false,
  onClose,
  onTitleChange,
  onContentChange,
  categoryDropdown,
}: EditorRootProps) {
  return (
    <div className="h-screen bg-[rgb(var(--color-background))] flex flex-col">
      <div className="mx-auto max-w-7xl w-full px-6 lg:px-8 flex flex-col flex-1 min-h-0">
        {/* Header - fixed */}
        <header className="shrink-0 flex items-center justify-between py-8">
          <div className="relative">
            <Selector
              category={{ name: categoryName, color: categoryColor }}
              isOpen={isCategoryOpen}
              onClick={onCategoryClick}
            />
            {categoryDropdown}
          </div>

          <button
            onClick={onClose}
            className="text-[rgb(var(--color-text-primary))] hover:opacity-70 transition-opacity"
            aria-label="Close editor"
          >
            <CloseIcon className="size-6" />
          </button>
        </header>

        {/* Editor Content - scrollable card, hidden scrollbar, contained scroll */}
        <main className="flex-1 min-h-0 pb-8">
          <div
            className={cn(
              'h-full rounded-xl p-6 lg:p-8 overflow-y-auto overscroll-contain scrollbar-none',
              'border-[3px]'
            )}
            style={{
              borderColor: categoryColor,
              backgroundColor: hexToRgba(categoryColor, 0.2), // 20% opacity
            }}
          >
            {/* Last Edited */}
            {lastEdited && (
              <div className="flex justify-end mb-4">
                <span className="text-sm text-[rgb(var(--color-text-secondary))]">
                  Last Edited: {lastEdited}
                </span>
              </div>
            )}

            {/* Title */}
            <input
              type="text"
              value={title}
              onChange={(e) => onTitleChange?.(e.target.value)}
              placeholder="Note Title"
              className={cn(
                'w-full bg-transparent border-none outline-none',
                'font-serif text-2xl font-bold',
                'text-[rgb(var(--color-text-primary))]',
                'placeholder:text-[rgb(var(--color-text-muted))]',
                'mb-4'
              )}
            />

            {/* Content */}
            <textarea
              value={content}
              onChange={(e) => onContentChange?.(e.target.value)}
              placeholder="Pour your heart out..."
              className={cn(
                'w-full min-h-96 bg-transparent border-none outline-none resize-none',
                'text-base',
                'text-[rgb(var(--color-text-primary))]',
                'placeholder:text-[rgb(var(--color-text-muted))]'
              )}
            />
          </div>
        </main>
      </div>

      {/* Quote Button */}
      <div className="fixed bottom-8 right-8">
        <IconButton icon={<QuoteIcon className="size-5" />} aria-label="Insert quote" />
      </div>
    </div>
  );
}

/**
 * EditorDropdown Component
 *
 * Dropdown menu for selecting note category
 */
interface EditorDropdownProps {
  categories: Array<{ id: number; name: string; color: string }>;
  selectedCategoryId?: number;
  onSelect: (id: number, color: string) => void;
  isLoading?: boolean;
  isError?: boolean;
}

function EditorDropdown({
  categories,
  selectedCategoryId,
  onSelect,
  isLoading,
  isError,
}: EditorDropdownProps) {
  return (
    <div className="absolute top-full left-0 mt-2 w-full min-w-48 bg-[rgb(var(--color-surface))] rounded-lg shadow-lg z-50 overflow-hidden border border-[rgb(var(--color-accent))]">
      {isLoading ? (
        <div className="px-4 py-3 text-sm text-[rgb(var(--color-text-secondary))]">
          Loading categories...
        </div>
      ) : isError ? (
        <div className="px-4 py-3 text-sm text-red-500">Failed to load categories</div>
      ) : categories.length === 0 ? (
        <div className="px-4 py-3 text-sm text-[rgb(var(--color-text-secondary))]">
          No categories available
        </div>
      ) : (
        categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => onSelect(cat.id, cat.color)}
            className={cn(
              'w-full px-4 py-2 flex items-center gap-2',
              'text-left transition-colors duration-200',
              'hover:bg-[rgb(var(--color-accent))]/20',
              selectedCategoryId === cat.id && 'bg-[rgb(var(--color-accent))]/10'
            )}
          >
            <Tag name={cat.name} color={cat.color} showLabel />
          </button>
        ))
      )}
    </div>
  );
}

// Export with compound component pattern
export const Editor = Object.assign(EditorConnected, {
  Root: EditorRoot,
  Dropdown: EditorDropdown,
});
