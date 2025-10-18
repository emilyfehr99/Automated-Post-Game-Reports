export interface Subscription {
  id: string
  userId: string
  plan: 'free' | 'pro' | 'team'
  status: 'active' | 'cancelled' | 'past_due'
  currentPeriodStart: Date
  currentPeriodEnd: Date
  cancelAtPeriodEnd: boolean
  stripeSubscriptionId?: string
  stripeCustomerId?: string
}

export interface SubscriptionLimits {
  maxPracticePlans: number
  maxDrills: number
  maxTeamMembers: number
  canExportPDF: boolean
  canUseAdvancedDrawing: boolean
  canCollaborate: boolean
  canUseAPI: boolean
  hasPrioritySupport: boolean
}

export const getSubscriptionLimits = (plan: string): SubscriptionLimits => {
  // Everything is free now - unlimited access to all features
  return {
    maxPracticePlans: -1, // unlimited
    maxDrills: -1, // unlimited
    maxTeamMembers: -1, // unlimited
    canExportPDF: true,
    canUseAdvancedDrawing: true,
    canCollaborate: true,
    canUseAPI: true,
    hasPrioritySupport: true
  }
}

export const checkFeatureAccess = (
  userPlan: string,
  feature: keyof SubscriptionLimits
): boolean => {
  const limits = getSubscriptionLimits(userPlan)
  return limits[feature] === true
}

export const checkUsageLimit = (
  userPlan: string,
  currentUsage: number,
  limitType: 'maxPracticePlans' | 'maxDrills' | 'maxTeamMembers'
): boolean => {
  const limits = getSubscriptionLimits(userPlan)
  const limit = limits[limitType]
  
  // -1 means unlimited
  if (limit === -1) return true
  
  return currentUsage < limit
}
