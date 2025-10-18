// Simple localStorage sync service
// This creates a shared storage system using localStorage with device identification

const DEVICE_ID_KEY = 'hockey-device-id'
const SYNC_DATA_KEY = 'hockey-sync-data'
const LAST_SYNC_KEY = 'hockey-last-sync'

// Generate a unique device ID
const getDeviceId = (): string => {
  let deviceId = localStorage.getItem(DEVICE_ID_KEY)
  if (!deviceId) {
    deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem(DEVICE_ID_KEY, deviceId)
  }
  return deviceId
}

// Get all data from localStorage
export const getAllData = () => {
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
export const saveAllData = (data: any) => {
  try {
    localStorage.setItem('hockey-drills', JSON.stringify(data.drills || []))
    localStorage.setItem('hockey-practice-plans', JSON.stringify(data.practicePlans || []))
    localStorage.setItem('hockey-settings', JSON.stringify(data.settings || {}))
    localStorage.setItem('hockey-custom-categories', JSON.stringify(data.customCategories || []))
    localStorage.setItem(LAST_SYNC_KEY, Date.now().toString())
    return true
  } catch (error) {
    console.error('Failed to save data:', error)
    return false
  }
}

// Check if data needs syncing
export const needsSync = (): boolean => {
  const lastSync = localStorage.getItem(LAST_SYNC_KEY)
  if (!lastSync) return true
  
  const timeSinceLastSync = Date.now() - parseInt(lastSync)
  return timeSinceLastSync > 30000 // 30 seconds
}

// Get sync status
export const getSyncStatus = () => {
  return {
    deviceId: getDeviceId(),
    lastSync: localStorage.getItem(LAST_SYNC_KEY),
    needsSync: needsSync()
  }
}
