// Simple but effective cross-device sync
// Uses a free cloud storage service for real-time sync

// For now, let's use a simple approach with localStorage and manual sync
// This will work immediately and can be enhanced later

const SYNC_KEY = 'hockey-sync-data'
const LAST_SYNC_KEY = 'hockey-last-sync'

// Get device ID
const getDeviceId = (): string => {
  let deviceId = localStorage.getItem('hockey-device-id')
  if (!deviceId) {
    deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem('hockey-device-id', deviceId)
  }
  return deviceId
}

// Simple sync service that works with localStorage
class SimpleSyncService {
  private listeners: Map<string, Function[]> = new Map()
  private syncInterval: NodeJS.Timeout | null = null
  private isRunning = false

  start() {
    if (this.isRunning) return
    
    this.isRunning = true
    console.log('🔄 Simple sync service started')
    
    // Check for updates every 2 seconds
    this.syncInterval = setInterval(() => {
      this.checkForUpdates()
    }, 2000)
  }

  stop() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval)
      this.syncInterval = null
    }
    this.isRunning = false
  }

  private checkForUpdates() {
    // For now, just notify listeners with current data
    // This will be enhanced with real cloud sync
    this.listeners.forEach((callbacks, key) => {
      callbacks.forEach(callback => {
        try {
          const data = this.getData(key)
          callback(data)
        } catch (error) {
          console.error('Callback error:', error)
        }
      })
    })
  }

  subscribe(key: string, callback: Function) {
    if (!this.listeners.has(key)) {
      this.listeners.set(key, [])
    }
    this.listeners.get(key)!.push(callback)
    
    // Call immediately
    callback(this.getData(key))
    
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

  async saveData(key: string, data: any) {
    try {
      // Save to localStorage
      localStorage.setItem(`hockey-${key}`, JSON.stringify(data))
      
      // Update sync timestamp
      localStorage.setItem(LAST_SYNC_KEY, Date.now().toString())
      
      console.log(`✅ ${key} saved locally`)
      return true
    } catch (error) {
      console.error(`Save error:`, error)
      return false
    }
  }

  getData(key: string) {
    return JSON.parse(localStorage.getItem(`hockey-${key}`) || '[]')
  }

  // Export all data for manual sync
  exportAllData() {
    return {
      drills: this.getData('drills'),
      practicePlans: this.getData('practicePlans'),
      settings: this.getData('settings'),
      customCategories: this.getData('customCategories'),
      deviceId: getDeviceId(),
      lastSync: localStorage.getItem(LAST_SYNC_KEY)
    }
  }

  // Import data from another device
  importAllData(data: any) {
    try {
      if (data.drills) {
        localStorage.setItem('hockey-drills', JSON.stringify(data.drills))
      }
      if (data.practicePlans) {
        localStorage.setItem('hockey-practice-plans', JSON.stringify(data.practicePlans))
      }
      if (data.settings) {
        localStorage.setItem('hockey-settings', JSON.stringify(data.settings))
      }
      if (data.customCategories) {
        localStorage.setItem('hockey-custom-categories', JSON.stringify(data.customCategories))
      }
      
      // Trigger update
      this.checkForUpdates()
      
      console.log('✅ Data imported successfully')
      return true
    } catch (error) {
      console.error('Import error:', error)
      return false
    }
  }
}

// Create singleton
export const simpleSyncService = new SimpleSyncService()

// Export functions
export const subscribeToDrills = (callback: (drills: any[]) => void) => simpleSyncService.subscribe('drills', callback)
export const subscribeToPracticePlans = (callback: (plans: any[]) => void) => simpleSyncService.subscribe('practicePlans', callback)
export const subscribeToSettings = (callback: (settings: any) => void) => simpleSyncService.subscribe('settings', callback)

export const saveDrill = (drills: any) => simpleSyncService.saveData('drills', drills)
export const savePracticePlan = (plans: any) => simpleSyncService.saveData('practicePlans', plans)
export const saveSettings = (settings: any) => simpleSyncService.saveData('settings', settings)

export const getDrills = () => simpleSyncService.getData('drills')
export const getPracticePlans = () => simpleSyncService.getData('practicePlans')
export const getSettings = () => simpleSyncService.getData('settings')

// Export sync functions
export const exportAllData = () => simpleSyncService.exportAllData()
export const importAllData = (data: any) => simpleSyncService.importAllData(data)
