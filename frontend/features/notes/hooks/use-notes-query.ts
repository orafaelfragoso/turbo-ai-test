'use client';

import { useQuery } from '@tanstack/react-query';
import { listNotesClient, type ListNotesParams } from '@/shared/lib/api/notes';
import { queryKeys } from '@/shared/lib/api/query-keys';

/**
 * Hook to fetch paginated notes list with optional filters
 */
export function useNotesQuery(params?: ListNotesParams) {
  return useQuery({
    queryKey: queryKeys.notes.list(params),
    queryFn: () => listNotesClient(params),
  });
}
