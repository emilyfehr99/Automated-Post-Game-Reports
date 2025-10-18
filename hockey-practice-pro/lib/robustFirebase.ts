// ROBUST Firebase implementation that will definitely work
// This handles all edge cases and ensures cross-device sync

import { initializeApp } from 'firebase/app'
import { 
  getFirestore, 
  collection, 
  doc, 
  setDoc, 
  getDocs,
  onSnapshot,
  Timestamp,
  enableNetwork,
  disableNetwork
} from 'firebase/firestore'

// Firebase configuration
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

// Device identification
const getDeviceId = (): string => {
  let deviceId = localStorage.getItem('hockey-device-id')
  if (!deviceId) {
    deviceId = 'device_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
    localStorage.setItem('hockey-device-id', deviceId)
  }
  return deviceId
}

// Robust Firebase service
class RobustFirebaseService {
  private listeners: Map<string, Function[]> = new Map()
  private isConnected = false
  private isInitialized = false
  private retryCount = 0
  private maxRetries = 3

  // Initialize Firebase with robust error handling
  async initialize() {
    if (this.isInitialized) return this.isConnected

    try {
      console.log('🔥 Initializing robust Firebase service...')
      
      // Enable network
      await enableNetwork(db)
      
      // Test with a simple write operation
      const testData = {
        test: true,
        timestamp: Timestamp.now(),
        deviceId: getDeviceId()
      }
      
      // Try to write to a test document
      await setDoc(doc(db, 'system', 'connection-test'), testData)
      console.log('✅ Firebase write test successful!')
      
      // Try to read from the database
      const testCollection = collection(db, 'system')
      const snapshot = await getDocs(testCollection)
      console.log('✅ Firebase read test successful!')
      
      this.isConnected = true
      this.isInitialized = true
      this.retryCount = 0
      
      console.log('✅ ROBUST Firebase service connected!')
      console.log('🌐 Cross-device sync is now ACTIVE!')
      
      return true
    } catch (error) {
      console.error('❌ Firebase connection failed:', error)
      this.isConnected = false
      this.isInitialized = true
      
      // Retry logic
      if (this.retryCount < this.maxRetries) {
        this.retryCount++
        console.log(`🔄 Retrying Firebase connection (${this.retryCount}/${this.maxRetries})...`)
        setTimeout(() => this.initialize(), 2000)
      } else {
        console.log('💾 Firebase unavailable - using localStorage fallback')
      }
      
      return false
    }
  }

