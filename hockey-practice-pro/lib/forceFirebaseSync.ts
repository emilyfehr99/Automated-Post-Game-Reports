// FORCE Firebase sync - ensures mobile loads data from Firebase
import { initializeApp } from 'firebase/app'
import { 
  getFirestore, 
  collection, 
  doc, 
  getDocs,
  getDoc
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

try {
  app = initializeApp(firebaseConfig)
  db = getFirestore(app)
  console.log('🔥 Force Firebase initialized successfully')
} catch (error) {
  console.error('❌ Force Firebase initialization failed:', error)
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

// Force load data from Firebase
export async function forceLoadFromFirebase(): Promise<boolean> {
  if (!db) {
    console.log('❌ Firebase not available for force load')
    return false
  }

  try {
    console.log('🔥 FORCE LOADING DATA FROM FIREBASE...')
    
    // Load drills
    const drillsSnapshot = await getDocs(collection(db, 'drills'))
    const drills = drillsSnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }))
    localStorage.setItem('hockey-drills', JSON.stringify(drills))
    console.log(`🔥 FORCE LOADED ${drills.length} drills from Firebase`)
    
    // Load practice plans
    const plansSnapshot = await getDocs(collection(db, 'practicePlans'))
    const plans = plansSnapshot.docs.map(doc => ({
      id: doc.id,
      ...doc.data()
    }))
    localStorage.setItem('hockey-practice-plans', JSON.stringify(plans))
    console.log(`🔥 FORCE LOADED ${plans.length} practice plans from Firebase`)
    
    // Load settings
    const settingsDoc = await getDoc(doc(db, 'settings', 'main'))
    const settings = settingsDoc.exists() ? settingsDoc.data() : {}
    localStorage.setItem('hockey-settings', JSON.stringify(settings))
    console.log('🔥 FORCE LOADED settings from Firebase')
    
    // Ensure device ID exists
    getDeviceId()
    console.log('🔥 FORCE LOAD COMPLETED - Data synced to localStorage')
    
    return true
  } catch (error) {
    console.error('❌ Force load failed:', error)
    return false
  }
}

// Check if we need to force load
export function shouldForceLoad(): boolean {
  const drills = localStorage.getItem('hockey-drills')
  const plans = localStorage.getItem('hockey-practice-plans')
  const deviceId = localStorage.getItem('hockey-device-id')
  
  const hasNoData = (!drills || JSON.parse(drills).length === 0) && 
                   (!plans || JSON.parse(plans).length === 0)
  const hasNoDeviceId = !deviceId
  
  console.log('🔍 Force load check:', {
    hasNoData,
    hasNoDeviceId,
    shouldForce: hasNoData || hasNoDeviceId
  })
  
  return hasNoData || hasNoDeviceId
}
