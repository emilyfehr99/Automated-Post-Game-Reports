// Real cross-device sync using cloud storage
// This creates a shared data store that all devices can access

const CLOUD_STORAGE_URL = 'https://api.jsonbin.io/v3/b'
const BIN_ID = 'hockey-practice-planner-data'
const API_KEY = '$2a$10$your-api-key-here' // This would be a real API key

// Device identification
const getDeviceId = (): string => {
  let deviceId = localStorage.getItem('hockey-device-id')
  if (!deviceId) {
    deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem('hockey-device-id', deviceId)
  }
  return deviceId
}

// Save data to cloud
const saveToCloud = async (data: any): Promise<boolean> => {
  try {
    const response = await fetch(`${CLOUD_STORAGE_URL}/${BIN_ID}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Master-Key': API_KEY,
        'X-Bin-Name': 'Hockey Practice Planner Data'
      },
      body: JSON.stringify({
        ...data,
        lastUpdated: Date.now(),
        updatedBy: getDeviceId()
      })
    })
    
    if (response.ok) {
      console.log('✅ Data saved to cloud')
      return true
    } else {
      console.error('Failed to save to cloud:', response.status)
      return false
    }
  } catch (error) {
    console.error('Error saving to cloud:', error)
    return false
  }
}

// Load data from cloud
const loadFromCloud = async (): Promise<any> => {
  try {
    const response = await fetch(`${CLOUD_STORAGE_URL}/${BIN_ID}/latest`, {
      headers: {
        'X-Master-Key': API_KEY
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      console.log('✅ Data loaded from cloud')
      return data.record
    } else {
      console.error('Failed to load from cloud:', response.status)
      return null
    }
  } catch (error) {
    console.error('Error loading from cloud:', error)
    return null
  }
}

// Cloud sync service
class CloudSyncService {
  private listeners: Map<string, Function[]> = new Map()
  private syncInterval: NodeJS.Timeout | null = null
  private isRunning = false
  private lastSyncTime = 0

  // Start the sync service
  start() {
    if (this.isRunning) return
    
    this.isRunning = true
    console.log('☁️ Cloud sync service started')
    
    // Initial sync
    this.syncFromCloud()
    
    // Check for updates periodically
    this.syncInterval = setInterval(() => {
      this.syncFromCloud()
    }, 5000) // Check every 5 seconds
  }

  // Stop the sync service
  stop() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval)
      this.syncInterval = null
    }
    this.isRunning = false
    console.log('⏹️ Cloud sync service stopped')
  }

  // Sync data from cloud
  private async syncFromCloud() {
    try {
      const cloudData = await loadFromCloud()
      if (!cloudData) return

      // Check if data is newer than our last sync
      if (cloudData.lastUpdated > this.lastSyncTime) {
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

        // Update last sync time
        this.lastSyncTime = cloudData.lastUpdated

        // Notify listeners
        this.notifyListeners(cloudData)
      }
    } catch (error) {
      console.error('Error syncing from cloud:', error)
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

  // Save data and sync to cloud
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

      // Save to cloud
      const success = await saveToCloud(allData)
      if (success) {
        this.lastSyncTime = Date.now()
        console.log(`✅ ${key} saved and synced to cloud`)
      } else {
        console.log(`⚠️ ${key} saved locally, cloud sync failed`)
      }
      
      return success
    } catch (error) {
      console.error(`Failed to save ${key}:`, error)
      return false
    }
  }

  // Get current data
  getData(key: string) {
    return JSON.parse(localStorage.getItem(`hockey-${key}`) || '[]')
  }

  // Export all data
  exportData() {
    return {
      drills: JSON.parse(localStorage.getItem('hockey-drills') || '[]'),
      practicePlans: JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]'),
      settings: JSON.parse(localStorage.getItem('hockey-settings') || '{}'),
      customCategories: JSON.parse(localStorage.getItem('hockey-custom-categories') || '[]'),
      deviceId: getDeviceId(),
      lastSync: this.lastSyncTime
    }
  }

  // Import data
  importData(data: any) {
    try {
      if (data.drills) localStorage.setItem('hockey-drills', JSON.stringify(data.drills))
      if (data.practicePlans) localStorage.setItem('hockey-practice-plans', JSON.stringify(data.practicePlans))
      if (data.settings) localStorage.setItem('hockey-settings', JSON.stringify(data.settings))
      if (data.customCategories) localStorage.setItem('hockey-custom-categories', JSON.stringify(data.customCategories))
      return true
    } catch (error) {
      console.error('Failed to import data:', error)
      return false
    }
  }

  // Get sync status
  getSyncStatus() {
    return {
      deviceId: getDeviceId(),
      lastSync: this.lastSyncTime,
      isRunning: this.isRunning
    }
  }
}

// Create singleton instance
export const cloudSyncService = new CloudSyncService()

// Export individual functions for compatibility
export const subscribeToDrills = (callback: (drills: any[]) => void) => cloudSyncService.subscribe('drills', callback)
export const subscribeToPracticePlans = (callback: (plans: any[]) => void) => cloudSyncService.subscribe('practicePlans', callback)
export const subscribeToSettings = (callback: (settings: any) => void) => cloudSyncService.subscribe('settings', callback)

export const saveDrill = (drills: any) => cloudSyncService.saveData('drills', drills)
export const savePracticePlan = (plans: any) => cloudSyncService.saveData('practicePlans', plans)
export const saveSettings = (settings: any) => cloudSyncService.saveData('settings', settings)

export const getDrills = () => cloudSyncService.getData('drills')
export const getPracticePlans = () => cloudSyncService.getData('practicePlans')
export const getSettings = () => cloudSyncService.getData('settings')
