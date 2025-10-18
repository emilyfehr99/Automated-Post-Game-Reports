// True automatic cross-device sync
// This will automatically sync data between all devices

// Using a simple cloud storage approach that actually works
const CLOUD_STORAGE_URL = 'https://api.jsonbin.io/v3/b'
const BIN_ID = 'hockey-practice-planner-sync'
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

// Save data to cloud storage
const saveToCloud = async (data: any): Promise<boolean> => {
  try {
    const response = await fetch(`${CLOUD_STORAGE_URL}/${BIN_ID}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Master-Key': API_KEY,
        'X-Bin-Name': 'Hockey Practice Planner - Auto Sync'
      },
      body: JSON.stringify({
        ...data,
        lastUpdated: Date.now(),
        updatedBy: getDeviceId(),
        version: Date.now()
      })
    })
    
    if (response.ok) {
      console.log('☁️ Data saved to cloud')
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
      console.log('☁️ Data loaded from cloud')
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

// Automatic sync service
class AutoSyncService {
  private listeners: Map<string, Function[]> = new Map()
  private syncInterval: NodeJS.Timeout | null = null
  private isRunning = false
  private lastSyncVersion = 0
  private isUploading = false

  // Start automatic sync
  start() {
    if (this.isRunning) return
    
    this.isRunning = true
    console.log('🔄 Auto sync service started')
    
    // Initial sync
    this.syncFromCloud()
    
    // Check for updates every 3 seconds
    this.syncInterval = setInterval(() => {
      this.syncFromCloud()
    }, 3000)
  }

  // Stop automatic sync
  stop() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval)
      this.syncInterval = null
    }
    this.isRunning = false
    console.log('⏹️ Auto sync service stopped')
  }

  // Sync data from cloud
  private async syncFromCloud() {
    try {
      const cloudData = await loadFromCloud()
      if (!cloudData) return

      // Check if cloud data is newer
      if (cloudData.version > this.lastSyncVersion) {
        console.log('🔄 Syncing from cloud...')
        
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
        
        console.log('✅ Auto sync completed')
      }
    } catch (error) {
      console.error('❌ Auto sync error:', error)
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

  // Save data and auto-sync to cloud
  async saveData(key: string, data: any) {
    try {
      // Update localStorage
      localStorage.setItem(`hockey-${key}`, JSON.stringify(data))
      
      // Get all current data
      const allData = {
        drills: JSON.parse(localStorage.getItem('hockey-drills') || '[]'),
        practicePlans: JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]'),
        settings: JSON.parse(localStorage.getItem('hockey-settings') || '{}'),
        customCategories: JSON.parse(localStorage.getItem('hockey-custom-categories') || '[]')
      }

      // Save to cloud (with rate limiting)
      if (!this.isUploading) {
        this.isUploading = true
        const success = await saveToCloud(allData)
        this.isUploading = false
        
        if (success) {
          this.lastSyncVersion = Date.now()
          console.log(`✅ ${key} auto-synced to cloud`)
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
    console.log('🔄 Force syncing...')
    await this.syncFromCloud()
  }
}

// Create singleton instance
export const autoSyncService = new AutoSyncService()

// Export functions
export const subscribeToDrills = (callback: (drills: any[]) => void) => autoSyncService.subscribe('drills', callback)
export const subscribeToPracticePlans = (callback: (plans: any[]) => void) => autoSyncService.subscribe('practicePlans', callback)
export const subscribeToSettings = (callback: (settings: any) => void) => autoSyncService.subscribe('settings', callback)

export const saveDrill = (drills: any) => autoSyncService.saveData('drills', drills)
export const savePracticePlan = (plans: any) => autoSyncService.saveData('practicePlans', plans)
export const saveSettings = (settings: any) => autoSyncService.saveData('settings', settings)

export const getDrills = () => autoSyncService.getData('drills')
export const getPracticePlans = () => autoSyncService.getData('practicePlans')
export const getSettings = () => autoSyncService.getData('settings')

export const getSyncStatus = () => autoSyncService.getSyncStatus()
export const forceSync = () => autoSyncService.forceSync()
