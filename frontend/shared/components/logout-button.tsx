'use client';

import { logoutAction } from '@/app/(auth)/actions';

/**
 * Logout Button
 * Client component that triggers the logout Server Action
 */
export function LogoutButton() {
  return (
    <form action={logoutAction}>
      <button
        type="submit"
        className="px-4 py-2 text-sm text-[rgb(var(--color-text-secondary))] hover:text-[rgb(var(--color-text-primary))] transition-colors"
      >
        Logout
      </button>
    </form>
  );
}
