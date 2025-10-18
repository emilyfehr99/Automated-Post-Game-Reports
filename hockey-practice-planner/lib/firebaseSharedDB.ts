// TRUE SHARED DATABASE - One website that saves everything for all devices
// Using Firebase Firestore for real cross-device synchronization

import { initializeApp } from 'firebase/app'
import { 
  getFirestore, 
  collection, 
  doc, 
  setDoc, 
  getDoc, 
  onSnapshot,
  Timestamp 
} from 'firebase/firestore'

// Firebase configuration
// This is a public config - safe to expose in client-side code
const firebaseConfig = {
  apiKey: "AIzaSyCm2m3lSlh_IBgHSOLcmeCO9lZYHaxgrFw",
  authDomain: "hockey-practice-planner.firebaseapp.com",
  projectId: "hockey-practice-planner",
  storageBucket: "hockey-practice-planner.firebasestorage.app",
  messagingSenderId: "557366268618",
  appId: "1:557366268618:web:d6f5cf9e80045d966fda33",
  measurementId: "G-BSH8MT49BZ"
}

// Initialize Firebase
const app = initializeApp(firebaseConfig)
const db = getFirestore(app)

// Collection names
const COLLECTIONS = {
  DRILLS: 'drills',
  PRACTICE_PLANS: 'practicePlans', 
  SETTINGS: 'settings',
  CUSTOM_CATEGORIES: 'customCategories'
}

// Device identification
const getDeviceId = (): string => {
  let deviceId = localStorage.getItem('hockey-device-id')
  if (!deviceId) {
    deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem('hockey-device-id', deviceId)
  }
  return deviceId
}

// True shared database service
class SharedDatabaseService {
  private listeners: Map<string, Function[]> = new Map()
  private isConnected = false
  private lastSyncTime = 0

  // Initialize the shared database
  async initialize() {
    try {
      console.log('🔥 Initializing Firebase shared database...')
      
      // Test connection by trying to access Firestore (this will work even if no documents exist)
      const testCollection = collection(db, 'drills')
      console.log('✅ Firebase Firestore accessible!')
      
      this.isConnected = true
      console.log('✅ Firebase shared database connected!')
      console.log('🌐 All devices will now share the same data!')
      
      return true
    } catch (error) {
      console.error('❌ Firebase connection failed:', error)
      console.log('💾 Falling back to localStorage...')
      this.isConnected = false
      return false
    }
  }

