// SIMPLE Firebase implementation - focuses on reliability
import { initializeApp } from 'firebase/app'
import { 
  getFirestore, 
  collection, 
  doc, 
  setDoc, 
  getDocs,
  onSnapshot
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
let app: any = null
let db: any = null
let isConnected = false

try {
  app = initializeApp(firebaseConfig)
  db = getFirestore(app)
  console.log('🔥 Firebase initialized successfully')
} catch (error) {
  console.error('❌ Firebase initialization failed:', error)
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

// Initialize Firebase
async function initializeFirebase(): Promise<boolean> {
  try {
    console.log('🔥 Initializing Firebase...')
    
    if (!firebaseConfig.apiKey) {
      throw new Error('Firebase config missing')
    }
    
    const app = initializeApp(firebaseConfig)
    db = getFirestore(app)
    
    // Test the connection with a simple read
    console.log('🔥 Testing Firebase connection...')
    const testRef = collection(db, 'drills')
    const testSnapshot = await getDocs(testRef)
    console.log(`✅ Firebase connected - found ${testSnapshot.docs.length} drills`)
    
    isConnected = true
    console.log('🌐 Firebase connected - cross-device sync active!')
    
    // Set up periodic connection check
    setInterval(async () => {
      try {
        const testSnapshot = await getDocs(collection(db!, 'drills'))
        if (!isConnected) {
          console.log('🔄 Firebase connection restored!')
          isConnected = true
        }
      } catch (error) {
        if (isConnected) {
          console.log('⚠️ Firebase connection lost, retrying...')
          isConnected = false
        }
      }
    }, 30000) // Check every 30 seconds
    
    return true
  } catch (error) {
    console.error('❌ Firebase initialization failed:', error)
    isConnected = false
    console.log('💾 Firebase offline - using localStorage only')
    return false
  }
}

// Subscribe to drills
function subscribeToDrills(callback: (drills: any[]) => void) {
  if (!isConnected || !db) {
    console.log('💾 Using localStorage for drills')
    const drills = JSON.parse(localStorage.getItem('hockey-drills') || '[]')
    callback(drills)
    return () => {}
  }

  console.log('🔥 Setting up Firebase drills listener')
  const unsubscribe = onSnapshot(
    collection(db, 'drills'),
    (snapshot) => {
      const drills = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }))
      console.log('🔥 Drills updated from Firebase:', drills.length)
      
      // IMPORTANT: Update localStorage with Firebase data
      localStorage.setItem('hockey-drills', JSON.stringify(drills))
      console.log('💾 Drills saved to localStorage from Firebase')
      
      callback(drills)
    },
    (error) => {
      console.error('❌ Drills listener error:', error)
      const drills = JSON.parse(localStorage.getItem('hockey-drills') || '[]')
      callback(drills)
    }
  )

  return unsubscribe
}

// Subscribe to practice plans
function subscribeToPracticePlans(callback: (plans: any[]) => void) {
  if (!isConnected || !db) {
    console.log('💾 Using localStorage for practice plans')
    const plans = JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
    callback(plans)
    return () => {}
  }

  console.log('🔥 Setting up Firebase practice plans listener')
  const unsubscribe = onSnapshot(
    collection(db, 'practicePlans'),
    (snapshot) => {
      const plans = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }))
      console.log('🔥 Practice plans updated from Firebase:', plans.length)
      
      // IMPORTANT: Update localStorage with Firebase data
      localStorage.setItem('hockey-practice-plans', JSON.stringify(plans))
      console.log('💾 Practice plans saved to localStorage from Firebase')
      
      callback(plans)
    },
    (error) => {
      console.error('❌ Practice plans listener error:', error)
      const plans = JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
      callback(plans)
    }
  )

  return unsubscribe
}

// Subscribe to settings
function subscribeToSettings(callback: (settings: any) => void) {
  if (!isConnected || !db) {
    console.log('💾 Using localStorage for settings')
    const settings = JSON.parse(localStorage.getItem('hockey-settings') || '{}')
    callback(settings)
    return () => {}
  }

  console.log('🔥 Setting up Firebase settings listener')
  const unsubscribe = onSnapshot(
    doc(db, 'settings', 'main'),
    (doc) => {
      const settings = doc.exists() ? doc.data() : {}
      console.log('🔥 Settings updated from Firebase')
      
      // IMPORTANT: Update localStorage with Firebase data
      localStorage.setItem('hockey-settings', JSON.stringify(settings))
      console.log('💾 Settings saved to localStorage from Firebase')
      
      callback(settings)
    },
    (error) => {
      console.error('❌ Settings listener error:', error)
      const settings = JSON.parse(localStorage.getItem('hockey-settings') || '{}')
      callback(settings)
    }
  )

  return unsubscribe
}

