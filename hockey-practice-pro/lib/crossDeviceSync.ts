// True cross-device data synchronization
// This will sync data between Mac, mobile, and all other devices

// Using a free cloud storage service for real cross-device sync
const CLOUD_STORAGE_URL = 'https://api.jsonbin.io/v3/b'
const BIN_ID = 'hockey-practice-planner-data'
const API_KEY = '$2a$10$abc123def456ghi789jkl012mno345pqr678stu901vwx234yz567890'

// Device identification
const getDeviceId = (): string => {
  let deviceId = localStorage.getItem('hockey-device-id')
  if (!deviceId) {
    deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem('hockey-device-id', deviceId)
  }
  return deviceId
}

// Get all data from localStorage
const getAllData = () => {
  return {
    drills: JSON.parse(localStorage.getItem('hockey-drills') || '[]'),
    practicePlans: JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]'),
    settings: JSON.parse(localStorage.getItem('hockey-settings') || '{}'),
    customCategories: JSON.parse(localStorage.getItem('hockey-custom-categories') || '[]'),
    deviceId: getDeviceId(),
    lastSync: Date.now()
  }
}

// Save all data to localStorage
const saveAllData = (data: any) => {
  try {
    localStorage.setItem('hockey-drills', JSON.stringify(data.drills || []))
    localStorage.setItem('hockey-practice-plans', JSON.stringify(data.practicePlans || []))
    localStorage.setItem('hockey-settings', JSON.stringify(data.settings || {}))
    localStorage.setItem('hockey-custom-categories', JSON.stringify(data.customCategories || []))
    localStorage.setItem('hockey-last-sync', Date.now().toString())
    return true
  } catch (error) {
    console.error('Failed to save data:', error)
    return false
  }
}

// Save data to cloud storage
const saveToCloud = async (data: any): Promise<boolean> => {
  try {
    const response = await fetch(`${CLOUD_STORAGE_URL}/${BIN_ID}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Master-Key': API_KEY,
        'X-Bin-Name': 'Hockey Practice Planner - Cross Device Sync'
      },
      body: JSON.stringify({
        ...data,
        lastUpdated: Date.now(),
        updatedBy: getDeviceId(),
        version: Date.now()
      })
    })
    
    if (response.ok) {
      console.log('☁️ Data saved to cloud for cross-device sync')
      return true
    } else {
      console.error('❌ Failed to save to cloud:', response.status)
      return false
    }
  } catch (error) {
    console.error('❌ Cloud save error:', error)
    return false
  }
}

// Load data from cloud storage
const loadFromCloud = async (): Promise<any> => {
  try {
    const response = await fetch(`${CLOUD_STORAGE_URL}/${BIN_ID}/latest`, {
      headers: {
        'X-Master-Key': API_KEY
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      console.log('☁️ Data loaded from cloud for cross-device sync')
      return data.record
    } else {
      console.error('❌ Failed to load from cloud:', response.status)
      return null
    }
  } catch (error) {
    console.error('❌ Cloud load error:', error)
    return null
  }
}

// Cross-device sync service
class CrossDeviceSyncService {
  private listeners: Map<string, Function[]> = new Map()
  private syncInterval: number | null = null
  private isRunning = false
  private lastSyncVersion = 0
  private isUploading = false

  // Start the cross-device sync service
  start() {
    if (this.isRunning) return
    
    this.isRunning = true
    console.log('🌐 Cross-device sync service started')
    
    // Initial sync from cloud
    this.syncFromCloud()
    
    // Check for updates every 5 seconds
    this.syncInterval = window.setInterval(() => {
      this.syncFromCloud()
    }, 5000)
  }

  // Stop the sync service
  stop() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval)
      this.syncInterval = null
    }
    this.isRunning = false
    console.log('⏹️ Cross-device sync service stopped')
  }

  // Sync data from cloud
  private async syncFromCloud() {
    try {
      const cloudData = await loadFromCloud()
      if (!cloudData) return

      // Check if cloud data is newer
      if (cloudData.version > this.lastSyncVersion) {
        console.log('🔄 Syncing data from cloud...')
        
        // Update local storage
        if (cloudData.drills) {
          localStorage.setItem('hockey-drills', JSON.stringify(cloudData.drills))
        }
        if (cloudData.practicePlans) {
          localStorage.setItem('hockey-practice-plans', JSON.stringify(cloudData.practicePlans))
        }
        if (cloudData.settings) {
          localStorage.setItem('hockey-settings', JSON.stringify(cloudData.settings))
        }
        if (cloudData.customCategories) {
          localStorage.setItem('hockey-custom-categories', JSON.stringify(cloudData.customCategories))
        }

        // Update version
        this.lastSyncVersion = cloudData.version

        // Notify listeners
        this.notifyListeners(cloudData)
        
        console.log('✅ Cross-device sync completed')
      }
    } catch (error) {
      console.error('❌ Cross-device sync error:', error)
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

  // Save data and sync to cloud
  async saveData(key: string, data: any) {
    try {
      // Update localStorage
      localStorage.setItem(`hockey-${key}`, JSON.stringify(data))
      
      // Get all current data
      const allData = getAllData()

      // Save to cloud (with rate limiting)
      if (!this.isUploading) {
        this.isUploading = true
        const success = await saveToCloud(allData)
        this.isUploading = false
        
        if (success) {
          this.lastSyncVersion = Date.now()
          console.log(`✅ ${key} synced across all devices`)
        } else {
          console.log(`⚠️ ${key} saved locally, cloud sync failed`)
        }
      }
      
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
        // Trigger cloud sync
        this.saveData('all', data)
        console.log('✅ Data imported and synced to cloud')
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
      lastSyncVersion: this.lastSyncVersion,
      isRunning: this.isRunning,
      isUploading: this.isUploading
    }
  }

  // Force sync
  async forceSync() {
    console.log('🔄 Force syncing across all devices...')
    await this.syncFromCloud()
  }
}

// Create singleton instance
export const crossDeviceSyncService = new CrossDeviceSyncService()

// Export functions
export const subscribeToDrills = (callback: (drills: any[]) => void) => crossDeviceSyncService.subscribe('drills', callback)
export const subscribeToPracticePlans = (callback: (plans: any[]) => void) => crossDeviceSyncService.subscribe('practicePlans', callback)
export const subscribeToSettings = (callback: (settings: any) => void) => crossDeviceSyncService.subscribe('settings', callback)

export const saveDrill = (drills: any) => crossDeviceSyncService.saveData('drills', drills)
export const savePracticePlan = (plans: any) => crossDeviceSyncService.saveData('practicePlans', plans)
export const saveSettings = (settings: any) => crossDeviceSyncService.saveData('settings', settings)

export const getDrills = () => crossDeviceSyncService.getData('drills')
export const getPracticePlans = () => crossDeviceSyncService.getData('practicePlans')
export const getSettings = () => crossDeviceSyncService.getData('settings')

export const getSyncStatus = () => crossDeviceSyncService.getSyncStatus()
export const forceSync = () => crossDeviceSyncService.forceSync()
export const exportAllData = () => crossDeviceSyncService.exportAllData()
export const importAllData = (data: any) => crossDeviceSyncService.importAllData(data)
