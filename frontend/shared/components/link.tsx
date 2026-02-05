import { type ComponentProps } from 'react';
import NextLink from 'next/link';
import { cn } from '@/shared/lib/cn';

type LinkProps = ComponentProps<typeof NextLink>;

/**
 * Link Component
 *
 * A styled anchor/link component built on Next.js Link.
 * Used for navigation and styled text links in forms.
 */
export function Link({ className, children, ...props }: LinkProps) {
  return (
    <NextLink
      className={cn(
        'font-sans text-xs font-normal',
        'text-[rgb(var(--color-accent))]',
        'underline',
        'transition-opacity duration-200',
        'hover:opacity-70',
        'focus-visible:outline-none',
        className
      )}
      {...props}
    >
      {children}
    </NextLink>
  );
}
