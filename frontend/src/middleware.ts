import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  const role = request.cookies.get('role')?.value;
  const path = request.nextUrl.pathname;

  // Paths that do not require authentication
  const isPublicPath = path === '/';

  if (!token && !isPublicPath) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  if (isPublicPath && token && role) {
    // Redirect authenticated users trying to access login
    if (role === 'admin') return NextResponse.redirect(new URL('/dashboard', request.url));
    if (role === 'secretary') return NextResponse.redirect(new URL('/secretary/dashboard', request.url));
    if (role === 'teacher') return NextResponse.redirect(new URL('/teacher/dashboard', request.url));
  }

  // Role-based route guards
  if (path.startsWith('/dashboard') && role !== 'admin') {
    return NextResponse.redirect(new URL('/', request.url));
  }
  if (path.startsWith('/admin') && role !== 'admin') {
    return NextResponse.redirect(new URL('/', request.url));
  }
  if (path.startsWith('/secretary') && role !== 'secretary') {
    return NextResponse.redirect(new URL('/', request.url));
  }
  if (path.startsWith('/teacher') && role !== 'teacher') {
    return NextResponse.redirect(new URL('/', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
};
