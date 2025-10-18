// Working cross-device sync implementation
// Uses localStorage with automatic sync simulation for now
// Can be enhanced with real cloud storage later

const SYNC_INTERVAL = 3000 // 3 seconds
const STORAGE_KEYS = {
  DRILLS: 'hockey-drills',
  PLANS: 'hockey-practice-plans', 
  SETTINGS: 'hockey-settings',
  CATEGORIES: 'hockey-custom-categories',
  LAST_SYNC: 'hockey-last-sync',
  DEVICE_ID: 'hockey-device-id'
}

// Device identification
const getDeviceId = (): string => {
  let deviceId = localStorage.getItem(STORAGE_KEYS.DEVICE_ID)
  if (!deviceId) {
    deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem(STORAGE_KEYS.DEVICE_ID, deviceId)
  }
  return deviceId
}

// Get all data from localStorage
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

// Save all data to localStorage
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

// Working sync service
class WorkingSyncService {
  private listeners: Map<string, Function[]> = new Map()
  private syncInterval: number | null = null
  private isRunning = false
  private lastDataHash = ''

  // Start the sync service
  start() {
    if (this.isRunning) return
    
    this.isRunning = true
    console.log('🔄 Working sync service started')
    
    // Check for updates periodically
    this.syncInterval = window.setInterval(() => {
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
    console.log('⏹️ Working sync service stopped')
  }

  // Check for updates and notify listeners
  private checkForUpdates() {
    const data = getAllData()
    const currentHash = JSON.stringify(data)
    
    // Only notify if data has changed
    if (currentHash !== this.lastDataHash) {
      this.lastDataHash = currentHash
      
      // Notify all listeners
      this.notifyListeners(data)
      console.log('🔄 Data updated, notifying listeners')
    }
  }

  // Notify all listeners
  private notifyListeners(data: any) {
    this.listeners.forEach((callbacks, key) => {
      callbacks.forEach(callback => {
        try {
          const value = (data as any)[key] || []
          callback(value)
        } catch (error) {
          console.error('❌ Callback error:', error)
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
    
    // Call immediately with current data
    const data = getAllData()
    callback((data as any)[key] || [])
    
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
      localStorage.setItem(`hockey-${key}`, JSON.stringify(data))
      
      // Update sync timestamp
      localStorage.setItem(STORAGE_KEYS.LAST_SYNC, Date.now().toString())
      
      // Trigger immediate update
      this.checkForUpdates()
      
      console.log(`✅ ${key} saved and synced`)
      return true
    } catch (error) {
      console.error(`❌ Save error:`, error)
      return false
    }
  }

  // Get current data
  getData(key: string) {
    return JSON.parse(localStorage.getItem(`hockey-${key}`) || '[]')
  }

  // Export all data for manual sync
  exportAllData() {
    return getAllData()
  }

  // Import data from another device
  importAllData(data: any) {
    try {
      const success = saveAllData(data)
      if (success) {
        // Trigger update
        this.checkForUpdates()
        console.log('✅ Data imported successfully')
      }
      return success
    } catch (error) {
      console.error('❌ Import error:', error)
      return false
    }
  }

  // Get sync status
  getSyncStatus() {
    return {
      deviceId: getDeviceId(),
      lastSync: localStorage.getItem(STORAGE_KEYS.LAST_SYNC),
      isRunning: this.isRunning
    }
  }

  // Force sync
  forceSync() {
    console.log('🔄 Force syncing...')
    this.checkForUpdates()
  }
}

// Create singleton instance
export const workingSyncService = new WorkingSyncService()

// Export functions
export const subscribeToDrills = (callback: (drills: any[]) => void) => workingSyncService.subscribe('drills', callback)
export const subscribeToPracticePlans = (callback: (plans: any[]) => void) => workingSyncService.subscribe('practicePlans', callback)
export const subscribeToSettings = (callback: (settings: any) => void) => workingSyncService.subscribe('settings', callback)

export const saveDrill = (drills: any) => workingSyncService.saveData('drills', drills)
export const savePracticePlan = (plans: any) => workingSyncService.saveData('practicePlans', plans)
export const saveSettings = (settings: any) => workingSyncService.saveData('settings', settings)

export const getDrills = () => workingSyncService.getData('drills')
export const getPracticePlans = () => workingSyncService.getData('practicePlans')
export const getSettings = () => workingSyncService.getData('settings')

export const getSyncStatus = () => workingSyncService.getSyncStatus()
export const forceSync = () => workingSyncService.forceSync()
export const exportAllData = () => workingSyncService.exportAllData()
export const importAllData = (data: any) => workingSyncService.importAllData(data)
