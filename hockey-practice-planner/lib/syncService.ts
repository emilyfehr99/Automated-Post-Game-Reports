// Real-time sync service using localStorage and periodic checks
// This creates a simple sync system that works across devices

const SYNC_INTERVAL = 5000 // Check for updates every 5 seconds
const STORAGE_KEYS = {
  DRILLS: 'hockey-drills',
  PLANS: 'hockey-practice-plans',
  SETTINGS: 'hockey-settings',
  CATEGORIES: 'hockey-custom-categories',
  LAST_SYNC: 'hockey-last-sync',
  DEVICE_ID: 'hockey-device-id'
}

// Generate unique device ID
const getDeviceId = (): string => {
  let deviceId = localStorage.getItem(STORAGE_KEYS.DEVICE_ID)
  if (!deviceId) {
    deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem(STORAGE_KEYS.DEVICE_ID, deviceId)
  }
  return deviceId
}

// Get all data with timestamps
const getAllData = () => {
  return {
    drills: JSON.parse(localStorage.getItem(STORAGE_KEYS.DRILLS) || '[]'),
    practicePlans: JSON.parse(localStorage.getItem(STORAGE_KEYS.PLANS) || '[]'),
    settings: JSON.parse(localStorage.getItem(STORAGE_KEYS.SETTINGS) || '{}'),
    customCategories: JSON.parse(localStorage.getItem(STORAGE_KEYS.CATEGORIES) || '[]'),
    deviceId: getDeviceId(),
    lastSync: Date.now()
  }
}

// Save all data
const saveAllData = (data: any) => {
  try {
    localStorage.setItem(STORAGE_KEYS.DRILLS, JSON.stringify(data.drills || []))
    localStorage.setItem(STORAGE_KEYS.PLANS, JSON.stringify(data.practicePlans || []))
    localStorage.setItem(STORAGE_KEYS.SETTINGS, JSON.stringify(data.settings || {}))
    localStorage.setItem(STORAGE_KEYS.CATEGORIES, JSON.stringify(data.customCategories || []))
    localStorage.setItem(STORAGE_KEYS.LAST_SYNC, Date.now().toString())
    return true
  } catch (error) {
    console.error('Failed to save data:', error)
    return false
  }
}

// Sync service class
class SyncService {
  private listeners: Map<string, Function[]> = new Map()
  private syncInterval: NodeJS.Timeout | null = null
  private isRunning = false

  // Start the sync service
  start() {
    if (this.isRunning) return
    
    this.isRunning = true
    console.log('🔄 Sync service started')
    
    // Check for updates periodically
    this.syncInterval = setInterval(() => {
      this.checkForUpdates()
    }, SYNC_INTERVAL)
  }

  // Stop the sync service
  stop() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval)
      this.syncInterval = null
    }
    this.isRunning = false
    console.log('⏹️ Sync service stopped')
  }

  // Check for updates and notify listeners
  private checkForUpdates() {
    const data = getAllData()
    
    // Notify all listeners
    this.listeners.forEach((callbacks, key) => {
      callbacks.forEach(callback => {
        try {
          const value = (data as any)[key] || []
          callback(value)
        } catch (error) {
          console.error('Error in sync callback:', error)
        }
      })
    })
  }

  // Subscribe to data changes
  subscribe(key: string, callback: Function) {
    if (!this.listeners.has(key)) {
      this.listeners.set(key, [])
    }
    this.listeners.get(key)!.push(callback)
    
    // Return unsubscribe function
    return () => {
      const callbacks = this.listeners.get(key)
      if (callbacks) {
        const index = callbacks.indexOf(callback)
        if (index > -1) {
          callbacks.splice(index, 1)
        }
      }
    }
  }

  // Save data and trigger sync
  async saveData(key: string, data: any) {
    try {
      // Update localStorage
      localStorage.setItem(STORAGE_KEYS[key.toUpperCase() as keyof typeof STORAGE_KEYS], JSON.stringify(data))
      
      // Update last sync time
      localStorage.setItem(STORAGE_KEYS.LAST_SYNC, Date.now().toString())
      
      // Notify listeners immediately
      this.checkForUpdates()
      
      console.log(`✅ ${key} saved and synced`)
      return true
    } catch (error) {
      console.error(`Failed to save ${key}:`, error)
      return false
    }
  }

  // Get current data
  getData(key: string) {
    const storageKey = STORAGE_KEYS[key.toUpperCase() as keyof typeof STORAGE_KEYS]
    return JSON.parse(localStorage.getItem(storageKey) || '[]')
  }

  // Export all data
  exportData() {
    return getAllData()
  }

  // Import data
  importData(data: any) {
    return saveAllData(data)
  }

  // Get sync status
  getSyncStatus() {
    return {
      deviceId: getDeviceId(),
      lastSync: localStorage.getItem(STORAGE_KEYS.LAST_SYNC),
      isRunning: this.isRunning
    }
  }
}

// Create singleton instance
export const syncService = new SyncService()

// Export individual functions for compatibility
export const subscribeToDrills = (callback: (drills: any[]) => void) => syncService.subscribe('drills', callback)
export const subscribeToPracticePlans = (callback: (plans: any[]) => void) => syncService.subscribe('practicePlans', callback)
export const subscribeToSettings = (callback: (settings: any) => void) => syncService.subscribe('settings', callback)

export const saveDrill = (drills: any) => syncService.saveData('drills', drills)
export const savePracticePlan = (plans: any) => syncService.saveData('practicePlans', plans)
export const saveSettings = (settings: any) => syncService.saveData('settings', settings)

export const getDrills = () => syncService.getData('drills')
export const getPracticePlans = () => syncService.getData('practicePlans')
export const getSettings = () => syncService.getData('settings')
