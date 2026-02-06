'use client';

import { useActionState, useEffect } from 'react';
import Image from 'next/image';
import { FormLayout } from '@/features/auth/components';
import { Button, Input, Link, EyeIcon } from '@/shared/components';
import { signupAction } from '@/app/(auth)/actions';

/**
 * Signup Page
 * Displays the registration form with email/password inputs
 */
export default function SignupPage() {
  const [state, formAction, isPending] = useActionState(signupAction, null);

  // Set document title
  useEffect(() => {
    document.title = 'Sign Up - NoteApp';
  }, []);

  return (
    <FormLayout
      title="Yay, New Friend!"
      illustration={
        <Image
          src="/cat.png"
          alt="Cute sleeping cat illustration"
          width={188.14}
          height={134}
          quality={90}
          priority
        />
      }
    >
      <form action={formAction} className="flex flex-col gap-4">
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
          autoComplete="new-password"
          icon={<EyeIcon className="size-5" />}
          required
          disabled={isPending}
          minLength={8}
        />

        <div className="text-xs text-[rgb(var(--color-text-secondary))]">
          Password must be at least 8 characters
        </div>

        <div className="mt-4">
          <Button type="submit" variant="blocked" disabled={isPending}>
            {isPending ? 'Creating account...' : 'Sign Up'}
          </Button>
        </div>

        <div className="text-center">
          <Link href="/login" className="underline">
            We&apos;re already friends!
          </Link>
        </div>
      </form>
    </FormLayout>
  );
}
