import { cookies } from 'next/headers';
import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ||
  (typeof window === 'undefined' ? 'http://api:8000' : 'http://localhost:8000');
const API_VERSION = 'application/vnd.noteapp.v1+json';

/**
 * Proxy route handler for authenticated API requests
 * Reads auth token from HTTP-only cookie and forwards to backend
 */
async function proxyRequest(request: NextRequest, method: string) {
  const cookieStore = await cookies();
  const accessToken = cookieStore.get('access_token')?.value;

  // Extract path segments
  const { pathname, search } = new URL(request.url);
  let path = pathname.replace('/api/proxy', '');

  // Ensure trailing slash for Django APPEND_SLASH compatibility
  // Add trailing slash if path doesn't end with one and doesn't have a file extension
  if (!path.endsWith('/') && !path.match(/\.[a-z0-9]+$/i)) {
    path = `${path}/`;
  }

  const targetUrl = `${API_BASE_URL}${path}${search}`;

  // Build headers
  const headers: HeadersInit = {
    Accept: API_VERSION,
  };

  // Add Authorization header if token exists
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  // Get request body for non-GET/HEAD requests
  let body: string | undefined = undefined;
  if (method !== 'GET' && method !== 'HEAD') {
    const contentType = request.headers.get('content-type');
    if (contentType?.includes('application/json') || contentType?.includes('text/plain')) {
      // For JSON or plain text, read as text and ensure JSON content type
      body = await request.text();
      headers['Content-Type'] = 'application/json';
    } else {
      // For other types, preserve the content type
      body = await request.text();
      if (contentType) {
        headers['Content-Type'] = contentType;
      }
    }
  }

  try {
    // Forward request to backend
    const response = await fetch(targetUrl, {
      method,
      headers,
      body,
    });

    // Get response body
    const responseBody = response.status === 204 ? null : await response.text();

    // Forward response back to client
    return new NextResponse(responseBody, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        'Content-Type': response.headers.get('content-type') || 'application/json',
      },
    });
  } catch (error) {
    console.error('Proxy request failed:', error);
    return NextResponse.json(
      {
        detail: 'Proxy request failed',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 502 }
    );
  }
}

export async function GET(request: NextRequest) {
  return proxyRequest(request, 'GET');
}

export async function POST(request: NextRequest) {
  return proxyRequest(request, 'POST');
}

export async function PATCH(request: NextRequest) {
  return proxyRequest(request, 'PATCH');
}

export async function PUT(request: NextRequest) {
  return proxyRequest(request, 'PUT');
}

export async function DELETE(request: NextRequest) {
  return proxyRequest(request, 'DELETE');
}
