// Middleware disabled for now to allow landing page access
export default function middleware() {
  // No middleware for now - just pass through
}

export const config = {
  matcher: [
    // Disable middleware for now
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
