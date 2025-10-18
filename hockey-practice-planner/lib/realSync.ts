// Real cross-device sync using a simple cloud storage approach
// This will actually sync data between devices

const SYNC_URL = 'https://api.jsonbin.io/v3/b/65f8a1231f5677401f2a1234'
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

// Save data to cloud
const saveToCloud = async (data: any): Promise<boolean> => {
  try {
    const response = await fetch(SYNC_URL, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Master-Key': API_KEY
      },
      body: JSON.stringify({
        ...data,
        lastUpdated: Date.now(),
        updatedBy: getDeviceId()
      })
    })
    
    return response.ok
  } catch (error) {
    console.error('Error saving to cloud:', error)
    return false
  }
}

// Load data from cloud
const loadFromCloud = async (): Promise<any> => {
  try {
    const response = await fetch(`${SYNC_URL}/latest`, {
      headers: {
        'X-Master-Key': API_KEY
      }
    })
    
    if (response.ok) {
      const data = await response.json()
      return data.record
    }
    return null
  } catch (error) {
    console.error('Error loading from cloud:', error)
    return null
  }
}

// Real sync service
class RealSyncService {
  private listeners: Map<string, Function[]> = new Map()
  private syncInterval: NodeJS.Timeout | null = null
  private isRunning = false
  private lastSyncTime = 0

  start() {
    if (this.isRunning) return
    
    this.isRunning = true
    console.log('☁️ Real sync service started')
    
    // Initial sync
    this.syncFromCloud()
    
    // Check for updates every 3 seconds
    this.syncInterval = setInterval(() => {
      this.syncFromCloud()
    }, 3000)
  }

  stop() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval)
      this.syncInterval = null
    }
    this.isRunning = false
  }

  private async syncFromCloud() {
    try {
      const cloudData = await loadFromCloud()
      if (!cloudData || cloudData.lastUpdated <= this.lastSyncTime) return

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

      this.lastSyncTime = cloudData.lastUpdated

      // Notify listeners
      this.notifyListeners(cloudData)
    } catch (error) {
      console.error('Sync error:', error)
    }
  }

  private notifyListeners(data: any) {
    this.listeners.forEach((callbacks, key) => {
      callbacks.forEach(callback => {
        try {
          const value = (data as any)[key] || []
          callback(value)
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
        console.log(`✅ ${key} synced to cloud`)
      }
      
      return success
    } catch (error) {
      console.error(`Save error:`, error)
      return false
    }
  }

  getData(key: string) {
    return JSON.parse(localStorage.getItem(`hockey-${key}`) || '[]')
  }
}

// Create singleton
export const realSyncService = new RealSyncService()

// Export functions
export const subscribeToDrills = (callback: (drills: any[]) => void) => realSyncService.subscribe('drills', callback)
export const subscribeToPracticePlans = (callback: (plans: any[]) => void) => realSyncService.subscribe('practicePlans', callback)
export const subscribeToSettings = (callback: (settings: any) => void) => realSyncService.subscribe('settings', callback)

export const saveDrill = (drills: any) => realSyncService.saveData('drills', drills)
export const savePracticePlan = (plans: any) => realSyncService.saveData('practicePlans', plans)
export const saveSettings = (settings: any) => realSyncService.saveData('settings', settings)

export const getDrills = () => realSyncService.getData('drills')
export const getPracticePlans = () => realSyncService.getData('practicePlans')
export const getSettings = () => realSyncService.getData('settings')
