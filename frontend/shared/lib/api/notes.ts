import { z } from 'zod';
import { apiRequest, apiRequestClient } from './client';
import {
  noteDetailSchema,
  paginatedNotesSchema,
  type NoteDetail,
  type PaginatedNotes,
  type NoteInput,
} from './schemas';

export interface ListNotesParams {
  category_id?: number;
  search?: string;
  page?: number;
  page_size?: number;
}

/**
 * List notes with optional filtering and pagination
 */
export async function listNotes(params?: ListNotesParams, token?: string): Promise<PaginatedNotes> {
  const searchParams = new URLSearchParams();
  if (params?.category_id !== undefined)
    searchParams.set('category_id', params.category_id.toString());
  if (params?.search) searchParams.set('search', params.search);
  if (params?.page) searchParams.set('page', params.page.toString());
  if (params?.page_size) searchParams.set('page_size', params.page_size.toString());

  const queryString = searchParams.toString();
  const endpoint = queryString ? `/api/notes/?${queryString}` : '/api/notes/';

  return apiRequest(endpoint, {
    method: 'GET',
    schema: paginatedNotesSchema,
    token,
  });
}

/**
 * List notes (client-side)
 */
export async function listNotesClient(params?: ListNotesParams): Promise<PaginatedNotes> {
  const searchParams = new URLSearchParams();
  if (params?.category_id !== undefined)
    searchParams.set('category_id', params.category_id.toString());
  if (params?.search) searchParams.set('search', params.search);
  if (params?.page) searchParams.set('page', params.page.toString());
  if (params?.page_size) searchParams.set('page_size', params.page_size.toString());

  const queryString = searchParams.toString();
  const endpoint = queryString ? `/api/notes/?${queryString}` : '/api/notes/';

  return apiRequestClient(endpoint, {
    method: 'GET',
    schema: paginatedNotesSchema,
  });
}

/**
 * Get a single note
 */
export async function getNote(id: string, token?: string): Promise<NoteDetail> {
  return apiRequest(`/api/notes/${id}/`, {
    method: 'GET',
    schema: noteDetailSchema,
    token,
  });
}

/**
 * Get a single note (client-side)
 */
export async function getNoteClient(id: string): Promise<NoteDetail> {
  return apiRequestClient(`/api/notes/${id}/`, {
    method: 'GET',
    schema: noteDetailSchema,
  });
}

/**
 * Create a new note
 */
export async function createNote(data: NoteInput, token?: string): Promise<NoteDetail> {
  return apiRequest('/api/notes/', {
    method: 'POST',
    schema: noteDetailSchema,
    token,
    body: JSON.stringify(data),
  });
}

/**
 * Create a new note (client-side)
 */
export async function createNoteClient(data: NoteInput): Promise<NoteDetail> {
  return apiRequestClient('/api/notes/', {
    method: 'POST',
    schema: noteDetailSchema,
    body: JSON.stringify(data),
  });
}

/**
 * Update a note
 */
export async function updateNote(
  id: string,
  data: Partial<NoteInput>,
  token?: string
): Promise<NoteDetail> {
  return apiRequest(`/api/notes/${id}/`, {
    method: 'PATCH',
    schema: noteDetailSchema,
    token,
    body: JSON.stringify(data),
  });
}

/**
 * Update a note (client-side)
 */
export async function updateNoteClient(id: string, data: Partial<NoteInput>): Promise<NoteDetail> {
  return apiRequestClient(`/api/notes/${id}/`, {
    method: 'PATCH',
    schema: noteDetailSchema,
    body: JSON.stringify(data),
  });
}

/**
 * Delete a note
 */
export async function deleteNote(id: string, token?: string): Promise<void> {
  return apiRequest(`/api/notes/${id}/`, {
    method: 'DELETE',
    schema: z.undefined(),
    token,
  });
}

/**
 * Delete a note (client-side)
 */
export async function deleteNoteClient(id: string): Promise<void> {
  return apiRequestClient(`/api/notes/${id}/`, {
    method: 'DELETE',
    schema: z.undefined(),
  });
}
