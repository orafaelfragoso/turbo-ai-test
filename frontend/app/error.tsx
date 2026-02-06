'use client';

import Image from 'next/image';
import { useEffect } from 'react';
import { Button } from '@/shared/components';

interface ErrorPageProps {
  error: Error & { digest?: string };
  reset: () => void;
}

/**
 * Error Page
 * Displayed when an unhandled error occurs in the application
 */
export default function ErrorPage({ error, reset }: ErrorPageProps) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error('Application error:', error);
  }, [error]);

  return (
    <div className="min-h-screen bg-[rgb(var(--color-background))] flex items-center justify-center px-6">
      <div className="text-center">
        <div className="flex justify-center mb-8">
          <Image
            src="/cactus.png"
            alt="Cactus illustration"
            width={120}
            height={140}
            quality={90}
          />
        </div>

        <h1 className="font-serif text-4xl font-bold text-[rgb(var(--color-text-primary))] mb-4">
          Something went wrong!
        </h1>

        <p className="text-lg text-[rgb(var(--color-text-secondary))] mb-8 max-w-md mx-auto">
          Don&apos;t worry, even the best apps have their moments. Let&apos;s try that again.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Button variant="contained" onClick={reset}>
            Try Again
          </Button>
          <Button variant="contained" onClick={() => (window.location.href = '/')}>
            Go Home
          </Button>
        </div>

        {process.env.NODE_ENV === 'development' && error.message && (
          <div className="mt-8 p-4 bg-red-50 rounded-lg max-w-lg mx-auto text-left">
            <p className="text-sm font-mono text-red-700 break-all">{error.message}</p>
          </div>
        )}
      </div>
    </div>
  );
}
