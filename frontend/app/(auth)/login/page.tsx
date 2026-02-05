import Image from 'next/image';
import { FormLayout } from '@/features/auth/components';
import { Button, Input, Link, EyeIcon } from '@/shared/components';

export const metadata = {
  title: 'Login - NoteApp',
  description: 'Sign in to your NoteApp account',
};

/**
 * Login Page
 * Displays the login form with email/password inputs
 */
export default function LoginPage() {
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
          autoComplete="current-password"
          icon={<EyeIcon className="size-5" />}
          required
        />

        <div className="mt-4">
          <Button type="submit" variant="blocked">
            Login
          </Button>
        </div>

        <div className="text-center">
          <Link href="/signup">Oops! I&apos;ve never been here before</Link>
        </div>
      </form>
    </FormLayout>
  );
}
