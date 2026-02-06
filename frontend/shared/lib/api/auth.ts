import { z } from 'zod';

/**
 * Auth API Schemas and Functions
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  (typeof window === 'undefined' ? 'http://api:8000' : 'http://localhost:8000');

const API_VERSION = 'application/vnd.noteapp.v1+json';

/**
 * Signup Response Schema
 */
export const signupResponseSchema = z.object({
  id: z.number(),
  email: z.string().email(),
  created_at: z.string(),
});

export type SignupResponse = z.infer<typeof signupResponseSchema>;

/**
 * Signin Response Schema
 */
export const signinResponseSchema = z.object({
  access_token: z.string(),
  refresh_token: z.string(),
  token_type: z.string(),
});

export type SigninResponse = z.infer<typeof signinResponseSchema>;

/**
 * Auth Error Response
 */
export const authErrorSchema = z.object({
  detail: z.string().optional(),
  email: z.array(z.string()).optional(),
  password: z.array(z.string()).optional(),
});

export type AuthError = z.infer<typeof authErrorSchema>;

/**
 * User Signup
 */
export async function signup(email: string, password: string): Promise<SignupResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/signup/`, {
    method: 'POST',
    headers: {
      Accept: API_VERSION,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    const parsedError = authErrorSchema.safeParse(errorData);

    if (parsedError.success) {
      const errorMsg =
        parsedError.data.detail ||
        parsedError.data.email?.[0] ||
        parsedError.data.password?.[0] ||
        'Signup failed';
      throw new Error(errorMsg);
    }

    throw new Error('Signup failed');
  }

  const data = await response.json();
  return signupResponseSchema.parse(data);
}

/**
 * User Signin
 */
export async function signin(email: string, password: string): Promise<SigninResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/signin/`, {
    method: 'POST',
    headers: {
      Accept: API_VERSION,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    const errorData = await response.json();
    const parsedError = authErrorSchema.safeParse(errorData);

    if (parsedError.success) {
      const errorMsg = parsedError.data.detail || 'Invalid email or password';
      throw new Error(errorMsg);
    }

    throw new Error('Login failed');
  }

  const data = await response.json();
  return signinResponseSchema.parse(data);
}

/**
 * User Logout
 */
export async function logout(accessToken: string, refreshToken: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/auth/logout/`, {
    method: 'POST',
    headers: {
      Accept: API_VERSION,
      'Content-Type': 'application/json',
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ refresh_token: refreshToken }),
  });

  if (!response.ok) {
    throw new Error('Logout failed');
  }
}
