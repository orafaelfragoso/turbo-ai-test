'use client';

import { Inter, Inria_Serif } from 'next/font/google';

const inter = Inter({
  variable: '--font-sans',
  subsets: ['latin'],
  display: 'swap',
});

const inriaSerif = Inria_Serif({
  variable: '--font-serif',
  weight: ['300', '400', '700'],
  subsets: ['latin'],
  display: 'swap',
});

interface GlobalErrorProps {
  error: Error & { digest?: string };
  reset: () => void;
}

/**
 * Global Error Page
 * Displayed when an error occurs at the root layout level
 * Must include its own html/body tags and inline styles (CSS may not load)
 */
export default function GlobalError({ reset }: GlobalErrorProps) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} ${inriaSerif.variable} antialiased`}
        style={{ backgroundColor: 'rgb(245, 239, 230)' }}
      >
        <div className="min-h-screen flex items-center justify-center px-6">
          <div className="text-center">
            <h1
              className="text-4xl font-bold mb-4"
              style={{ fontFamily: "'Inria Serif', serif", color: 'rgb(92, 75, 55)' }}
            >
              Something went terribly wrong!
            </h1>

            <p className="text-lg mb-8 max-w-md mx-auto" style={{ color: 'rgb(139, 115, 85)' }}>
              We&apos;re sorry, but something unexpected happened. Please try again.
            </p>

            <button
              onClick={reset}
              className="px-4 py-3 rounded-full font-bold transition-colors duration-200"
              style={{
                backgroundColor: 'transparent',
                color: 'rgb(149, 113, 57)',
                border: '1px solid rgb(149, 113, 57)',
              }}
            >
              Try Again
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
