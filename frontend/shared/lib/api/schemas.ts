import { z } from 'zod';

/**
 * Category Schema
 * Matches backend Category model
 */
export const categorySchema = z.object({
  id: z.number(),
  name: z.string(),
  color: z.string(),
  note_count: z.number(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type Category = z.infer<typeof categorySchema>;

/**
 * Category Nested Schema (for note responses)
 * Matches CategoryNestedSerializer from backend - only includes id, name, color
 */
export const categoryNestedSchema = z.object({
  id: z.number(),
  name: z.string(),
  color: z.string(),
});

export type CategoryNested = z.infer<typeof categoryNestedSchema>;

/**
 * Note Preview Schema (for list views)
 * Used in paginated note lists
 */
export const notePreviewSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  content_preview: z.string(),
  category: categoryNestedSchema.nullable(),
  updated_at: z.string(),
});

export type NotePreview = z.infer<typeof notePreviewSchema>;

/**
 * Note Detail Schema (full note)
 * Used for single note views and editor
 */
export const noteDetailSchema = z.object({
  id: z.string().uuid(),
  title: z.string(),
  content: z.string(),
  category: categoryNestedSchema.nullable(),
  created_at: z.string(),
  updated_at: z.string(),
});

export type NoteDetail = z.infer<typeof noteDetailSchema>;

/**
 * Paginated Notes Response
 */
export const paginatedNotesSchema = z.object({
  count: z.number(),
  next: z.string().nullable(),
  previous: z.string().nullable(),
  results: z.array(notePreviewSchema),
});

export type PaginatedNotes = z.infer<typeof paginatedNotesSchema>;

/**
 * Note Create/Update Input
 */
export const noteInputSchema = z.object({
  title: z.string().max(255).optional(),
  content: z.string().max(100000).optional(),
  category_id: z.number().nullable().optional(),
});

export type NoteInput = z.infer<typeof noteInputSchema>;

/**
 * Category Create/Update Input
 */
export const categoryInputSchema = z.object({
  name: z.string().min(1).max(100),
  color: z.string().regex(/^#[0-9A-Fa-f]{6}$/),
});

export type CategoryInput = z.infer<typeof categoryInputSchema>;

/**
 * API Error Response
 */
export const apiErrorSchema = z.object({
  detail: z.string().optional(),
  message: z.string().optional(),
});

export type ApiError = z.infer<typeof apiErrorSchema>;