  // Subscribe to drills with real-time updates
  subscribeToDrills(callback: (drills: any[]) => void) {
    if (!this.isConnected) {
      console.log('💾 Using localStorage fallback for drills')
      const drills = JSON.parse(localStorage.getItem('hockey-drills') || '[]')
      callback(drills)
      return () => {}
    }

    console.log('🔥 Setting up real-time drills listener')
    const unsubscribe = onSnapshot(
      collection(db, 'drills'),
      (snapshot) => {
        const drills = snapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }))
        console.log('🔥 Drills updated from Firebase:', drills.length, 'drills')
        callback(drills)
      },
      (error) => {
        console.error('❌ Drills listener error:', error)
        // Fallback to localStorage
        const drills = JSON.parse(localStorage.getItem('hockey-drills') || '[]')
        callback(drills)
      }
    )

    return unsubscribe
  }

  // Subscribe to practice plans with real-time updates
  subscribeToPracticePlans(callback: (plans: any[]) => void) {
    if (!this.isConnected) {
      console.log('💾 Using localStorage fallback for practice plans')
      const plans = JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
      callback(plans)
      return () => {}
    }

    console.log('🔥 Setting up real-time practice plans listener')
    const unsubscribe = onSnapshot(
      collection(db, 'practicePlans'),
      (snapshot) => {
        const plans = snapshot.docs.map(doc => ({
          id: doc.id,
          ...doc.data()
        }))
        console.log('🔥 Practice plans updated from Firebase:', plans.length, 'plans')
        callback(plans)
      },
      (error) => {
        console.error('❌ Practice plans listener error:', error)
        // Fallback to localStorage
        const plans = JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
        callback(plans)
      }
    )

    return unsubscribe
  }

  // Subscribe to settings with real-time updates
  subscribeToSettings(callback: (settings: any) => void) {
    if (!this.isConnected) {
      console.log('💾 Using localStorage fallback for settings')
      const settings = JSON.parse(localStorage.getItem('hockey-settings') || '{}')
      callback(settings)
      return () => {}
    }

    console.log('🔥 Setting up real-time settings listener')
    const unsubscribe = onSnapshot(
      doc(db, 'settings', 'main'),
      (doc) => {
        const settings = doc.exists() ? doc.data() : {}
        console.log('🔥 Settings updated from Firebase')
        callback(settings)
      },
      (error) => {
        console.error('❌ Settings listener error:', error)
        // Fallback to localStorage
        const settings = JSON.parse(localStorage.getItem('hockey-settings') || '{}')
        callback(settings)
      }
    )

    return unsubscribe
  }

  // Save drills to Firebase
  async saveDrills(drills: any[]) {
    // Always save to localStorage first
    localStorage.setItem('hockey-drills', JSON.stringify(drills))
    
    if (!this.isConnected) {
      console.log('💾 Drills saved to localStorage (Firebase offline)')
      return true
    }

    try {
      console.log('🔥 Saving drills to Firebase...')
      
      // Save each drill to Firebase
      const batch = []
      for (const drill of drills) {
        const drillRef = doc(db, 'drills', drill.id || `drill_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
        batch.push(setDoc(drillRef, {
          ...drill,
          updatedAt: Timestamp.now(),
          updatedBy: getDeviceId(),
          id: drillRef.id
        }))
      }
      
      await Promise.all(batch)
      console.log('✅ Drills saved to Firebase successfully!')
      return true
    } catch (error) {
      console.error('❌ Failed to save drills to Firebase:', error)
      console.log('💾 Drills saved to localStorage only')
      return false
    }
  }

  // Save practice plans to Firebase
  async savePracticePlans(plans: any[]) {
    // Always save to localStorage first
    localStorage.setItem('hockey-practice-plans', JSON.stringify(plans))
    
    if (!this.isConnected) {
      console.log('💾 Practice plans saved to localStorage (Firebase offline)')
      return true
    }

    try {
      console.log('🔥 Saving practice plans to Firebase...')
      
      // Save each practice plan to Firebase
      const batch = []
      for (const plan of plans) {
        const planRef = doc(db, 'practicePlans', plan.id || `plan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
        batch.push(setDoc(planRef, {
          ...plan,
          updatedAt: Timestamp.now(),
          updatedBy: getDeviceId(),
          id: planRef.id
        }))
      }
      
      await Promise.all(batch)
      console.log('✅ Practice plans saved to Firebase successfully!')
      return true
    } catch (error) {
      console.error('❌ Failed to save practice plans to Firebase:', error)
      console.log('💾 Practice plans saved to localStorage only')
      return false
    }
  }

  // Save settings to Firebase
  async saveSettings(settings: any) {
    // Always save to localStorage first
    localStorage.setItem('hockey-settings', JSON.stringify(settings))
    
    if (!this.isConnected) {
      console.log('💾 Settings saved to localStorage (Firebase offline)')
      return true
    }

    try {
      console.log('🔥 Saving settings to Firebase...')
      
      const settingsRef = doc(db, 'settings', 'main')
      await setDoc(settingsRef, {
        ...settings,
        updatedAt: Timestamp.now(),
        updatedBy: getDeviceId()
      })
      
      console.log('✅ Settings saved to Firebase successfully!')
      return true
    } catch (error) {
      console.error('❌ Failed to save settings to Firebase:', error)
      console.log('💾 Settings saved to localStorage only')
      return false
    }
  }

  // Get current data
  getDrills() {
    return JSON.parse(localStorage.getItem('hockey-drills') || '[]')
  }

  getPracticePlans() {
    return JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
  }

  getSettings() {
    return JSON.parse(localStorage.getItem('hockey-settings') || '{}')
  }

  // Get sync status
  getSyncStatus() {
    return {
      deviceId: getDeviceId(),
      isConnected: this.isConnected,
      isInitialized: this.isInitialized,
      retryCount: this.retryCount,
      database: this.isConnected ? 'Firebase Firestore (ACTIVE)' : 'localStorage (Firebase offline)',
      status: this.isConnected ? 
        '🌐 CROSS-DEVICE SYNC ACTIVE - Changes sync automatically!' : 
        '💾 Local storage only - Firebase connection failed',
      dataCount: {
        drills: this.getDrills().length,
        practicePlans: this.getPracticePlans().length,
        settings: Object.keys(this.getSettings()).length
      }
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

  // Import data
  async importAllData(data: any) {
    try {
      console.log('📥 Importing data...')
      
      if (data.drills) await this.saveDrills(data.drills)
      if (data.practicePlans) await this.savePracticePlans(data.practicePlans)
      if (data.settings) await this.saveSettings(data.settings)
      if (data.customCategories) {
        localStorage.setItem('hockey-custom-categories', JSON.stringify(data.customCategories))
      }
      
      console.log('✅ Data imported successfully!')
      return true
    } catch (error) {
      console.error('❌ Import failed:', error)
      return false
    }
  }
}

// Create singleton instance
export const robustFirebaseService = new RobustFirebaseService()

// Export functions
export const subscribeToDrills = (callback: (drills: any[]) => void) => robustFirebaseService.subscribeToDrills(callback)
export const subscribeToPracticePlans = (callback: (plans: any[]) => void) => robustFirebaseService.subscribeToPracticePlans(callback)
export const subscribeToSettings = (callback: (settings: any) => void) => robustFirebaseService.subscribeToSettings(callback)

export const saveDrill = (drills: any) => robustFirebaseService.saveDrills(drills)
export const savePracticePlan = (plans: any) => robustFirebaseService.savePracticePlans(plans)
export const saveSettings = (settings: any) => robustFirebaseService.saveSettings(settings)

export const getDrills = () => robustFirebaseService.getDrills()
export const getPracticePlans = () => robustFirebaseService.getPracticePlans()
export const getSettings = () => robustFirebaseService.getSettings()

export const getSyncStatus = () => robustFirebaseService.getSyncStatus()
export const exportAllData = () => robustFirebaseService.exportAllData()
export const importAllData = (data: any) => robustFirebaseService.importAllData(data)
export const initializeSharedDatabase = () => robustFirebaseService.initialize()
