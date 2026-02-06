import type { Metadata } from 'next';
import { Inter, Inria_Serif } from 'next/font/google';
import { QueryClientProvider } from '@/shared/components';
import './globals.css';

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

export const metadata: Metadata = {
  title: 'NoteApp',
  description: 'A beautiful note-taking application',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${inriaSerif.variable} antialiased`}>
        <QueryClientProvider>{children}</QueryClientProvider>
      </body>
    </html>
  );
}
