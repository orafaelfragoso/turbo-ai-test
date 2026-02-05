'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { type CategoryType } from '@/shared/lib/category-colors';

/**
 * useNotesFilter Hook
 *
 * Manages notes filtering and navigation.
 * Reads category filter from URL query params.
 */
export function useNotesFilter() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const selectedCategory = searchParams.get('category') as CategoryType | null;

  const openNote = (id: string) => {
    router.push(`/notes/${id}`);
  };

  const createNote = () => {
    router.push('/notes/new');
  };

  return { selectedCategory, openNote, createNote };
}
