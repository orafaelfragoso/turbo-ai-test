import { z } from 'zod';
import { apiRequest, apiRequestClient } from './client';
import { categorySchema, type Category, type CategoryInput } from './schemas';

/**
 * List all categories for the authenticated user
 */
export async function listCategories(token?: string): Promise<Category[]> {
  return apiRequest('/api/categories/', {
    method: 'GET',
    schema: z.array(categorySchema),
    token,
  });
}

/**
 * List all categories (client-side)
 */
export async function listCategoriesClient(): Promise<Category[]> {
  return apiRequestClient('/api/categories/', {
    method: 'GET',
    schema: z.array(categorySchema),
  });
}

/**
 * Get a single category
 */
export async function getCategory(id: number, token?: string): Promise<Category> {
  return apiRequest(`/api/categories/${id}/`, {
    method: 'GET',
    schema: categorySchema,
    token,
  });
}

/**
 * Get a single category (client-side)
 */
export async function getCategoryClient(id: number): Promise<Category> {
  return apiRequestClient(`/api/categories/${id}/`, {
    method: 'GET',
    schema: categorySchema,
  });
}

/**
 * Create a new category
 */
export async function createCategory(data: CategoryInput, token?: string): Promise<Category> {
  return apiRequest('/api/categories/', {
    method: 'POST',
    schema: categorySchema,
    token,
    body: JSON.stringify(data),
  });
}

/**
 * Create a new category (client-side)
 */
export async function createCategoryClient(data: CategoryInput): Promise<Category> {
  return apiRequestClient('/api/categories/', {
    method: 'POST',
    schema: categorySchema,
    body: JSON.stringify(data),
  });
}

/**
 * Update a category
 */
export async function updateCategory(
  id: number,
  data: Partial<CategoryInput>,
  token?: string
): Promise<Category> {
  return apiRequest(`/api/categories/${id}/`, {
    method: 'PATCH',
    schema: categorySchema,
    token,
    body: JSON.stringify(data),
  });
}

/**
 * Update a category (client-side)
 */
export async function updateCategoryClient(
  id: number,
  data: Partial<CategoryInput>
): Promise<Category> {
  return apiRequestClient(`/api/categories/${id}/`, {
    method: 'PATCH',
    schema: categorySchema,
    body: JSON.stringify(data),
  });
}

/**
 * Delete a category
 */
export async function deleteCategory(id: number, token?: string): Promise<void> {
  return apiRequest(`/api/categories/${id}/`, {
    method: 'DELETE',
    schema: z.undefined(),
    token,
  });
}

/**
 * Delete a category (client-side)
 */
export async function deleteCategoryClient(id: number): Promise<void> {
  return apiRequestClient(`/api/categories/${id}/`, {
    method: 'DELETE',
    schema: z.undefined(),
  });
}
