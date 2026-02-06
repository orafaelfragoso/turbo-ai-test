'use client';

import { useQuery } from '@tanstack/react-query';
import { getNoteClient } from '@/shared/lib/api/notes';
import { queryKeys } from '@/shared/lib/api/query-keys';

/**
 * Hook to fetch a single note
 */
export function useNoteQuery(id: string) {
  return useQuery({
    queryKey: queryKeys.notes.detail(id),
    queryFn: () => getNoteClient(id),
    enabled: !!id && id !== 'new',
  });
}
