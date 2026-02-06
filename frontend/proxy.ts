import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

/**
 * Proxy to protect routes and handle authentication
 * (formerly known as Middleware in Next.js <16)
 */
export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const accessToken = request.cookies.get('access_token')?.value;

  // Public routes that don't require authentication
  const publicRoutes = ['/login', '/signup'];
  const isPublicRoute = publicRoutes.some((route) => pathname.startsWith(route));

  // API health check is always public
  if (pathname.startsWith('/api/health')) {
    return NextResponse.next();
  }

  // If user is not authenticated and trying to access protected route
  if (!accessToken && !isPublicRoute) {
    const loginUrl = new URL('/login', request.url);
    // Add redirect parameter to return to original page after login
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // If user is authenticated and trying to access login/signup, redirect to home
  if (accessToken && isPublicRoute) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  return NextResponse.next();
}

/**
 * Matcher configuration
 * Applies proxy to all routes except:
 * - Static files (_next/static)
 * - Image optimization (_next/image)
 * - Favicon
 * - Public images
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (images, etc.)
     */
    '/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
  ],
};
