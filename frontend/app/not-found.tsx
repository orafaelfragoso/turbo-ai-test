import Image from 'next/image';
import { Button, Link } from '@/shared/components';

export const metadata = {
  title: '404 - Page Not Found | NoteApp',
  description: 'The page you are looking for does not exist',
};

/**
 * 404 Not Found Page
 * Displayed when a user navigates to a non-existent route
 */
export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-[rgb(var(--color-background))] flex items-center justify-center px-6">
      <div className="text-center">
        <div className="flex justify-center mb-8">
          <Image src="/coffee.png" alt="Coffee cup illustration" width={120} height={160} quality={90} />
        </div>

        <h1 className="font-serif text-6xl font-bold text-[rgb(var(--color-text-primary))] mb-4">
          404
        </h1>

        <p className="text-xl text-[rgb(var(--color-text-secondary))] mb-8 max-w-md mx-auto">
          Oops! This page seems to have wandered off. Let&apos;s get you back on track.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/">
            <Button variant="contained">Go Home</Button>
          </Link>
          <Link href="/login">
            <Button variant="contained">Sign In</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
