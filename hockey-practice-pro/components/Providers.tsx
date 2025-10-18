'use client'

import { SessionProvider } from 'next-auth/react'
import { SubscriptionProvider } from './SubscriptionProvider'

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <SessionProvider>
      <SubscriptionProvider>
        {children}
      </SubscriptionProvider>
    </SessionProvider>
  )
}
