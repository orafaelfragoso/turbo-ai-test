import { type ReactNode } from 'react';

interface FormLayoutProps {
  /** The heading text (e.g., "Yay, You're Back!" or "Yay, New Friend!") */
  title: string;
  /** Illustration/image to display above the title */
  illustration: ReactNode;
  /** Form content (inputs, buttons, links) */
  children: ReactNode;
}

/**
 * FormLayout Component
 *
 * Layout wrapper for authentication forms (login/signup).
 * Centers content, displays illustration, and uses Inria Serif for the title.
 */
export function FormLayout({ title, illustration, children }: FormLayoutProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[rgb(var(--color-background))] px-6">
      <div className="w-full max-w-sm">
        <div className="flex flex-col items-center gap-8">
          {/* Illustration */}
          <div className="flex items-center justify-center">{illustration}</div>

          {/* Title - Using Inria Serif */}
          <h1 className="font-serif text-4xl md:text-5xl text-[rgb(var(--color-text-primary))] text-center font-bold">
            {title}
          </h1>

          {/* Form Content */}
          <div className="w-full flex flex-col gap-4">{children}</div>
        </div>
      </div>
    </div>
  );
}
