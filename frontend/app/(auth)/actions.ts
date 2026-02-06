'use server';

import { cookies } from 'next/headers';
import { redirect } from 'next/navigation';
import { z } from 'zod';
import { signin, signup } from '@/shared/lib/api/auth';

/**
 * Input validation schemas
 */
const signupSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

const signinSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

/**
 * Action State Type
 */
export type AuthActionState = {
  error?: string;
  success?: boolean;
} | null;

/**
 * Signup Action
 * Creates a new user account and redirects to login
 */
export async function signupAction(
  prevState: AuthActionState,
  formData: FormData
): Promise<AuthActionState> {
  try {
    // Extract and validate form data
    const rawData = {
      email: formData.get('email'),
      password: formData.get('password'),
    };

    const validatedData = signupSchema.parse(rawData);

    // Call signup API
    await signup(validatedData.email, validatedData.password);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { error: error.errors[0].message };
    }

    if (error instanceof Error) {
      return { error: error.message };
    }

    return { error: 'An unexpected error occurred. Please try again.' };
  }

  // Redirect outside try-catch to allow Next.js redirect to work properly
  redirect('/login?success=account-created');
}

/**
 * Signin Action
 * Authenticates user and sets auth cookies
 */
export async function signinAction(
  prevState: AuthActionState,
  formData: FormData
): Promise<AuthActionState> {
  let redirectUrl: string | null = null;

  try {
    // Extract and validate form data
    const rawData = {
      email: formData.get('email'),
      password: formData.get('password'),
    };

    const validatedData = signinSchema.parse(rawData);

    // Call signin API
    const tokens = await signin(validatedData.email, validatedData.password);

    // Set HTTP-only cookies for tokens
    const cookieStore = await cookies();

    // Access token (15 minutes)
    cookieStore.set('access_token', tokens.access_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 15 * 60, // 15 minutes
      path: '/',
    });

    // Refresh token (7 days)
    cookieStore.set('refresh_token', tokens.refresh_token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 7 * 24 * 60 * 60, // 7 days
      path: '/',
    });

    // Get redirect parameter or default to home
    redirectUrl = formData.get('redirect') as string | null;
  } catch (error) {
    if (error instanceof z.ZodError) {
      return { error: error.errors[0].message };
    }

    if (error instanceof Error) {
      return { error: error.message };
    }

    return { error: 'An unexpected error occurred. Please try again.' };
  }

  // Redirect outside try-catch to allow Next.js redirect to work properly
  redirect(redirectUrl && redirectUrl !== '/login' ? redirectUrl : '/');
}

/**
 * Logout Action
 * Clears auth cookies and redirects to login
 */
export async function logoutAction(): Promise<void> {
  const cookieStore = await cookies();

  // Clear auth cookies
  cookieStore.delete('access_token');
  cookieStore.delete('refresh_token');

  redirect('/login');
}
