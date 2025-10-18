// Simple localStorage-based sync system
// This provides a unified interface for data management

// Data types
export interface Drill {
  id: string
  name: string
  description: string
  category: string
  setup: string[]
  instructions: string[]
  images: string[]
  createdAt: string
  updatedAt: string
}

export interface PracticePlan {
  id: string
  name: string
  description: string
  drills: Array<{
    id: string
    name: string
    duration: number
    category: string
    images: string[]
  }>
  totalDuration: number
  createdAt: string
  updatedAt: string
}

export interface Settings {
  teamName: string
  coachName: string
  season: string
  level: string
  updatedAt: string
}

// Drills functions
export const saveDrill = async (drill: any) => {
  try {
    const drills = JSON.parse(localStorage.getItem('hockey-drills') || '[]')
    const existingIndex = drills.findIndex((d: any) => d.id === drill.id)
    
    if (existingIndex >= 0) {
      drills[existingIndex] = { ...drill, updatedAt: new Date().toISOString() }
    } else {
      drills.push({ ...drill, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() })
    }
    
    localStorage.setItem('hockey-drills', JSON.stringify(drills))
    return true
  } catch (error) {
    console.error('Failed to save drill:', error)
    return false
  }
}

export const getDrills = async (): Promise<Drill[]> => {
  try {
    return JSON.parse(localStorage.getItem('hockey-drills') || '[]')
  } catch (error) {
    console.error('Failed to get drills:', error)
    return []
  }
}

export const subscribeToDrills = (callback: (drills: Drill[]) => void) => {
  // Simulate real-time updates by checking localStorage periodically
  const checkForUpdates = () => {
    const drills = JSON.parse(localStorage.getItem('hockey-drills') || '[]')
    callback(drills)
  }
  
  // Check immediately
  checkForUpdates()
  
  // Set up interval to check for changes
  const interval = setInterval(checkForUpdates, 2000) // Check every 2 seconds
  
  // Return cleanup function
  return () => clearInterval(interval)
}

// Practice Plans functions
export const savePracticePlan = async (plan: any) => {
  try {
    const plans = JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
    const existingIndex = plans.findIndex((p: any) => p.id === plan.id)
    
    if (existingIndex >= 0) {
      plans[existingIndex] = { ...plan, updatedAt: new Date().toISOString() }
    } else {
      plans.push({ ...plan, createdAt: new Date().toISOString(), updatedAt: new Date().toISOString() })
    }
    
    localStorage.setItem('hockey-practice-plans', JSON.stringify(plans))
    return true
  } catch (error) {
    console.error('Failed to save practice plan:', error)
    return false
  }
}

export const getPracticePlans = async (): Promise<PracticePlan[]> => {
  try {
    return JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
  } catch (error) {
    console.error('Failed to get practice plans:', error)
    return []
  }
}

export const subscribeToPracticePlans = (callback: (plans: PracticePlan[]) => void) => {
  // Simulate real-time updates by checking localStorage periodically
  const checkForUpdates = () => {
    const plans = JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
    callback(plans)
  }
  
  // Check immediately
  checkForUpdates()
  
  // Set up interval to check for changes
  const interval = setInterval(checkForUpdates, 2000) // Check every 2 seconds
  
  // Return cleanup function
  return () => clearInterval(interval)
}

// Settings functions
export const saveSettings = async (settings: any) => {
  try {
    const settingsData = { ...settings, updatedAt: new Date().toISOString() }
    localStorage.setItem('hockey-settings', JSON.stringify(settingsData))
    return true
  } catch (error) {
    console.error('Failed to save settings:', error)
    return false
  }
}

export const getSettings = async (): Promise<Settings | null> => {
  try {
    const settings = localStorage.getItem('hockey-settings')
    return settings ? JSON.parse(settings) : null
  } catch (error) {
    console.error('Failed to get settings:', error)
    return null
  }
}

export const subscribeToSettings = (callback: (settings: Settings | null) => void) => {
  // Simulate real-time updates by checking localStorage periodically
  const checkForUpdates = () => {
    const settings = localStorage.getItem('hockey-settings')
    callback(settings ? JSON.parse(settings) : null)
  }
  
  // Check immediately
  checkForUpdates()
  
  // Set up interval to check for changes
  const interval = setInterval(checkForUpdates, 2000) // Check every 2 seconds
  
  // Return cleanup function
  return () => clearInterval(interval)
}
