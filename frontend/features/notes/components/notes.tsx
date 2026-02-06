import Image from 'next/image';
import { type ComponentProps, type ReactNode } from 'react';
import { Tag, Button, PlusIcon, Link, LogoutButton } from '@/shared/components';
import { cn } from '@/shared/lib/cn';
import type { NotePreview } from '@/shared/lib/api/schemas';

/**
 * Convert hex color to rgba with opacity
 */
function hexToRgba(hex: string, opacity: number): string {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
}

interface NotesConnectedProps {
  notes: NotePreview[];
  showHeaderOnly?: boolean;
  showContentOnly?: boolean;
}

/**
 * Notes Component (Server Component)
 *
 * Displays notes with filtering applied.
 */
function NotesConnected({ notes, showHeaderOnly, showContentOnly }: NotesConnectedProps) {
  // Header only mode
  if (showHeaderOnly) {
    return <NotesHeader />;
  }

  // Content only mode
  if (showContentOnly) {
    if (notes.length === 0) {
      return (
        <NotesEmpty
          illustration={
            <Image
              src="/coffee.png"
              alt="Coffee cup illustration"
              width={120}
              height={160}
              quality={90}
              className="w-auto h-auto"
            />
          }
          message="I'm just here waiting for your charming notes..."
        />
      );
    }

    return (
      <NotesGrid>
        {notes.map((note) => (
          <Link key={note.id} href={`/notes/${note.id}`}>
            <NotesCard
              title={note.title}
              content={note.content_preview}
              category={note.category}
              date={new Date(note.updated_at).toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric',
              })}
            />
          </Link>
        ))}
      </NotesGrid>
    );
  }

  // Full widget (default)
  return (
    <main className="flex-1 flex flex-col min-w-0">
      <NotesHeader />
      <div className="flex-1">
        {notes.length > 0 ? (
          <NotesGrid>
            {notes.map((note) => (
              <Link key={note.id} href={`/notes/${note.id}`}>
                <NotesCard
                  title={note.title}
                  content={note.content_preview}
                  category={note.category}
                  date={new Date(note.updated_at).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                  })}
                />
              </Link>
            ))}
          </NotesGrid>
        ) : (
          <NotesEmpty
            illustration={
              <Image
                src="/coffee.png"
                alt="Coffee cup illustration"
                width={120}
                height={160}
                quality={90}
                className="w-auto h-auto"
              />
            }
            message="I'm just here waiting for your charming notes..."
          />
        )}
      </div>
    </main>
  );
}

/**
 * NotesHeader Component
 *
 * Header with the "New Note" and logout buttons
 */
function NotesHeader() {
  return (
    <header className="flex items-center justify-between p-4">
      <div>{/* Placeholder for future user menu */}</div>
      <div className="flex items-center gap-3">
        <LogoutButton />
        <Link href="/notes/new">
          <Button variant="contained" className="flex items-center gap-2">
            <PlusIcon className="size-5" />
            <span>New Note</span>
          </Button>
        </Link>
      </div>
    </header>
  );
}

/**
 * NotesGrid Component
 *
 * Responsive grid layout for note cards
 */
interface NotesGridProps {
  children: ReactNode;
}

function NotesGrid({ children }: NotesGridProps) {
  return <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 p-4">{children}</div>;
}

/**
 * NotesCard Component
 *
 * Displays a note with category-based background color
 */
interface NotesCardProps extends ComponentProps<'article'> {
  title: string;
  content: ReactNode;
  category: { name: string; color: string } | null;
  date: string;
}

function NotesCard({ title, content, category, date, className, ...props }: NotesCardProps) {
  const categoryColor = category?.color || '#6366F1';

  return (
    <article
      className={cn(
        'w-full min-h-60 rounded-xl p-4',
        'flex flex-col items-start gap-3',
        'text-left',
        'border-[3px]',
        'shadow-sm',
        'transition-all duration-200',
        'cursor-pointer hover:shadow-lg hover:scale-[1.02]',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[rgb(var(--color-accent))] focus-visible:ring-offset-2',
        className
      )}
      style={{
        borderColor: categoryColor,
        backgroundColor: hexToRgba(categoryColor, 0.2), // 20% opacity
      }}
      {...props}
    >
      {/* Header: Date and Category */}
      <div className="flex flex-row items-start gap-2">
        <span className="font-sans text-xs font-bold text-[rgb(var(--color-text-primary))]">
          {date}
        </span>
        {category && <Tag name={category.name} color={category.color} showLabel />}
      </div>

      {/* Title */}
      <h3 className="font-serif text-2xl font-bold text-[rgb(var(--color-text-primary))]">
        {title}
      </h3>

      {/* Content Preview */}
      <div className="font-sans text-xs font-normal text-[rgb(var(--color-text-primary))] line-clamp-4">
        {content}
      </div>
    </article>
  );
}

/**
 * NotesEmpty Component
 *
 * Displays centered illustration with message when there are no notes
 */
interface NotesEmptyProps {
  illustration: ReactNode;
  message: string;
}

function NotesEmpty({ illustration, message }: NotesEmptyProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-96 px-4">
      {/* Illustration */}
      <div className="mb-8 flex items-center justify-center">{illustration}</div>

      {/* Message */}
      <p className="text-lg text-[rgb(var(--color-text-secondary))] text-center max-w-md font-medium">
        {message}
      </p>
    </div>
  );
}

// Export with compound component pattern
export const Notes = Object.assign(NotesConnected, {
  Header: NotesHeader,
  Grid: NotesGrid,
  Card: NotesCard,
  Empty: NotesEmpty,
});
