import { z } from 'zod';
import { apiErrorSchema } from './schemas';

/**
 * API Client Configuration
 */
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  (typeof window === 'undefined' ? 'http://api:8000' : 'http://localhost:8000');
const API_VERSION = 'application/vnd.noteapp.v1+json';

/**
 * API Client Error
 */
export class ApiClientError extends Error {
  constructor(
    public status: number,
    public message: string,
    public details?: unknown
  ) {
    super(message);
    this.name = 'ApiClientError';
  }
}

/**
 * Fetch wrapper with Zod validation and error handling
 * For server-side use (reads auth token from cookies)
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit & {
    schema: z.ZodType<T>;
    token?: string;
  }
): Promise<T> {
  const { schema, token, ...fetchOptions } = options;

  const headers: HeadersInit = {
    Accept: API_VERSION,
    'Content-Type': 'application/json',
    ...fetchOptions.headers,
  };

  // Add Authorization header if token provided
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers,
    });

    // Handle error responses
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      let errorDetails: unknown = undefined;

      try {
        const errorData = await response.json();
        const parsedError = apiErrorSchema.safeParse(errorData);
        if (parsedError.success) {
          errorMessage = parsedError.data.detail || parsedError.data.message || errorMessage;
        }
        errorDetails = errorData;
      } catch {
        // Failed to parse error response, use status text
        errorMessage = response.statusText || errorMessage;
      }

      throw new ApiClientError(response.status, errorMessage, errorDetails);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    // Parse and validate response
    const data = await response.json();
    const parsed = schema.safeParse(data);

    if (!parsed.success) {
      throw new Error(`Schema validation failed: ${parsed.error.message}`);
    }

    return parsed.data;
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw error;
    }
    throw new Error(
      `API request failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}

/**
 * Client-side fetch wrapper (routes through Next.js proxy)
 */
export async function apiRequestClient<T>(
  endpoint: string,
  options: RequestInit & {
    schema: z.ZodType<T>;
  }
): Promise<T> {
  const { schema, ...fetchOptions } = options;

  // Route through Next.js proxy to attach auth headers server-side
  const proxyUrl = `/api/proxy${endpoint}`;

  try {
    const response = await fetch(proxyUrl, fetchOptions);

    // Handle error responses
    if (!response.ok) {
      let errorMessage = `HTTP ${response.status}`;
      let errorDetails: unknown = undefined;

      try {
        const errorData = await response.json();
        const parsedError = apiErrorSchema.safeParse(errorData);
        if (parsedError.success) {
          errorMessage = parsedError.data.detail || parsedError.data.message || errorMessage;
        }
        errorDetails = errorData;
      } catch {
        errorMessage = response.statusText || errorMessage;
      }

      throw new ApiClientError(response.status, errorMessage, errorDetails);
    }

    // Handle 204 No Content
    if (response.status === 204) {
      return undefined as T;
    }

    // Parse and validate response
    const data = await response.json();
    const parsed = schema.safeParse(data);

    if (!parsed.success) {
      throw new Error(`Schema validation failed: ${parsed.error.message}`);
    }

    return parsed.data;
  } catch (error) {
    if (error instanceof ApiClientError) {
      throw error;
    }
    throw new Error(
      `API request failed: ${error instanceof Error ? error.message : 'Unknown error'}`
    );
  }
}
