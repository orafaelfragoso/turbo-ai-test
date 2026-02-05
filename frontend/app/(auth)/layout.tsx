import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'NoteApp - Authentication',
  description: 'Sign in or create an account to start taking notes',
};

interface AuthLayoutProps {
  children: React.ReactNode;
}

/**
 * Auth Layout
 * Wraps all authentication pages (login, signup)
 * Uses a simple centered layout
 */
export default function AuthLayout({ children }: AuthLayoutProps) {
  return <>{children}</>;
}