// Save drills
async function saveDrills(drills: any[]) {
  // Always save to localStorage first
  localStorage.setItem('hockey-drills', JSON.stringify(drills))
  
  if (!isConnected || !db) {
    console.log('💾 Drills saved to localStorage (Firebase offline)')
    return true
  }

  try {
    console.log('🔥 Saving drills to Firebase...')
    
    // Save each drill to Firebase
    for (const drill of drills) {
      const drillRef = doc(db, 'drills', drill.id || `drill_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
      await setDoc(drillRef, {
        ...drill,
        updatedAt: new Date().toISOString(),
        updatedBy: getDeviceId(),
        id: drillRef.id
      })
    }
    
    console.log('✅ Drills saved to Firebase!')
    return true
  } catch (error) {
    console.error('❌ Failed to save drills to Firebase:', error)
    return false
  }
}

// Save practice plans
async function savePracticePlans(plans: any[]) {
  // Always save to localStorage first
  localStorage.setItem('hockey-practice-plans', JSON.stringify(plans))
  
  if (!isConnected || !db) {
    console.log('💾 Practice plans saved to localStorage (Firebase offline)')
    return true
  }

  try {
    console.log('🔥 Saving practice plans to Firebase...')
    
    // Save each practice plan to Firebase
    for (const plan of plans) {
      const planRef = doc(db, 'practicePlans', plan.id || `plan_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`)
      await setDoc(planRef, {
        ...plan,
        updatedAt: new Date().toISOString(),
        updatedBy: getDeviceId(),
        id: planRef.id
      })
    }
    
    console.log('✅ Practice plans saved to Firebase!')
    return true
  } catch (error) {
    console.error('❌ Failed to save practice plans to Firebase:', error)
    return false
  }
}

// Save settings
async function saveSettings(settings: any) {
  // Always save to localStorage first
  localStorage.setItem('hockey-settings', JSON.stringify(settings))
  
  if (!isConnected || !db) {
    console.log('💾 Settings saved to localStorage (Firebase offline)')
    return true
  }

  try {
    console.log('🔥 Saving settings to Firebase...')
    
    const settingsRef = doc(db, 'settings', 'main')
    await setDoc(settingsRef, {
      ...settings,
      updatedAt: new Date().toISOString(),
      updatedBy: getDeviceId()
    })
    
    console.log('✅ Settings saved to Firebase!')
    return true
  } catch (error) {
    console.error('❌ Failed to save settings to Firebase:', error)
    return false
  }
}

// Get current data
function getDrills() {
  return JSON.parse(localStorage.getItem('hockey-drills') || '[]')
}

function getPracticePlans() {
  return JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
}

function getSettings() {
  return JSON.parse(localStorage.getItem('hockey-settings') || '{}')
}

// Get sync status
function getSyncStatus() {
  return {
    deviceId: getDeviceId(),
    isConnected: isConnected,
    database: isConnected ? 'Firebase Firestore (ACTIVE)' : 'localStorage (Firebase offline)',
    status: isConnected ? 
      '🌐 CROSS-DEVICE SYNC ACTIVE - Changes sync automatically!' : 
      '💾 Local storage only - Firebase connection failed',
    dataCount: {
      drills: getDrills().length,
      practicePlans: getPracticePlans().length,
      settings: Object.keys(getSettings()).length
    }
  }
}

// Export all data
function exportAllData() {
  return {
    drills: getDrills(),
    practicePlans: getPracticePlans(),
    settings: getSettings(),
    customCategories: JSON.parse(localStorage.getItem('hockey-custom-categories') || '[]'),
    exportTime: new Date().toISOString(),
    deviceId: getDeviceId(),
    database: isConnected ? 'Firebase Firestore' : 'localStorage'
  }
}

// Import data
async function importAllData(data: any) {
  try {
    console.log('📥 Importing data...')
    
    if (data.drills) await saveDrills(data.drills)
    if (data.practicePlans) await savePracticePlans(data.practicePlans)
    if (data.settings) await saveSettings(data.settings)
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

// Force refresh data from Firebase
async function forceRefreshFromFirebase() {
  if (!isConnected || !db) {
    console.log('💾 Firebase not connected, using localStorage')
    return false
  }

  try {
    console.log('🔄 Force refreshing data from Firebase...')
    
    // Get fresh data from Firebase
    const [drillsSnapshot, plansSnapshot, settingsSnapshot] = await Promise.all([
      getDocs(collection(db, 'drills')),
      getDocs(collection(db, 'practicePlans')),
      getDocs(collection(db, 'settings'))
    ])
    
    const drills = drillsSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }))
    const plans = plansSnapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }))
    const settings = settingsSnapshot.docs.length > 0 ? settingsSnapshot.docs[0].data() : {}
    
    // Update localStorage
    localStorage.setItem('hockey-drills', JSON.stringify(drills))
    localStorage.setItem('hockey-practice-plans', JSON.stringify(plans))
    localStorage.setItem('hockey-settings', JSON.stringify(settings))
    
    console.log('✅ Force refresh complete:', { drills: drills.length, plans: plans.length })
    return true
  } catch (error) {
    console.error('❌ Force refresh failed:', error)
    return false
  }
}

// Export functions
export { 
  subscribeToDrills, 
  subscribeToPracticePlans, 
  subscribeToSettings,
  saveDrills as saveDrill,
  savePracticePlans as savePracticePlan,
  saveSettings,
  getDrills,
  getPracticePlans,
  getSettings,
  getSyncStatus,
  exportAllData,
  importAllData,
  initializeFirebase as initializeSharedDatabase,
  forceRefreshFromFirebase
}
