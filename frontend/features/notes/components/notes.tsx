'use client';

import Image from 'next/image';
import { type ComponentProps, type ReactNode } from 'react';
import { type CategoryType, getCategoryColorClass, getCategoryBorderClass } from '@/shared/lib/category-colors';
import { Tag, Button, PlusIcon } from '@/shared/components';
import { cn } from '@/shared/lib/cn';
import { useNotesFilter } from '@/features/notes/hooks';

// Sample notes data - in real app, this would come from API
const sampleNotes = [
  {
    id: '1',
    title: 'Grocery List',
    content: (
      <ul className="list-disc list-inside space-y-1">
        <li>Milk</li>
        <li>Eggs</li>
        <li>Bread</li>
        <li>Bananas</li>
        <li>Spinach</li>
      </ul>
    ),
    category: 'random-thoughts' as CategoryType,
    date: 'today',
  },
  {
    id: '2',
    title: 'Meeting with Team',
    content:
      'Discuss project timeline and milestones. Review budget and resource allocation. Address any blockers and plan next steps.',
    category: 'school' as CategoryType,
    date: 'yesterday',
  },
  {
    id: '3',
    title: 'Note Title',
    content: 'Note content...',
    category: 'school' as CategoryType,
    date: 'July 16',
  },
  {
    id: '4',
    title: 'Vacation Ideas',
    content: (
      <ul className="list-disc list-inside space-y-1">
        <li>Visit Bali for beaches and culture</li>
        <li>Explore the historic sites in Rome</li>
        <li>Go hiking in the Swiss Alps</li>
        <li>Relax in the hot springs of Iceland</li>
      </ul>
    ),
    category: 'random-thoughts' as CategoryType,
    date: 'July 15',
  },
  {
    id: '5',
    title: 'Note Title',
    content:
      'Lately, I\'ve been on a quest to discover new books to read. I\'ve come across several recommendations that have piqued my interest. "The Alchemist" by Paulo Coelho is at the top of my list, given its reputation as a life-changing read. I\'ve also heard great things about "Educated" by Tara Westover and "Becoming" by Michelle Obama. Each of thes...',
    category: 'personal' as CategoryType,
    date: 'June 12',
  },
  {
    id: '6',
    title:
      'A Deep and Contemplative Personal Reflection on the Multifaceted and Ever-Evolving Journey of Life',
    content: "Life has been a whirlwind of events and emotions lately. I've been juggling work,",
    category: 'random-thoughts' as CategoryType,
    date: 'June 11',
  },
  {
    id: '7',
    title: 'Project X Updates',
    content:
      'Finalized design mockups and received approval from stakeholders. Began development on the front-end. Backend integration is scheduled for next week. Team is on track to meet the deadline.',
    category: 'school' as CategoryType,
    date: 'June 10',
  },
];

interface NotesConnectedProps {
  showHeaderOnly?: boolean;
  showContentOnly?: boolean;
}

/**
 * Notes Component (Connected)
 *
 * Self-contained component that manages notes data and filtering.
 */
function NotesConnected({ showHeaderOnly, showContentOnly }: NotesConnectedProps) {
  const { selectedCategory, openNote, createNote } = useNotesFilter();

  const filteredNotes =
    selectedCategory === null
      ? sampleNotes
      : sampleNotes.filter((note) => note.category === selectedCategory);

  // Header only mode
  if (showHeaderOnly) {
    return <NotesHeader onNewNote={createNote} />;
  }

  // Content only mode
  if (showContentOnly) {
    if (filteredNotes.length === 0) {
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
        {filteredNotes.map((note) => (
          <NotesCard
            key={note.id}
            title={note.title}
            content={note.content}
            category={note.category}
            date={note.date}
            onClick={() => openNote(note.id)}
          />
        ))}
      </NotesGrid>
    );
  }

  // Full widget (default)
  return (
    <main className="flex-1 flex flex-col min-w-0">
      <NotesHeader onNewNote={createNote} />
      <div className="flex-1">
        {filteredNotes.length > 0 ? (
          <NotesGrid>
            {filteredNotes.map((note) => (
              <NotesCard
                key={note.id}
                title={note.title}
                content={note.content}
                category={note.category}
                date={note.date}
                onClick={() => openNote(note.id)}
              />
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
 * Header with the "New Note" button
 */
interface NotesHeaderProps {
  onNewNote?: () => void;
}

function NotesHeader({ onNewNote }: NotesHeaderProps) {
  return (
    <header className="flex items-center justify-end p-4">
      <Button variant="contained" onClick={onNewNote} className="flex items-center gap-2">
        <PlusIcon className="size-5" />
        <span>New Note</span>
      </Button>
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
  category: CategoryType;
  date: string;
  onClick?: () => void;
}

function NotesCard({ title, content, category, date, onClick, className, ...props }: NotesCardProps) {
  const Component = onClick ? 'button' : 'article';

  return (
    <Component
      className={cn(
        'w-full min-h-60 rounded-xl p-4',
        'flex flex-col items-start gap-3',
        'text-left',
        'border-[3px]',
        'shadow-sm',
        'transition-all duration-200',
        getCategoryColorClass(category),
        getCategoryBorderClass(category),
        onClick && 'cursor-pointer hover:shadow-lg hover:scale-[1.02]',
        onClick &&
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[rgb(var(--color-accent))] focus-visible:ring-offset-2',
        className
      )}
      onClick={onClick}
      {...props}
    >
      {/* Header: Date and Category */}
      <div className="flex flex-row items-start gap-2">
        <span className="font-sans text-xs font-bold text-[rgb(var(--color-text-primary))]">{date}</span>
        <Tag category={category} showLabel />
      </div>

      {/* Title */}
      <h3 className="font-serif text-2xl font-bold text-[rgb(var(--color-text-primary))]">{title}</h3>

      {/* Content Preview */}
      <div className="font-sans text-xs font-normal text-[rgb(var(--color-text-primary))] line-clamp-4">
        {content}
      </div>
    </Component>
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
      <p className="text-lg text-[rgb(var(--color-text-secondary))] text-center max-w-md font-medium">{message}</p>
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
