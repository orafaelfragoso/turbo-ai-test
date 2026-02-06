import { cookies } from 'next/headers';
import { notFound } from 'next/navigation';
import { Editor } from '@/features/notes/components';
import { getNote } from '@/shared/lib/api/notes';

interface PageProps {
  params: Promise<{ id: string }>;
}

export async function generateMetadata({ params }: PageProps) {
  const { id } = await params;
  const isNew = id === 'new';

  return {
    title: isNew ? 'New Note - NoteApp' : 'Edit Note - NoteApp',
    description: isNew ? 'Create a new note' : 'Edit your note',
  };
}

/**
 * Note Editor Page
 * Full-page editor for creating/editing/viewing a note.
 * Route: /notes/[id] where id can be 'new' or an existing note UUID
 */
export default async function NoteEditorPage({ params }: PageProps) {
  const { id } = await params;
  const isNew = id === 'new';

  // For new notes, pass no initial data
  if (isNew) {
    return <Editor noteId={id} />;
  }

  // For existing notes, fetch the note data server-side
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('access_token')?.value;

  try {
    const note = await getNote(id, accessToken);

    // Convert backend note to editor initial data format
    const initialData = {
      title: note.title,
      content: note.content,
      categoryId: note.category?.id,
      categoryName: note.category?.name,
      categoryColor: note.category?.color || '#6366F1',
      lastEdited:
        new Date(note.updated_at).toLocaleDateString('en-US', {
          month: 'long',
          day: 'numeric',
          year: 'numeric',
        }) +
        ' at ' +
        new Date(note.updated_at).toLocaleTimeString('en-US', {
          hour: 'numeric',
          minute: '2-digit',
          hour12: true,
        }),
    };

    return <Editor noteId={id} initialData={initialData} />;
  } catch (error) {
    console.error('Failed to fetch note:', error);
    // If note not found or error, show 404
    notFound();
  }
}
