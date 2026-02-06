'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useCreateNoteMutation, useUpdateNoteMutation } from '@/features/notes/hooks';

interface NoteData {
  title: string;
  content: string;
  categoryId?: number;
  categoryName?: string;
  categoryColor?: string;
  lastEdited?: string;
}

const defaultNote: NoteData = {
  title: '',
  content: '',
  categoryId: undefined,
  categoryName: undefined,
  categoryColor: '#6366F1',
  lastEdited: undefined,
};

/**
 * useNoteEditor Hook
 *
 * Manages note editing state including title, content, category selection.
 * Handles category dropdown state, navigation, and auto-save via mutations.
 */
export function useNoteEditor(noteId: string, initialData?: NoteData) {
  const router = useRouter();
  const isNewNote = noteId === 'new';

  const noteData = initialData || defaultNote;

  const [title, setTitle] = useState(noteData.title);
  const [content, setContent] = useState(noteData.content);
  const [categoryId, setCategoryId] = useState<number | undefined>(noteData.categoryId);
  const [categoryColor, setCategoryColor] = useState<string>(noteData.categoryColor || '#6366F1');
  const [isCategoryOpen, setIsCategoryOpen] = useState(false);
  const [createdNoteId, setCreatedNoteId] = useState<string | null>(null);

  const createNoteMutation = useCreateNoteMutation();
  const updateNoteMutation = useUpdateNoteMutation();

  // Track if we're currently creating a note to avoid duplicate creations
  const isCreatingRef = useRef(false);

  // Auto-save logic for existing notes (debounced)
  useEffect(() => {
    const currentNoteId = createdNoteId || noteId;

    // Skip if it's a new note that hasn't been created yet
    if (isNewNote && !createdNoteId) return;

    const timeout = setTimeout(() => {
      // Only save if there's content to save and we have a note ID
      if ((title || content) && currentNoteId && currentNoteId !== 'new') {
        updateNoteMutation.mutate({
          id: currentNoteId,
          data: {
            title,
            content,
            category_id: categoryId || null,
          },
        });
      }
    }, 1000); // 1 second debounce

    return () => clearTimeout(timeout);
  }, [title, content, categoryId, createdNoteId]); // eslint-disable-line react-hooks/exhaustive-deps

  // Auto-create note for new notes when user starts typing (debounced)
  useEffect(() => {
    if (!isNewNote || createdNoteId || isCreatingRef.current) return;

    // Only create if there's actual content
    if (!title && !content) return;

    const timeout = setTimeout(() => {
      if (isCreatingRef.current) return;

      isCreatingRef.current = true;
      createNoteMutation.mutate(
        {
          title,
          content,
          category_id: categoryId || null,
        },
        {
          onSuccess: (createdNote) => {
            setCreatedNoteId(createdNote.id);
            // Navigate to the note detail page
            router.push(`/notes/${createdNote.id}`);
            isCreatingRef.current = false;
          },
          onError: (error) => {
            console.error('Failed to create note:', error);
            isCreatingRef.current = false;
          },
        }
      );
    }, 500); // 500ms debounce before creating

    return () => clearTimeout(timeout);
  }, [title, content, categoryId, isNewNote, createdNoteId, router]); // eslint-disable-line react-hooks/exhaustive-deps

  const close = () => {
    router.push('/');
  };

  const selectCategory = (newCategoryId: number, newCategoryColor: string) => {
    setCategoryId(newCategoryId);
    setCategoryColor(newCategoryColor);
    setIsCategoryOpen(false);
  };

  const toggleCategoryDropdown = () => {
    setIsCategoryOpen(!isCategoryOpen);
  };

  return {
    title,
    setTitle,
    content,
    setContent,
    categoryId,
    categoryColor,
    selectCategory,
    isCategoryOpen,
    toggleCategoryDropdown,
    close,
    lastEdited: isNewNote ? undefined : noteData.lastEdited,
  };
}