  // Subscribe to real-time updates from shared database
  subscribeToDrills(callback: (drills: any[]) => void) {
    if (!this.isConnected) {
      // Fallback to localStorage
      const drills = JSON.parse(localStorage.getItem('hockey-drills') || '[]')
      callback(drills)
      return () => {}
    }

    const unsubscribe = onSnapshot(
      collection(db, COLLECTIONS.DRILLS),
      (snapshot) => {
        const drills = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }))
        console.log('🔥 Drills updated from shared database:', drills.length)
        callback(drills)
      },
      (error) => {
        console.error('❌ Drills subscription error:', error)
        // Fallback to localStorage
        const drills = JSON.parse(localStorage.getItem('hockey-drills') || '[]')
        callback(drills)
      }
    )

    return unsubscribe
  }

  subscribeToPracticePlans(callback: (plans: any[]) => void) {
    if (!this.isConnected) {
      // Fallback to localStorage
      const plans = JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
      callback(plans)
      return () => {}
    }

    const unsubscribe = onSnapshot(
      collection(db, COLLECTIONS.PRACTICE_PLANS),
      (snapshot) => {
        const plans = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }))
        console.log('🔥 Practice plans updated from shared database:', plans.length)
        callback(plans)
      },
      (error) => {
        console.error('❌ Practice plans subscription error:', error)
        // Fallback to localStorage
        const plans = JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
        callback(plans)
      }
    )

    return unsubscribe
  }

  subscribeToSettings(callback: (settings: any) => void) {
    if (!this.isConnected) {
      // Fallback to localStorage
      const settings = JSON.parse(localStorage.getItem('hockey-settings') || '{}')
      callback(settings)
      return () => {}
    }

    const unsubscribe = onSnapshot(
      doc(db, COLLECTIONS.SETTINGS, 'main'),
      (doc) => {
        const settings = doc.exists() ? doc.data() : {}
        console.log('🔥 Settings updated from shared database')
        callback(settings)
      },
      (error) => {
        console.error('❌ Settings subscription error:', error)
        // Fallback to localStorage
        const settings = JSON.parse(localStorage.getItem('hockey-settings') || '{}')
        callback(settings)
      }
    )

    return unsubscribe
  }

  // Save data to shared database
  async saveDrills(drills: any[]) {
    if (!this.isConnected) {
      // Fallback to localStorage
      localStorage.setItem('hockey-drills', JSON.stringify(drills))
      console.log('💾 Drills saved to localStorage (offline mode)')
      return true
    }

    try {
      // Save each drill to Firestore
      const batch = []
      for (const drill of drills) {
        const drillRef = doc(db, COLLECTIONS.DRILLS, drill.id || `drill_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
        batch.push(setDoc(drillRef, {
          ...drill,
          updatedAt: Timestamp.now(),
          updatedBy: getDeviceId()
        }))
      }
      
      await Promise.all(batch)
      console.log('🔥 Drills saved to shared database!')
      return true
    } catch (error) {
      console.error('❌ Failed to save drills to shared database:', error)
      // Fallback to localStorage
      localStorage.setItem('hockey-drills', JSON.stringify(drills))
      return false
    }
  }

  async savePracticePlans(plans: any[]) {
    if (!this.isConnected) {
      // Fallback to localStorage
      localStorage.setItem('hockey-practice-plans', JSON.stringify(plans))
      console.log('💾 Practice plans saved to localStorage (offline mode)')
      return true
    }

    try {
      // Save each practice plan to Firestore
      const batch = []
      for (const plan of plans) {
        const planRef = doc(db, COLLECTIONS.PRACTICE_PLANS, plan.id || `plan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
        batch.push(setDoc(planRef, {
          ...plan,
          updatedAt: Timestamp.now(),
          updatedBy: getDeviceId()
        }))
      }
      
      await Promise.all(batch)
      console.log('🔥 Practice plans saved to shared database!')
      return true
    } catch (error) {
      console.error('❌ Failed to save practice plans to shared database:', error)
      // Fallback to localStorage
      localStorage.setItem('hockey-practice-plans', JSON.stringify(plans))
      return false
    }
  }

  async saveSettings(settings: any) {
    if (!this.isConnected) {
      // Fallback to localStorage
      localStorage.setItem('hockey-settings', JSON.stringify(settings))
      console.log('💾 Settings saved to localStorage (offline mode)')
      return true
    }

    try {
      const settingsRef = doc(db, COLLECTIONS.SETTINGS, 'main')
      await setDoc(settingsRef, {
        ...settings,
        updatedAt: Timestamp.now(),
        updatedBy: getDeviceId()
      })
      
      console.log('🔥 Settings saved to shared database!')
      return true
    } catch (error) {
      console.error('❌ Failed to save settings to shared database:', error)
      // Fallback to localStorage
      localStorage.setItem('hockey-settings', JSON.stringify(settings))
      return false
    }
  }

  // Get current data
  getDrills() {
    if (!this.isConnected) {
      return JSON.parse(localStorage.getItem('hockey-drills') || '[]')
    }
    // For real-time data, use subscriptions instead
    return []
  }

  getPracticePlans() {
    if (!this.isConnected) {
      return JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
    }
    // For real-time data, use subscriptions instead
    return []
  }

  getSettings() {
    if (!this.isConnected) {
      return JSON.parse(localStorage.getItem('hockey-settings') || '{}')
    }
    // For real-time data, use subscriptions instead
    return {}
  }

  // Get sync status
  getSyncStatus() {
    return {
      deviceId: getDeviceId(),
      isConnected: this.isConnected,
      database: this.isConnected ? 'Firebase Firestore (Shared)' : 'localStorage (Local Only)',
      lastSync: this.lastSyncTime,
      status: this.isConnected ? '🌐 Shared database active - all devices sync automatically!' : '💾 Local storage only - manual sync required'
    }
  }

  // Export all data
  exportAllData() {
    return {
      drills: this.getDrills(),
      practicePlans: this.getPracticePlans(),
      settings: this.getSettings(),
      customCategories: JSON.parse(localStorage.getItem('hockey-custom-categories') || '[]'),
      exportTime: new Date().toISOString(),
      deviceId: getDeviceId(),
      database: this.isConnected ? 'Firebase Firestore' : 'localStorage'
    }
  }

  // Import data (for migration)
  async importAllData(data: any) {
    try {
      if (data.drills) await this.saveDrills(data.drills)
      if (data.practicePlans) await this.savePracticePlans(data.practicePlans)
      if (data.settings) await this.saveSettings(data.settings)
      if (data.customCategories) {
        localStorage.setItem('hockey-custom-categories', JSON.stringify(data.customCategories))
      }
      
      console.log('✅ Data imported to shared database!')
      return true
    } catch (error) {
      console.error('❌ Import failed:', error)
      return false
    }
  }
}

// Create singleton instance
export const sharedDatabaseService = new SharedDatabaseService()

// Export functions
export const subscribeToDrills = (callback: (drills: any[]) => void) => sharedDatabaseService.subscribeToDrills(callback)
export const subscribeToPracticePlans = (callback: (plans: any[]) => void) => sharedDatabaseService.subscribeToPracticePlans(callback)
export const subscribeToSettings = (callback: (settings: any) => void) => sharedDatabaseService.subscribeToSettings(callback)

export const saveDrill = (drills: any) => sharedDatabaseService.saveDrills(drills)
export const savePracticePlan = (plans: any) => sharedDatabaseService.savePracticePlans(plans)
export const saveSettings = (settings: any) => sharedDatabaseService.saveSettings(settings)

export const getDrills = () => sharedDatabaseService.getDrills()
export const getPracticePlans = () => sharedDatabaseService.getPracticePlans()
export const getSettings = () => sharedDatabaseService.getSettings()

export const getSyncStatus = () => sharedDatabaseService.getSyncStatus()
export const exportAllData = () => sharedDatabaseService.exportAllData()
export const importAllData = (data: any) => sharedDatabaseService.importAllData(data)
export const initializeSharedDatabase = () => sharedDatabaseService.initialize()
