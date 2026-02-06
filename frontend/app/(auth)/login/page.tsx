'use client';

import { useActionState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import Image from 'next/image';
import { FormLayout } from '@/features/auth/components';
import { Button, Input, Link, EyeIcon } from '@/shared/components';
import { signinAction } from '@/app/(auth)/actions';

/**
 * Login Page
 * Displays the login form with email/password inputs
 */
export default function LoginPage() {
  const searchParams = useSearchParams();
  const [state, formAction, isPending] = useActionState(signinAction, null);
  const successMessage = searchParams.get('success');

  // Set document title
  useEffect(() => {
    document.title = 'Login - NoteApp';
  }, []);

  return (
    <FormLayout
      title="Yay, You're Back!"
      illustration={
        <Image
          src="/cactus.png"
          alt="Cute cactus illustration"
          width={95.21}
          height={113.6}
          quality={90}
          priority
        />
      }
    >
      <form action={formAction} className="flex flex-col gap-4">
        {/* Success message after signup */}
        {successMessage === 'account-created' && (
          <div className="px-4 py-3 rounded-lg bg-green-50 border border-green-200">
            <p className="text-sm text-green-800">Account created successfully! Please sign in.</p>
          </div>
        )}

        {/* Error message */}
        {state?.error && (
          <div className="px-4 py-3 rounded-lg bg-red-50 border border-red-200">
            <p className="text-sm text-red-800">{state.error}</p>
          </div>
        )}

        <Input
          type="email"
          name="email"
          placeholder="Email address"
          autoComplete="email"
          required
          disabled={isPending}
        />
        <Input
          type="password"
          name="password"
          placeholder="Password"
          autoComplete="current-password"
          icon={<EyeIcon className="size-5" />}
          required
          disabled={isPending}
        />

        {/* Hidden input for redirect URL */}
        <input type="hidden" name="redirect" value={searchParams.get('redirect') || '/'} />

        <div className="mt-4">
          <Button type="submit" variant="blocked" disabled={isPending}>
            {isPending ? 'Signing in...' : 'Login'}
          </Button>
        </div>

        <div className="text-center">
          <Link href="/signup" className="underline">
            Oops! I&apos;ve never been here before
          </Link>
        </div>
      </form>
    </FormLayout>
  );
}
