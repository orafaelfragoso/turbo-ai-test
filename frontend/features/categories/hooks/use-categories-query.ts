'use client';

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  listCategoriesClient,
  getCategoryClient,
  createCategoryClient,
  updateCategoryClient,
  deleteCategoryClient,
} from '@/shared/lib/api/categories';
import { queryKeys } from '@/shared/lib/api/query-keys';
import type { CategoryInput } from '@/shared/lib/api/schemas';

/**
 * Hook to fetch all categories
 */
export function useCategoriesQuery() {
  return useQuery({
    queryKey: queryKeys.categories.list(),
    queryFn: () => listCategoriesClient(),
  });
}

/**
 * Hook to fetch a single category
 */
export function useCategoryQuery(id: number) {
  return useQuery({
    queryKey: queryKeys.categories.detail(id),
    queryFn: () => getCategoryClient(id),
    enabled: !!id,
  });
}

/**
 * Hook to create a new category
 */
export function useCreateCategoryMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CategoryInput) => createCategoryClient(data),
    onSuccess: () => {
      // Invalidate categories list to refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.categories.lists() });
    },
  });
}

/**
 * Hook to update a category
 */
export function useUpdateCategoryMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<CategoryInput> }) =>
      updateCategoryClient(id, data),
    onSuccess: (updatedCategory) => {
      // Update the specific category in cache
      queryClient.setQueryData(queryKeys.categories.detail(updatedCategory.id), updatedCategory);
      // Invalidate list to refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.categories.lists() });
    },
  });
}

/**
 * Hook to delete a category
 */
export function useDeleteCategoryMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => deleteCategoryClient(id),
    onSuccess: (_, deletedId) => {
      // Remove from cache
      queryClient.removeQueries({ queryKey: queryKeys.categories.detail(deletedId) });
      // Invalidate list to refetch
      queryClient.invalidateQueries({ queryKey: queryKeys.categories.lists() });
      // Invalidate notes since category deletion affects notes
      queryClient.invalidateQueries({ queryKey: queryKeys.notes.lists() });
    },
  });
}
