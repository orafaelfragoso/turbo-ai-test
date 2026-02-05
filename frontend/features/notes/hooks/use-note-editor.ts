'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { type CategoryType } from '@/shared/lib/category-colors';

interface NoteData {
  title: string;
  content: string;
  category: CategoryType;
  lastEdited?: string;
}

const defaultNote: NoteData = {
  title: '',
  content: '',
  category: 'random-thoughts',
  lastEdited: undefined,
};

// Sample note data for demo
const sampleNote: NoteData = {
  title: 'Note Title',
  content: '',
  category: 'random-thoughts',
  lastEdited: 'July 21, 2024 at 8:39pm',
};

/**
 * useNoteEditor Hook
 *
 * Manages note editing state including title, content, category selection.
 * Handles category dropdown state and navigation.
 */
export function useNoteEditor(noteId: string, initialData?: NoteData) {
  const router = useRouter();
  const isNewNote = noteId === 'new';

  const noteData = initialData || (isNewNote ? defaultNote : sampleNote);

  const [title, setTitle] = useState(noteData.title);
  const [content, setContent] = useState(noteData.content);
  const [category, setCategory] = useState<CategoryType>(noteData.category);
  const [isCategoryOpen, setIsCategoryOpen] = useState(false);

  const close = () => {
    router.push('/');
  };

  const selectCategory = (newCategory: CategoryType) => {
    setCategory(newCategory);
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
    category,
    selectCategory,
    isCategoryOpen,
    toggleCategoryDropdown,
    close,
    lastEdited: isNewNote ? undefined : noteData.lastEdited,
  };
}
