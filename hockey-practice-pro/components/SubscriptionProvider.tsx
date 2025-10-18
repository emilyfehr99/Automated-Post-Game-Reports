'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useSession } from 'next-auth/react'
import { Subscription, getSubscriptionLimits, checkFeatureAccess, checkUsageLimit } from '@/lib/subscription'

interface SubscriptionContextType {
  subscription: Subscription | null
  limits: ReturnType<typeof getSubscriptionLimits>
  isLoading: boolean
  canUseFeature: (feature: keyof ReturnType<typeof getSubscriptionLimits>) => boolean
  canCreateItem: (type: 'practicePlans' | 'drills' | 'teamMembers', currentCount: number) => boolean
  upgradeRequired: (feature: keyof ReturnType<typeof getSubscriptionLimits>) => boolean
}

const SubscriptionContext = createContext<SubscriptionContextType | undefined>(undefined)

export function SubscriptionProvider({ children }: { children: ReactNode }) {
  const { data: session } = useSession()
  const [subscription, setSubscription] = useState<Subscription | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (session?.user) {
      // Everything is free now - unlimited access
      const mockSubscription: Subscription = {
        id: 'sub_' + Date.now(),
        userId: session.user.id || '1',
        plan: 'free', // All users get free access
        status: 'active',
        currentPeriodStart: new Date(),
        currentPeriodEnd: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000), // 1 year from now
        cancelAtPeriodEnd: false
      }
      
      setSubscription(mockSubscription)
      setIsLoading(false)
    } else {
      setSubscription(null)
      setIsLoading(false)
    }
  }, [session])

  const limits = getSubscriptionLimits(subscription?.plan || 'free')

  const canUseFeature = (feature: keyof ReturnType<typeof getSubscriptionLimits>): boolean => {
    if (!subscription) return false
    return checkFeatureAccess(subscription.plan, feature)
  }

  const canCreateItem = (type: 'practicePlans' | 'drills' | 'teamMembers', currentCount: number): boolean => {
    if (!subscription) return false
    
    const limitType = type === 'practicePlans' ? 'maxPracticePlans' as const :
                     type === 'drills' ? 'maxDrills' as const :
                     'maxTeamMembers' as const
    
    return checkUsageLimit(subscription.plan, currentCount, limitType)
  }

  const upgradeRequired = (feature: keyof ReturnType<typeof getSubscriptionLimits>): boolean => {
    return !canUseFeature(feature)
  }

  return (
    <SubscriptionContext.Provider value={{
      subscription,
      limits,
      isLoading,
      canUseFeature,
      canCreateItem,
      upgradeRequired
    }}>
      {children}
    </SubscriptionContext.Provider>
  )
}

export function useSubscription() {
  const context = useContext(SubscriptionContext)
  if (context === undefined) {
    throw new Error('useSubscription must be used within a SubscriptionProvider')
  }
  return context
}
