import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Providers } from '@/components/Providers'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Hockey Practice Pro',
  description: 'Professional hockey practice planning and drill management platform',
  icons: {
    icon: [
      { url: '/favicon-16x16.png?v=2', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png?v=2', sizes: '32x32', type: 'image/png' },
      { url: '/favicon.ico?v=2', sizes: 'any' }
    ],
    apple: [
      { url: '/apple-touch-icon.png?v=2', sizes: '180x180', type: 'image/png' }
    ],
    other: [
      { url: '/android-chrome-192x192.png?v=2', sizes: '192x192', type: 'image/png' },
      { url: '/android-chrome-512x512.png?v=2', sizes: '512x512', type: 'image/png' }
    ]
  }
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="manifest" href="/site.webmanifest" />
      </head>
      <body className={inter.className}>
        <Providers>
          <div className="min-h-screen bg-gray-50">
            {children}
          </div>
        </Providers>
      </body>
    </html>
  )
}
