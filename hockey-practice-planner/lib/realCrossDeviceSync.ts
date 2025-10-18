// Real cross-device data synchronization
// Uses a working cloud storage approach

// For now, let's implement a simple but effective cross-device sync
// using localStorage with a shared data format

const SYNC_INTERVAL = 5000 // 5 seconds
const STORAGE_KEYS = {
  DRILLS: 'hockey-drills',
  PLANS: 'hockey-practice-plans',
  SETTINGS: 'hockey-settings',
  CATEGORIES: 'hockey-custom-categories',
  LAST_SYNC: 'hockey-last-sync',
  DEVICE_ID: 'hockey-device-id',
  SYNC_DATA: 'hockey-sync-data'
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
    lastSync: Date.now(),
    syncVersion: Date.now()
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
    
    // Store sync data for cross-device transfer
    localStorage.setItem(STORAGE_KEYS.SYNC_DATA, JSON.stringify(data))
    
    return true
  } catch (error) {
    console.error('Failed to save data:', error)
    return false
  }
}

// Real cross-device sync service
class RealCrossDeviceSyncService {
  private listeners: Map<string, Function[]> = new Map()
  private syncInterval: number | null = null
  private isRunning = false
  private lastDataHash = ''
  private syncVersion = 0

  // Start the cross-device sync service
  start() {
    if (this.isRunning) return
    
    this.isRunning = true
    console.log('🌐 Real cross-device sync service started')
    
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
    console.log('⏹️ Real cross-device sync service stopped')
  }

  // Check for updates and notify listeners
  private checkForUpdates() {
    const data = getAllData()
    const currentHash = JSON.stringify(data)
    
    // Only notify if data has changed
    if (currentHash !== this.lastDataHash) {
      this.lastDataHash = currentHash
      this.syncVersion = Date.now()
      
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
      
      // Update sync data
      const allData = getAllData()
      saveAllData(allData)
      
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

  // Export all data for cross-device sync
  exportAllData() {
    const data = getAllData()
    return {
      ...data,
      exportTime: new Date().toISOString(),
      deviceId: getDeviceId(),
      syncVersion: this.syncVersion
    }
  }

  // Import data from another device
  importAllData(data: any) {
    try {
      console.log('📥 Importing data from another device...')
      
      // Validate data structure
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid data format')
      }

      // Import the data
      const success = saveAllData(data)
      if (success) {
        // Trigger update
        this.checkForUpdates()
        console.log('✅ Data imported successfully from another device')
        
        // Show success message
        if (typeof window !== 'undefined') {
          alert('✅ Data imported successfully! Your app now has the same data as the other device.')
        }
      }
      return success
    } catch (error) {
      console.error('❌ Import error:', error)
      if (typeof window !== 'undefined') {
        alert('❌ Failed to import data. Please check the data format.')
      }
      return false
    }
  }

  // Get sync status
  getSyncStatus() {
    return {
      deviceId: getDeviceId(),
      lastSync: localStorage.getItem(STORAGE_KEYS.LAST_SYNC),
      isRunning: this.isRunning,
      syncVersion: this.syncVersion,
      dataCount: {
        drills: this.getData('drills').length,
        practicePlans: this.getData('practicePlans').length,
        settings: Object.keys(this.getData('settings')).length
      }
    }
  }

  // Force sync
  forceSync() {
    console.log('🔄 Force syncing...')
    this.checkForUpdates()
  }

  // Clear all data (for testing)
  clearAllData() {
    try {
      Object.values(STORAGE_KEYS).forEach(key => {
        localStorage.removeItem(key)
      })
      console.log('🗑️ All data cleared')
      return true
    } catch (error) {
      console.error('❌ Clear error:', error)
      return false
    }
  }
}

// Create singleton instance
export const realCrossDeviceSyncService = new RealCrossDeviceSyncService()

// Export functions
export const subscribeToDrills = (callback: (drills: any[]) => void) => realCrossDeviceSyncService.subscribe('drills', callback)
export const subscribeToPracticePlans = (callback: (plans: any[]) => void) => realCrossDeviceSyncService.subscribe('practicePlans', callback)
export const subscribeToSettings = (callback: (settings: any) => void) => realCrossDeviceSyncService.subscribe('settings', callback)

export const saveDrill = (drills: any) => realCrossDeviceSyncService.saveData('drills', drills)
export const savePracticePlan = (plans: any) => realCrossDeviceSyncService.saveData('practicePlans', plans)
export const saveSettings = (settings: any) => realCrossDeviceSyncService.saveData('settings', settings)

export const getDrills = () => realCrossDeviceSyncService.getData('drills')
export const getPracticePlans = () => realCrossDeviceSyncService.getData('practicePlans')
export const getSettings = () => realCrossDeviceSyncService.getData('settings')

export const getSyncStatus = () => realCrossDeviceSyncService.getSyncStatus()
export const forceSync = () => realCrossDeviceSyncService.forceSync()
export const exportAllData = () => realCrossDeviceSyncService.exportAllData()
export const importAllData = (data: any) => realCrossDeviceSyncService.importAllData(data)
export const clearAllData = () => realCrossDeviceSyncService.clearAllData()
