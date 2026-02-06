import { Suspense } from 'react';
import { cookies } from 'next/headers';
import { Sidebar } from '@/features/categories/components';
import { Notes } from '@/features/notes/components';
import { listCategories } from '@/shared/lib/api/categories';
import { listNotes } from '@/shared/lib/api/notes';

export const metadata = {
  title: 'Notes - NoteApp',
  description: 'Your personal notes dashboard',
};

interface DashboardPageProps {
  searchParams: Promise<{ category_id?: string }>;
}

/**
 * Dashboard Page
 * Main notes list view with category sidebar.
 * Supports filtering via ?category_id=... query param.
 */
export default async function DashboardPage({ searchParams }: DashboardPageProps) {
  const params = await searchParams;
  const categoryId = params.category_id ? parseInt(params.category_id, 10) : undefined;

  return (
    <div className="h-screen bg-[rgb(var(--color-background))] flex flex-col">
      <div className="mx-auto max-w-7xl w-full flex flex-col flex-1 min-h-0">
        {/* Row 1: Header with New Note button */}
        <div className="shrink-0">
          <Suspense fallback={<HeaderSkeleton />}>
            <NotesHeaderWrapper />
          </Suspense>
        </div>

        {/* Row 2: Sidebar + Notes Grid */}
        <div className="flex gap-8 lg:gap-12 flex-1 min-h-0">
          {/* Sidebar - fixed width, scrollable, hidden scrollbar, contained scroll */}
          <div className="shrink-0 overflow-y-auto overscroll-contain scrollbar-none">
            <Suspense fallback={<SidebarSkeleton />}>
              <SidebarData selectedCategoryId={categoryId} />
            </Suspense>
          </div>

          {/* Notes Grid - fills remaining space, scrollable, hidden scrollbar, contained scroll */}
          <div className="flex-1 min-w-0 overflow-y-auto overscroll-contain scrollbar-none">
            <Suspense fallback={<GridSkeleton />}>
              <NotesData categoryId={categoryId} />
            </Suspense>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Server Component to render the notes header
 */
async function NotesHeaderWrapper() {
  return <Notes.Header />;
}

/**
 * Server Component to fetch and display sidebar data
 */
async function SidebarData({ selectedCategoryId }: { selectedCategoryId?: number }) {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('access_token')?.value;

  let categories = [];
  try {
    categories = await listCategories(accessToken);
  } catch (error) {
    console.error('Failed to fetch categories:', error);
    // categories remains empty array
  }

  return <Sidebar categories={categories} selectedCategoryId={selectedCategoryId} />;
}

/**
 * Server Component to fetch and display notes data
 */
async function NotesData({ categoryId }: { categoryId?: number }) {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('access_token')?.value;

  let notes = [];
  try {
    const response = await listNotes({ category_id: categoryId, page_size: 100 }, accessToken);
    // Handle both paginated response and array response
    if (Array.isArray(response)) {
      notes = response;
    } else if (response && 'results' in response) {
      notes = response.results;
    }
  } catch (error) {
    console.error('Failed to fetch notes:', error);
    // notes remains empty array
  }

  return <Notes showContentOnly notes={notes} />;
}

/**
 * Loading skeletons for Suspense boundaries
 */
function HeaderSkeleton() {
  return (
    <div className="flex justify-end pb-6">
      <div className="h-12 w-32 bg-[rgb(var(--color-text-primary))]/10 rounded-full animate-pulse" />
    </div>
  );
}

function SidebarSkeleton() {
  return (
    <aside className="w-56 shrink-0 animate-pulse">
      <div className="space-y-2">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-10 bg-[rgb(var(--color-text-primary))]/10 rounded-lg" />
        ))}
      </div>
    </aside>
  );
}

function GridSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 p-1">
      {[...Array(6)].map((_, i) => (
        <div
          key={i}
          className="h-60 bg-[rgb(var(--color-text-primary))]/10 rounded-xl animate-pulse"
        />
      ))}
    </div>
  );
}
