import { Suspense } from 'react';
import { Sidebar } from '@/features/categories/components';
import { Notes } from '@/features/notes/components';

export const metadata = {
  title: 'Notes - NoteApp',
  description: 'Your personal notes dashboard',
};

/**
 * Dashboard Page
 * Main notes list view with category sidebar.
 * Supports filtering via ?category=... query param.
 */
export default function DashboardPage() {
  return (
    <div className="h-screen bg-[rgb(var(--color-background))] flex flex-col">
      <div className="mx-auto max-w-7xl w-full flex flex-col flex-1 min-h-0">
        {/* Row 1: Header with New Note button */}
        <div className="shrink-0">
          <Suspense fallback={<HeaderSkeleton />}>
            <Notes showHeaderOnly />
          </Suspense>
        </div>

        {/* Row 2: Sidebar + Notes Grid */}
        <div className="flex gap-8 lg:gap-12 flex-1 min-h-0">
          {/* Sidebar - fixed width, scrollable, hidden scrollbar, contained scroll */}
          <div className="shrink-0 overflow-y-auto overscroll-contain scrollbar-none">
            <Suspense fallback={<SidebarSkeleton />}>
              <Sidebar />
            </Suspense>
          </div>

          {/* Notes Grid - fills remaining space, scrollable, hidden scrollbar, contained scroll */}
          <div className="flex-1 min-w-0 overflow-y-auto overscroll-contain scrollbar-none">
            <Suspense fallback={<GridSkeleton />}>
              <Notes showContentOnly />
            </Suspense>
          </div>
        </div>
      </div>
    </div>
  );
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
