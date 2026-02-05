import Image from 'next/image';
import { FormLayout } from '@/features/auth/components';
import { Button, Input, Link, EyeIcon } from '@/shared/components';

export const metadata = {
  title: 'Sign Up - NoteApp',
  description: 'Create a new NoteApp account',
};

/**
 * Signup Page
 * Displays the registration form with email/password inputs
 */
export default function SignupPage() {
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
      <form className="flex flex-col gap-4">
        <Input
          type="email"
          name="email"
          placeholder="Email address"
          autoComplete="email"
          required
        />
        <Input
          type="password"
          name="password"
          placeholder="Password"
          autoComplete="new-password"
          icon={<EyeIcon className="size-5" />}
          required
        />

        <div className="mt-4">
          <Button type="submit" variant="blocked">
            Sign Up
          </Button>
        </div>

        <div className="text-center">
          <Link href="/login">We&apos;re already friends!</Link>
        </div>
      </form>
    </FormLayout>
  );
}
