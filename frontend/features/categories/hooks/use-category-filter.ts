'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { type CategoryType } from '@/shared/lib/category-colors';

/**
 * useCategoryFilter Hook
 *
 * Manages category selection state synced with URL query params.
 * Returns the currently selected category and a function to select a new one.
 */
export function useCategoryFilter() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const selected = (searchParams.get('category') as CategoryType | null) || 'all';

  const select = (category: CategoryType | 'all') => {
    const params = new URLSearchParams(searchParams.toString());

    if (category === 'all') {
      params.delete('category');
    } else {
      params.set('category', category);
    }

    const queryString = params.toString();
    router.push(queryString ? `/?${queryString}` : '/');
  };

  return { selected, select };
}
