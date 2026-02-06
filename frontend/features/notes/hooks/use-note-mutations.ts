'use client';

import { useMutation, useQueryClient } from '@tanstack/react-query';
import { createNoteClient, updateNoteClient, deleteNoteClient } from '@/shared/lib/api/notes';
import { queryKeys } from '@/shared/lib/api/query-keys';
import type { NoteInput } from '@/shared/lib/api/schemas';

/**
 * Hook to create a new note
 */
export function useCreateNoteMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: NoteInput) => createNoteClient(data),
    onSuccess: () => {
      // Invalidate notes lists to refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.notes.lists() });
      // Invalidate categories to update note counts
      queryClient.invalidateQueries({ queryKey: queryKeys.categories.lists() });
    },
  });
}

/**
 * Hook to update a note (for auto-save)
 */
export function useUpdateNoteMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<NoteInput> }) =>
      updateNoteClient(id, data),
    onSuccess: (updatedNote) => {
      // Update the specific note in cache
      queryClient.setQueryData(queryKeys.notes.detail(updatedNote.id), updatedNote);
      // Invalidate lists to refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.notes.lists() });
      // Invalidate categories if category changed
      queryClient.invalidateQueries({ queryKey: queryKeys.categories.lists() });
    },
  });
}

/**
 * Hook to delete a note
 */
export function useDeleteNoteMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteNoteClient(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: queryKeys.notes.detail(deletedId) });
      // Invalidate lists to refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.notes.lists() });
      // Invalidate categories to update note counts
      queryClient.invalidateQueries({ queryKey: queryKeys.categories.lists() });
    },
  });
}
