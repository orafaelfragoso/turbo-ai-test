import { Editor } from '@/features/notes/components';

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
 * Route: /notes/[id] where id can be 'new' or an existing note ID
 */
export default async function NoteEditorPage({ params }: PageProps) {
  const { id } = await params;

  return <Editor noteId={id} />;
}
