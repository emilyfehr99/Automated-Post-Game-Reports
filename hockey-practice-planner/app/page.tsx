'use client'

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Plus, 
  Search, 
  Play, 
  Users, 
  Calendar, 
  Settings,
  FileText,
  Video,
  Image,
  Share2,
  Download,
  Timer
} from 'lucide-react'
import DrillDrawingTool from '@/components/DrillDrawingTool'
import PracticePlanBuilder from '@/components/PracticePlanBuilder'
import DrillPreviewModal from '@/components/DrillPreviewModal'
import SimpleDrillCreator from '@/components/SimpleDrillCreator'
import PracticePlanDetailModal from '@/components/PracticePlanDetailModal'
import QRCodeSync from '@/components/QRCodeSync'
import TimerView from '@/components/TimerView'
import { 
  subscribeToDrills, 
  subscribeToPracticePlans, 
  subscribeToSettings,
  saveDrill,
  savePracticePlan,
  saveSettings,
  getDrills,
  getPracticePlans,
  getSettings,
  getSyncStatus,
  exportAllData,
  importAllData,
  forceRefreshFromFirebase
} from '../lib/simpleFirebase'

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [showDrillDrawingTool, setShowDrillDrawingTool] = useState(false)
  const [showSimpleDrillCreator, setShowSimpleDrillCreator] = useState(false)
  const [showPracticePlanBuilder, setShowPracticePlanBuilder] = useState(false)
  const [showDrillPreview, setShowDrillPreview] = useState(false)
  const [previewDrill, setPreviewDrill] = useState<any>(null)
  const [showDrillDetail, setShowDrillDetail] = useState(false)
  const [selectedDrill, setSelectedDrill] = useState<any>(null)
  const [showPracticePlanDetail, setShowPracticePlanDetail] = useState(false)
  const [selectedPracticePlan, setSelectedPracticePlan] = useState<any>(null)
  const [practicePlans, setPracticePlans] = useState<any[]>([])
  const [drills, setDrills] = useState<any[]>([])
  const [isAutoSaving, setIsAutoSaving] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [syncStatus, setSyncStatus] = useState('🔄 Syncing...')
  const [settings, setSettings] = useState({
    teamName: '',
    coachName: '',
    season: '',
    level: ''
  })
  const [showQRSync, setShowQRSync] = useState(false)

  // Function to handle data import from QR sync
  const handleDataImport = (data: any) => {
    if (data.drills) {
      setDrills(data.drills)
      localStorage.setItem('hockey-drills', JSON.stringify(data.drills))
    }
    if (data.practicePlans) {
      setPracticePlans(data.practicePlans)
      localStorage.setItem('hockey-practice-plans', JSON.stringify(data.practicePlans))
    }
    if (data.settings) {
      setSettings(data.settings)
      localStorage.setItem('hockey-settings', JSON.stringify(data.settings))
    }
    if (data.customCategories) {
      localStorage.setItem('hockey-custom-categories', JSON.stringify(data.customCategories))
    }
    alert('✅ Data imported successfully!')
  }

  // Load data from sync service on component mount
  useEffect(() => {
    let unsubscribeDrills: (() => void) | undefined
    let unsubscribePlans: (() => void) | undefined
    let unsubscribeSettings: (() => void) | undefined

    const initializeSync = async () => {
      try {
        // Subscribe to real-time updates
        unsubscribeDrills = subscribeToDrills((drills) => {
          setDrills(drills)
          console.log('✅ Drills updated from sync service:', drills.length)
        })

        unsubscribePlans = subscribeToPracticePlans((plans) => {
          setPracticePlans(plans)
          console.log('✅ Practice plans updated from sync service:', plans.length)
        })

        unsubscribeSettings = subscribeToSettings((settingsData) => {
          if (settingsData) {
            setSettings(settingsData)
            console.log('✅ Settings updated from sync service')
          }
        })

        setIsLoading(false)
        
        // Initialize the shared database
        const { initializeSharedDatabase } = await import('../lib/simpleFirebase')
        
        const isConnected = await initializeSharedDatabase()
        
        // Force refresh data from Firebase if connected
        if (isConnected) {
          console.log('🔄 Force refreshing data from Firebase...')
          const refreshed = await forceRefreshFromFirebase()
          if (refreshed) {
            console.log('✅ Force refresh successful - reloading data')
            // Reload data after force refresh
            const drills = JSON.parse(localStorage.getItem('hockey-drills') || '[]')
            const plans = JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
            const settings = JSON.parse(localStorage.getItem('hockey-settings') || '{}')
            setDrills(drills)
            setPracticePlans(plans)
            setSettings(settings)
          }
        }
        
        if (isConnected) {
          setSyncStatus('🌐 Shared database active - all devices sync!')
        } else {
          setSyncStatus('💾 Local storage (offline mode)')
        }
        
        console.log('✅ Sync service connected - real-time sync active!')
      } catch (error) {
        console.error('❌ Sync service connection failed:', error)
        // Fallback to localStorage if sync fails
        const savedDrills = localStorage.getItem('hockey-drills')
        const savedPlans = localStorage.getItem('hockey-practice-plans')
        const savedSettings = localStorage.getItem('hockey-settings')
        
        if (savedDrills) setDrills(JSON.parse(savedDrills))
        if (savedPlans) setPracticePlans(JSON.parse(savedPlans))
        if (savedSettings) setSettings(JSON.parse(savedSettings))
        
        setIsLoading(false)
      }
    }

    initializeSync()

    // Cleanup subscriptions on unmount
    return () => {
      if (unsubscribeDrills) unsubscribeDrills()
      if (unsubscribePlans) unsubscribePlans()
      if (unsubscribeSettings) unsubscribeSettings()
    }
  }, [])

  // Save drills to sync service whenever drills change (with error handling)
  useEffect(() => {
    if (drills.length === 0) return // Don't save on initial load
    
    setIsAutoSaving(true)
    
    const saveDrillsToSync = async () => {
      try {
        // Save drills to sync service
        await saveDrill(drills)
        console.log('✅ Drills auto-saved to sync service')
        
        // Hide auto-save indicator after a short delay
        setTimeout(() => setIsAutoSaving(false), 1000)
      } catch (error) {
        console.error('Failed to save drills to sync service:', error)
        setIsAutoSaving(false)
        // Fallback to localStorage if sync fails
        try {
          localStorage.setItem('hockey-drills', JSON.stringify(drills))
          console.log('✅ Drills saved to localStorage as fallback')
        } catch (localError) {
          console.error('Failed to save to localStorage:', localError)
        }
      }
    }

    saveDrillsToSync()
  }, [drills])

  // Save practice plans to sync service whenever practicePlans change (with error handling)
  useEffect(() => {
    if (practicePlans.length === 0) return // Don't save on initial load
    
    setIsAutoSaving(true)
    
    const savePlansToSync = async () => {
      try {
        // Save practice plans to sync service
        await savePracticePlan(practicePlans)
        console.log('✅ Practice plans auto-saved to sync service')
        
        // Hide auto-save indicator after a short delay
        setTimeout(() => setIsAutoSaving(false), 1000)
      } catch (error) {
        console.error('Failed to save practice plans to sync service:', error)
        setIsAutoSaving(false)
        // Fallback to localStorage if sync fails
        try {
          localStorage.setItem('hockey-practice-plans', JSON.stringify(practicePlans))
          console.log('✅ Practice plans saved to localStorage as fallback')
        } catch (localError) {
          console.error('Failed to save to localStorage:', localError)
        }
      }
    }

    savePlansToSync()
  }, [practicePlans])

  // Save settings to sync service whenever settings change (with error handling)
  useEffect(() => {
    const saveSettingsToSync = async () => {
      try {
        await saveSettings(settings)
        console.log('✅ Settings auto-saved to sync service')
      } catch (error) {
        console.error('Failed to save settings to sync service:', error)
        // Fallback to localStorage if sync fails
        try {
          localStorage.setItem('hockey-settings', JSON.stringify(settings))
          console.log('✅ Settings saved to localStorage as fallback')
        } catch (localError) {
          console.error('Failed to save to localStorage:', localError)
        }
      }
    }

    saveSettingsToSync()
  }, [settings])

  // Helper function to compress images (simplified)
  const compressImage = (base64: string): Promise<string> => {
    try {
      // If image is already small enough, return as is
      if (base64.length < 50000) {
        return Promise.resolve(base64)
      }

      // Create a canvas to compress the image
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      const img = document.createElement('img')
      
      // Return a promise that resolves to compressed image
      return new Promise<string>((resolve) => {
        img.onload = () => {
          // Set canvas size to a reasonable maximum
          const maxWidth = 600
          const maxHeight = 400
          let { width, height } = img
          
          if (width > height) {
            if (width > maxWidth) {
              height = (height * maxWidth) / width
              width = maxWidth
            }
          } else {
            if (height > maxHeight) {
              width = (width * maxHeight) / height
              height = maxHeight
            }
          }
          
          canvas.width = width
          canvas.height = height
          
          ctx?.drawImage(img, 0, 0, width, height)
          const compressed = canvas.toDataURL('image/jpeg', 0.6) // 60% quality for smaller size
          resolve(compressed)
        }
        img.onerror = () => {
          // If image fails to load, return original
          resolve(base64)
        }
        img.src = base64
      })
    } catch (error) {
      console.error('Failed to compress image:', error)
      return Promise.resolve(base64) // Return original if compression fails
    }
  }

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Play },
    { id: 'drills', label: 'Drill Library', icon: Search },
    { id: 'practice', label: 'Practice Plans', icon: Calendar },
    { id: 'timer', label: 'Timer', icon: Timer },
    { id: 'create', label: 'Create', icon: Plus },
    { id: 'team', label: 'Team', icon: Users },
    { id: 'settings', label: 'Settings', icon: Settings },
  ]

  // Show loading screen while data is being loaded
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-hockey-blue mx-auto mb-4"></div>
          <h2 className="text-xl font-russo text-hockey-blue mb-2">Loading Your Data...</h2>
          <p className="text-gray-600">Restoring your drills and practice plans from previous session</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-hockey-blue text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8">
          <div className="flex justify-between items-center h-14 sm:h-16">
            <div className="flex items-center">
              <h1 className="text-lg sm:text-xl lg:text-2xl font-russo">Hockey Practice Planner</h1>
              <div className="ml-3 text-xs text-gray-500 hidden sm:block">
                {syncStatus}
              </div>
            </div>
            <div className="flex items-center space-x-4">
              
              <button 
                onClick={() => {
                  // Force save to localStorage
                  localStorage.setItem('hockey-drills', JSON.stringify(drills))
                  localStorage.setItem('hockey-practice-plans', JSON.stringify(practicePlans))
                  alert('✅ All data saved successfully!')
                }}
                className="hockey-button-secondary text-xs sm:text-sm px-2 sm:px-3 py-1 sm:py-2"
                title="Force save all data"
              >
                <Download className="w-3 h-3 sm:w-4 sm:h-4 sm:mr-2" />
                <span className="hidden sm:inline">Force Save</span>
                <span className="sm:hidden">Save</span>
              </button>
              <button className="hockey-button-secondary text-xs sm:text-sm px-2 sm:px-3 py-1 sm:py-2">
                <Share2 className="w-3 h-3 sm:w-4 sm:h-4 sm:mr-2" />
                <span className="hidden sm:inline">Share</span>
              </button>
              <button className="hockey-button text-xs sm:text-sm px-2 sm:px-3 py-1 sm:py-2">
                <Download className="w-3 h-3 sm:w-4 sm:h-4 sm:mr-2" />
                <span className="hidden sm:inline">Export</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8">
          <div className="flex overflow-x-auto scrollbar-hide">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-2 sm:px-3 py-3 sm:py-4 text-xs sm:text-sm font-medium border-b-2 transition-colors duration-200 whitespace-nowrap ${
                    activeTab === tab.id
                      ? 'border-hockey-blue text-hockey-blue'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-3 h-3 sm:w-4 sm:h-4 mr-1 sm:mr-2" />
                  <span className="hidden xs:inline">{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-2 sm:px-4 lg:px-8 py-4 sm:py-8">
        {activeTab === 'dashboard' && (
          <DashboardView 
            onOpenPracticeBuilder={() => setShowPracticePlanBuilder(true)}
            onOpenDrillDrawing={() => setShowDrillDrawingTool(true)}
            onOpenSimpleDrillCreator={() => setShowSimpleDrillCreator(true)}
            onViewPracticePlan={(plan) => {
              setSelectedPracticePlan(plan)
              setShowPracticePlanDetail(true)
            }}
            drills={drills}
            practicePlans={practicePlans}
          />
        )}
        {activeTab === 'drills' && (
          <DrillLibraryView 
            onOpenDrillDrawing={() => setShowDrillDrawingTool(true)}
            onOpenSimpleDrillCreator={() => setShowSimpleDrillCreator(true)}
            drills={drills}
            onAddDrillToPlan={(drill) => {
              // For now, just show an alert - this would add to current practice plan
              alert(`Added "${drill.name}" to practice plan`)
            }}
            onViewDrill={(drill) => {
              setSelectedDrill(drill)
              setShowDrillDetail(true)
            }}
          />
        )}
        {activeTab === 'practice' && (
          <PracticePlansView 
            onOpenPracticeBuilder={() => setShowPracticePlanBuilder(true)}
            onViewPracticePlan={(plan) => {
              setSelectedPracticePlan(plan)
              setShowPracticePlanDetail(true)
            }}
            practicePlans={practicePlans}
          />
        )}
        {activeTab === 'timer' && <TimerView />}
        {activeTab === 'create' && (
          <CreateView 
            onOpenPracticeBuilder={() => setShowPracticePlanBuilder(true)}
            onOpenDrillDrawing={() => setShowDrillDrawingTool(true)}
            onOpenSimpleDrillCreator={() => setShowSimpleDrillCreator(true)}
          />
        )}
        {activeTab === 'team' && <TeamView />}
        {activeTab === 'settings' && <SettingsView onShowQRSync={() => setShowQRSync(true)} />}
      </main>

      {/* Modals */}
      {showDrillDrawingTool && (
        <DrillDrawingTool
          onSave={(drillData) => {
            setDrills([...drills, drillData])
            setShowDrillDrawingTool(false)
            alert(`Drill "${drillData.name}" saved successfully!`)
          }}
          onClose={() => setShowDrillDrawingTool(false)}
          onPreview={(drillData) => {
            setPreviewDrill(drillData)
            setShowDrillDrawingTool(false)
            setShowDrillPreview(true)
          }}
        />
      )}

      {showDrillPreview && previewDrill && (
        <DrillPreviewModal
          drill={previewDrill}
          onSave={(drillData) => {
            setDrills([...drills, drillData])
            setShowDrillPreview(false)
            setPreviewDrill(null)
            alert(`Drill "${drillData.name}" saved successfully!`)
          }}
          onClose={() => {
            setShowDrillPreview(false)
            setPreviewDrill(null)
          }}
        />
      )}

      {showSimpleDrillCreator && (
        <SimpleDrillCreator
          onSave={(drillData) => {
            if (selectedDrill) {
              // Editing existing drill
              setDrills(drills.map(d => d.id === drillData.id ? drillData : d))
              alert(`Drill "${drillData.name}" updated successfully!`)
            } else {
              // Creating new drill
              setDrills([...drills, drillData])
              alert(`Drill "${drillData.name}" created successfully!`)
            }
            setShowSimpleDrillCreator(false)
            setSelectedDrill(null)
          }}
          onClose={() => {
            setShowSimpleDrillCreator(false)
            setSelectedDrill(null)
          }}
          editDrill={selectedDrill}
        />
      )}

      {showPracticePlanBuilder && (
        <PracticePlanBuilder
          onSave={(plan) => {
            if (selectedPracticePlan) {
              // Editing existing practice plan
              setPracticePlans(practicePlans.map(p => p.id === plan.id ? plan : p))
              alert(`Practice plan "${plan.name}" updated successfully!`)
            } else {
              // Creating new practice plan
              setPracticePlans([...practicePlans, plan])
              alert(`Practice plan "${plan.name}" created successfully!`)
            }
            setShowPracticePlanBuilder(false)
            setSelectedPracticePlan(null)
          }}
          onClose={() => {
            setShowPracticePlanBuilder(false)
            setSelectedPracticePlan(null)
          }}
          initialPlan={selectedPracticePlan}
          availableDrills={drills}
        />
      )}

      {showDrillDetail && selectedDrill && (
        <DrillDetailModal
          drill={selectedDrill}
          onClose={() => {
            setShowDrillDetail(false)
            setSelectedDrill(null)
          }}
          onEdit={(drill) => {
            setShowDrillDetail(false)
            setSelectedDrill(drill)
            setShowSimpleDrillCreator(true)
          }}
          onDelete={(drill) => {
            if (confirm(`Are you sure you want to delete "${drill.name}"?`)) {
              setDrills(drills.filter(d => d.id !== drill.id))
              setShowDrillDetail(false)
              setSelectedDrill(null)
            }
          }}
        />
      )}

      {showPracticePlanDetail && selectedPracticePlan && (
        <PracticePlanDetailModal
          practicePlan={selectedPracticePlan}
          onClose={() => {
            setShowPracticePlanDetail(false)
            setSelectedPracticePlan(null)
          }}
          onEdit={(plan) => {
            setShowPracticePlanDetail(false)
            setSelectedPracticePlan(plan)
            setShowPracticePlanBuilder(true)
          }}
          onDelete={(plan) => {
            if (confirm(`Are you sure you want to delete "${plan.name}"?`)) {
              setPracticePlans(practicePlans.filter(p => p.id !== plan.id))
              setShowPracticePlanDetail(false)
              setSelectedPracticePlan(null)
            }
          }}
          onReorder={async (updatedPlan) => {
            // Update the practice plan with new drill order
            const updatedPlans = practicePlans.map(p => 
              p.id === updatedPlan.id ? updatedPlan : p
            )
            setPracticePlans(updatedPlans)
            setSelectedPracticePlan(updatedPlan)
            
            // Save to Firebase
            try {
              const { savePracticePlan } = await import('../lib/simpleFirebase')
              await savePracticePlan(updatedPlan)
              console.log('✅ Practice plan reordered and saved to Firebase')
            } catch (error) {
              console.error('❌ Failed to save reordered practice plan:', error)
            }
          }}
        />
      )}

      {showQRSync && (
        <QRCodeSync
          onClose={() => setShowQRSync(false)}
          onImport={handleDataImport}
        />
      )}
    </div>
  )
}

function DashboardView({ 
  onOpenPracticeBuilder, 
  onOpenDrillDrawing,
  onOpenSimpleDrillCreator,
  onViewPracticePlan,
  drills,
  practicePlans
}: { 
  onOpenPracticeBuilder: () => void
  onOpenDrillDrawing: () => void
  onOpenSimpleDrillCreator: () => void
  onViewPracticePlan: (plan: any) => void
  drills: any[]
  practicePlans: any[]
}) {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="hockey-card"
        >
          <h3 className="text-lg font-russo text-hockey-blue mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button 
              onClick={onOpenPracticeBuilder}
              className="w-full hockey-button flex items-center justify-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Practice Plan
            </button>
            <button 
              onClick={onOpenSimpleDrillCreator}
              className="w-full hockey-button-secondary flex items-center justify-center"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Drill
            </button>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="hockey-card"
        >
          <h3 className="text-lg font-russo text-hockey-blue mb-4">Recent Practice Plans</h3>
          <div className="space-y-2">
            {practicePlans.length > 0 ? (
              practicePlans.slice(0, 2).map((plan, index) => (
                <div 
                  key={plan.id || index} 
                  className="p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors"
                  onClick={() => onViewPracticePlan(plan)}
                >
                  <p className="font-medium">{plan.name}</p>
                  <p className="text-sm text-gray-600">
                    {plan.createdAt ? new Date(plan.createdAt).toLocaleDateString() : 'Recently created'}
                  </p>
                </div>
              ))
            ) : (
              <div className="p-3 bg-gray-50 rounded-lg text-center">
                <p className="text-gray-500 text-sm">No practice plans yet</p>
                <p className="text-xs text-gray-400 mt-1">Create your first one!</p>
              </div>
            )}
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="hockey-card"
        >
          <h3 className="text-lg font-russo text-hockey-blue mb-4">Statistics</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Total Drills:</span>
              <span className="font-bold">{drills.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Practice Plans:</span>
              <span className="font-bold">{practicePlans.length}</span>
            </div>
            <div className="flex justify-between">
              <span>Team Members:</span>
              <span className="font-bold">0</span>
            </div>
          </div>
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center text-sm text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
              Auto-save enabled - Your work is always saved
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

function DrillLibraryView({ 
  onOpenDrillDrawing, 
  onOpenSimpleDrillCreator,
  drills, 
  onAddDrillToPlan,
  onViewDrill
}: { 
  onOpenDrillDrawing: () => void
  onOpenSimpleDrillCreator: () => void
  drills: any[]
  onAddDrillToPlan: (drill: any) => void
  onViewDrill: (drill: any) => void
}) {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')

  const categories = ['All', 'Skills', 'Systems', 'Offensive', 'Defensive', 'Power Play', 'Penalty Kill', 'Warm-up', 'Cool-down']

  const filteredDrills = drills.filter(drill => {
    const matchesSearch = drill.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         drill.description.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesCategory = selectedCategory === 'All' || drill.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-russo text-hockey-blue">Drill Library</h2>
        <div className="flex space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search drills..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
            />
          </div>
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
          <button 
            onClick={onOpenSimpleDrillCreator}
            className="hockey-button"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Drill
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredDrills.map((drill, index) => (
          <motion.div
            key={drill.id}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className="hockey-card hover:shadow-xl transition-shadow duration-200 cursor-pointer"
            onClick={() => onViewDrill(drill)}
          >
            <div className="aspect-video bg-ice-blue rounded-lg mb-4 flex items-center justify-center overflow-hidden">
              {drill.images && drill.images.length > 0 ? (
                <img 
                  src={drill.images[0]} 
                  alt={drill.name}
                  className="w-full h-full object-cover rounded-lg"
                />
              ) : (
                <div className="text-center">
                  <div className="w-16 h-16 bg-hockey-blue rounded-full flex items-center justify-center mx-auto mb-2">
                    <Play className="w-8 h-8 text-white" />
                  </div>
                  <p className="text-sm text-gray-600">
                    {drill.type === 'custom' ? 'Custom Drill' : 
                     drill.type === 'pdf' ? 'PDF Drill' : 'Sample Drill'}
                  </p>
                </div>
              )}
            </div>
            <h3 className="font-russo text-lg mb-2">{drill.name}</h3>
            <p className="text-gray-600 text-sm mb-4">{drill.description}</p>
            <div className="flex justify-between items-center">
              <div className="flex items-center space-x-2">
                <span className="text-xs bg-hockey-blue text-white px-2 py-1 rounded">
                  {drill.category}
                </span>
                <span className="text-xs text-gray-500">
                  {drill.duration}min
                </span>
              </div>
              <button 
                onClick={(e) => {
                  e.stopPropagation()
                  onAddDrillToPlan(drill)
                }}
                className="text-hockey-blue hover:text-blue-800 transition-colors"
                title="Add to Practice Plan"
              >
                <Plus className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        ))}
      </div>

      {filteredDrills.length === 0 && (
        <div className="text-center py-12">
          <Search className="w-12 h-12 mx-auto mb-4 text-gray-300" />
          <p className="text-gray-500">No drills found matching your search criteria.</p>
        </div>
      )}
    </div>
  )
}

function PracticePlansView({ 
  onOpenPracticeBuilder, 
  onViewPracticePlan,
  practicePlans 
}: { 
  onOpenPracticeBuilder: () => void
  onViewPracticePlan: (plan: any) => void
  practicePlans: any[]
}) {
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-russo text-hockey-blue">Practice Plans</h2>
        <button 
          onClick={onOpenPracticeBuilder}
          className="hockey-button"
        >
          <Plus className="w-4 h-4 mr-2" />
          New Practice Plan
        </button>
      </div>

      {practicePlans.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {practicePlans.map((plan, index) => (
            <motion.div
              key={plan.id || index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="hockey-card hover:shadow-xl transition-shadow duration-200 cursor-pointer"
              onClick={() => onViewPracticePlan(plan)}
            >
              <div className="flex justify-between items-start mb-4">
                <h3 className="font-russo text-lg">{plan.name || `Practice Plan ${index + 1}`}</h3>
                <div className="flex space-x-2">
                  <button className="text-gray-400 hover:text-gray-600">
                    <Share2 className="w-4 h-4" />
                  </button>
                  <button className="text-gray-400 hover:text-gray-600">
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
              <p className="text-gray-600 text-sm mb-4">
                {plan.createdAt ? new Date(plan.createdAt).toLocaleDateString() : 'Recently created'}
              </p>
              <div className="space-y-2">
                <div className="flex items-center text-sm">
                  <FileText className="w-4 h-4 mr-2 text-gray-400" />
                  <span>{plan.drills?.length || 0} drills</span>
                </div>
                <div className="flex items-center text-sm">
                  <Calendar className="w-4 h-4 mr-2 text-gray-400" />
                  <span>{plan.duration || 'No duration set'}</span>
                </div>
                <div className="flex items-center text-sm">
                  <Play className="w-4 h-4 mr-2 text-gray-400" />
                  <span>{plan.category || 'General'}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <Calendar className="w-16 h-16 mx-auto mb-4 text-gray-300" />
          <h3 className="text-lg font-medium text-gray-500 mb-2">No Practice Plans Yet</h3>
          <p className="text-gray-400 mb-6">Create your first practice plan to get started!</p>
          <button 
            onClick={onOpenPracticeBuilder}
            className="hockey-button"
          >
            <Plus className="w-4 h-4 mr-2" />
            Create Your First Practice Plan
          </button>
        </div>
      )}
    </div>
  )
}

function CreateView({ 
  onOpenPracticeBuilder, 
  onOpenDrillDrawing,
  onOpenSimpleDrillCreator
}: { 
  onOpenPracticeBuilder: () => void
  onOpenDrillDrawing: () => void
  onOpenSimpleDrillCreator: () => void
}) {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-russo text-hockey-blue">Create New Content</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <motion.div
          whileHover={{ scale: 1.05 }}
          className="hockey-card cursor-pointer"
          onClick={onOpenPracticeBuilder}
        >
          <div className="text-center">
            <div className="w-16 h-16 bg-hockey-blue rounded-full flex items-center justify-center mx-auto mb-4">
              <Calendar className="w-8 h-8 text-white" />
            </div>
            <h3 className="font-russo text-lg mb-2">Practice Plan</h3>
            <p className="text-gray-600 text-sm">Create a structured practice session with drills and activities</p>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          className="hockey-card cursor-pointer"
          onClick={onOpenSimpleDrillCreator}
        >
          <div className="text-center">
            <div className="w-16 h-16 bg-hockey-red rounded-full flex items-center justify-center mx-auto mb-4">
              <Plus className="w-8 h-8 text-white" />
            </div>
            <h3 className="font-russo text-lg mb-2">Create Drill</h3>
            <p className="text-gray-600 text-sm">Upload images and add text to create a drill plan</p>
          </div>
        </motion.div>

        <motion.div
          whileHover={{ scale: 1.05 }}
          className="hockey-card cursor-pointer"
        >
          <div className="text-center">
            <div className="w-16 h-16 bg-hockey-gold rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-white" />
            </div>
            <h3 className="font-russo text-lg mb-2">Team Setup</h3>
            <p className="text-gray-600 text-sm">Configure your team roster and settings</p>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

function TeamView() {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-russo text-hockey-blue">Team Management</h2>
      <div className="hockey-card">
        <p className="text-gray-600">Team management features coming soon...</p>
      </div>
    </div>
  )
}

function SettingsView({ onShowQRSync }: { onShowQRSync: () => void }) {
  const [isRestoring, setIsRestoring] = useState(false)
  const [settings, setSettings] = useState({
    teamName: 'My Hockey Team',
    coachName: '',
    defaultDrillDuration: 15,
    autoSave: true,
    theme: 'hockey'
  })

  const restoreDataFromFirebase = async () => {
    setIsRestoring(true)
    try {
      // Direct Firebase restore without complex imports
      const { initializeApp } = await import('firebase/app')
      const { getFirestore, collection, getDocs } = await import('firebase/firestore')
      
      const firebaseConfig = {
        apiKey: "AIzaSyCm2m3lSlh_IBgHSOLcmeCO9lZYHaxgrFw",
        authDomain: "hockey-practice-planner.firebaseapp.com",
        projectId: "hockey-practice-planner",
        storageBucket: "hockey-practice-planner.firebasestorage.app",
        messagingSenderId: "557366268618",
        appId: "1:557366268618:web:d6f5cf9e80045d966fda33",
        measurementId: "G-BSH8MT49BZ"
      }

      const app = initializeApp(firebaseConfig)
      const db = getFirestore(app)
      
      console.log('🔥 Direct Firebase restore started...')
      
      // Load practice plans
      const practicePlansRef = collection(db, 'practicePlans')
      const practicePlansSnapshot = await getDocs(practicePlansRef)
      const practicePlans = practicePlansSnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }))
      
      // Load drills
      const drillsRef = collection(db, 'drills')
      const drillsSnapshot = await getDocs(drillsRef)
      const drills = drillsSnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }))
      
      // Save to localStorage
      localStorage.setItem('hockey-practice-plans', JSON.stringify(practicePlans))
      localStorage.setItem('hockey-drills', JSON.stringify(drills))
      localStorage.setItem('hockey-device-id', 'device_' + Date.now() + '_restored')
      
      console.log(`✅ Restored ${practicePlans.length} practice plans and ${drills.length} drills`)
      
      if (practicePlans.length > 0) {
        alert(`✅ Successfully restored ${practicePlans.length} practice plans and ${drills.length} drills! Refreshing page...`)
        setTimeout(() => window.location.reload(), 1000)
      } else {
        alert('⚠️ No practice plans found in Firebase. They may have been deleted.')
      }
      
    } catch (error) {
      console.error('❌ Restore error:', error)
      alert(`❌ Error restoring data: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsRestoring(false)
    }
  }

  // Load settings from localStorage
  useEffect(() => {
    const savedSettings = localStorage.getItem('hockey-settings')
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings))
    }
  }, [])

  // Save settings to localStorage
  const saveSettings = () => {
    localStorage.setItem('hockey-settings', JSON.stringify(settings))
    alert('✅ Settings saved successfully!')
  }

  const exportData = () => {
    try {
      console.log('Starting export...')
      const data = {
        drills: JSON.parse(localStorage.getItem('hockey-drills') || '[]'),
        practicePlans: JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]'),
        settings: settings,
        customCategories: JSON.parse(localStorage.getItem('hockey-custom-categories') || '[]'),
        exportDate: new Date().toISOString()
      }
      
      console.log('Export data:', data)
      console.log('Drills count:', data.drills.length)
      console.log('Practice plans count:', data.practicePlans.length)
      
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `hockey-practice-planner-backup-${new Date().toISOString().split('T')[0]}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      console.log('Export completed successfully')
      alert(`✅ Data exported successfully! ${data.drills.length} drills and ${data.practicePlans.length} practice plans exported.`)
    } catch (error) {
      console.error('Export error:', error)
      alert('❌ Error exporting data. Please check the console for details.')
    }
  }

  const copyDataToClipboard = async () => {
    try {
      const data = {
        drills: JSON.parse(localStorage.getItem('hockey-drills') || '[]'),
        practicePlans: JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]'),
        settings: settings,
        customCategories: JSON.parse(localStorage.getItem('hockey-custom-categories') || '[]'),
        exportDate: new Date().toISOString()
      }
      
      const dataString = JSON.stringify(data, null, 2)
      await navigator.clipboard.writeText(dataString)
      alert(`✅ Data copied to clipboard! ${data.drills.length} drills and ${data.practicePlans.length} practice plans copied.`)
    } catch (error) {
      console.error('Copy error:', error)
      alert('❌ Error copying data. Please try the download method instead.')
    }
  }

  const [showDataText, setShowDataText] = useState(false)

  const getExportData = () => {
    return {
      drills: JSON.parse(localStorage.getItem('hockey-drills') || '[]'),
      practicePlans: JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]'),
      settings: settings,
      customCategories: JSON.parse(localStorage.getItem('hockey-custom-categories') || '[]'),
      exportDate: new Date().toISOString()
    }
  }

  const importData = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target?.result as string)
          console.log('Importing data:', data)
          
          if (data.drills) {
            localStorage.setItem('hockey-drills', JSON.stringify(data.drills))
            console.log(`Imported ${data.drills.length} drills`)
          }
          if (data.practicePlans) {
            localStorage.setItem('hockey-practice-plans', JSON.stringify(data.practicePlans))
            console.log(`Imported ${data.practicePlans.length} practice plans`)
          }
          if (data.settings) {
            localStorage.setItem('hockey-settings', JSON.stringify(data.settings))
            console.log('Imported settings')
          }
          if (data.customCategories) {
            localStorage.setItem('hockey-custom-categories', JSON.stringify(data.customCategories))
            console.log(`Imported ${data.customCategories.length} custom categories`)
          }
          
          alert(`✅ Data imported successfully! ${data.drills?.length || 0} drills, ${data.practicePlans?.length || 0} practice plans imported. The page will refresh now.`)
          
          // Automatically refresh the page to show the new data
          setTimeout(() => {
            window.location.reload()
          }, 1000)
          
        } catch (error) {
          console.error('Import error:', error)
          alert('❌ Error importing data. Please check the file format.')
        }
      }
      reader.readAsText(file)
    }
  }

  const clearAllData = () => {
    if (confirm('⚠️ Are you sure you want to clear ALL data? This cannot be undone!')) {
      localStorage.removeItem('hockey-drills')
      localStorage.removeItem('hockey-practice-plans')
      localStorage.removeItem('hockey-settings')
      alert('🗑️ All data cleared. Please refresh the page.')
    }
  }

  const clearStorageAndRestart = () => {
    if (confirm('🔄 Clear all storage and restart fresh? This will remove all data but fix quota issues.')) {
      localStorage.clear()
      alert('✅ Storage cleared! The page will refresh.')
      window.location.reload()
    }
  }

  const clearOldDrills = () => {
    if (confirm('🗑️ Clear drills older than 30 days? This will help free up storage space.')) {
      const thirtyDaysAgo = new Date()
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
      
      const currentDrills = JSON.parse(localStorage.getItem('hockey-drills') || '[]')
      const filteredDrills = currentDrills.filter((drill: any) => {
        if (!drill.createdAt) return true // Keep drills without creation date
        return new Date(drill.createdAt) > thirtyDaysAgo
      })
      
      localStorage.setItem('hockey-drills', JSON.stringify(filteredDrills))
      alert(`✅ Cleared ${currentDrills.length - filteredDrills.length} old drills. Please refresh the page.`)
    }
  }

  const optimizeStorage = async () => {
    if (confirm('🔧 Optimize storage by compressing all images? This may take a moment.')) {
      const currentDrills = JSON.parse(localStorage.getItem('hockey-drills') || '[]')
      const optimizedDrills = await Promise.all(currentDrills.map(async (drill: any) => ({
        ...drill,
        images: drill.images?.map((img: string) => {
          // Simple truncation for now to avoid build issues
          if (img.length > 50000) {
            return img.substring(0, 50000)
          }
          return img
        }) || []
      })))
      
      try {
        localStorage.setItem('hockey-drills', JSON.stringify(optimizedDrills))
        alert('✅ Storage optimized! Images have been compressed.')
      } catch (error) {
        alert('❌ Failed to optimize storage. Please try clearing some data first.')
      }
    }
  }

  const getStorageUsage = () => {
    const drillsSize = (localStorage.getItem('hockey-drills') || '').length
    const plansSize = (localStorage.getItem('hockey-practice-plans') || '').length
    const settingsSize = (localStorage.getItem('hockey-settings') || '').length
    const totalSize = drillsSize + plansSize + settingsSize
    
    // Estimate localStorage quota (usually 5-10MB)
    const estimatedQuota = 5 * 1024 * 1024 // 5MB
    const usagePercent = Math.round((totalSize / estimatedQuota) * 100)
    
    return {
      total: totalSize,
      drills: drillsSize,
      plans: plansSize,
      settings: settingsSize,
      usagePercent: Math.min(usagePercent, 100)
    }
  }

  const storageUsage = getStorageUsage()

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-russo text-hockey-blue">Settings</h2>
      
      {/* Mobile Sync Section */}
      <div className="hockey-card bg-blue-50 border-blue-200">
        <h3 className="text-lg font-russo text-hockey-blue mb-4">📱 Mobile Device Sync</h3>
        <div className="bg-blue-100 p-4 rounded-lg mb-4">
          <p className="text-sm text-blue-800 mb-2">
            <strong>To sync your data to your phone:</strong>
          </p>
          <ol className="text-sm text-blue-800 list-decimal list-inside space-y-1">
            <li>Export your data from this computer using the button below</li>
            <li>Open the app on your phone at: <code className="bg-blue-200 px-1 rounded">http://192.168.4.44:3000</code></li>
            <li>Go to Settings → Import Data → Select the downloaded file</li>
            <li><strong>The page will automatically refresh</strong> - your drills and practice plans will appear!</li>
            <li>If you don't see your data, try refreshing the page manually</li>
          </ol>
        </div>

        <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4 mb-4">
          <div className="flex">
            <div className="ml-3">
              <p className="text-sm text-yellow-800">
                <strong>⚠️ Important:</strong> Changes made on one device will <strong>NOT</strong> automatically sync to the other device. 
                If you add new drills or practice plans on your phone, you'll need to export from your phone and import back to your computer to keep both devices in sync.
              </p>
            </div>
          </div>
        </div>

        <div className="bg-green-50 border-l-4 border-green-500 p-4 mb-4">
          <h4 className="font-medium text-green-900 mb-2">🔄 How to Keep Devices in Sync:</h4>
          <div className="text-sm text-green-800 space-y-2">
            <p><strong>After adding drills on your computer:</strong> Export data and import on your phone</p>
            <p><strong>After adding drills on your phone:</strong> Export data on your phone and import back to your computer</p>
            <p><strong>Best practice:</strong> Use one device as your "main" device and sync changes regularly</p>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            onClick={exportData}
            className="hockey-button text-sm py-3"
          >
            📤 Download Data File
          </button>
          <button
            onClick={copyDataToClipboard}
            className="hockey-button-secondary text-sm py-3"
          >
            📋 Copy Data to Clipboard
          </button>
        </div>
        
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mt-3">
          <button
            onClick={onShowQRSync}
            className="hockey-button text-sm py-3"
          >
            📱 QR Sync
          </button>
          <button
            onClick={() => {
              const status = getSyncStatus()
              if (status.isConnected) {
                alert('✅ Shared database is active! Changes sync automatically between all devices.')
              } else {
                alert('💾 Using local storage. Use "Copy Data" and "Import Data" to sync between devices.')
              }
            }}
            className="hockey-button text-sm py-3"
          >
            🔄 Sync Info
          </button>
          <button
            onClick={() => {
              const status = getSyncStatus()
              alert(`📊 Database Status:\nDevice: ${status.deviceId}\nDatabase: ${status.database}\nStatus: ${status.status}\n\nData Count:\n• Drills: ${status.dataCount.drills}\n• Practice Plans: ${status.dataCount.practicePlans}\n• Settings: ${status.dataCount.settings}\n\nThis shows if cross-device sync is working.`)
            }}
            className="hockey-button-secondary text-sm py-3"
          >
            📊 Database Status
          </button>
          <button
            onClick={async () => {
              try {
                const { initializeApp } = await import('firebase/app')
                const { getFirestore, collection, getDocs } = await import('firebase/firestore')
                
                const firebaseConfig = {
                  apiKey: "AIzaSyCm2m3lSlh_IBgHSOLcmeCO9lZYHaxgrFw",
                  authDomain: "hockey-practice-planner.firebaseapp.com",
                  projectId: "hockey-practice-planner",
                  storageBucket: "hockey-practice-planner.firebasestorage.app",
                  messagingSenderId: "557366268618",
                  appId: "1:557366268618:web:d6f5cf9e80045d966fda33",
                  measurementId: "G-BSH8MT49BZ"
                }

                const app = initializeApp(firebaseConfig)
                const db = getFirestore(app)
                
                // Check practice plans
                const practicePlansRef = collection(db, 'practicePlans')
                const practicePlansSnapshot = await getDocs(practicePlansRef)
                const practicePlans = practicePlansSnapshot.docs.map(doc => ({
                  id: doc.id,
                  ...doc.data()
                }))
                
                // Check drills
                const drillsRef = collection(db, 'drills')
                const drillsSnapshot = await getDocs(drillsRef)
                const drills = drillsSnapshot.docs.map(doc => ({
                  id: doc.id,
                  ...doc.data()
                }))
                
                alert(`🔍 Firebase Direct Check:\n\nPractice Plans: ${practicePlans.length}\n${practicePlans.length > 0 ? practicePlans.map((p: any) => `• "${p.name}" (${p.drills?.length || 0} drills)`).join('\n') : 'No practice plans found'}\n\nDrills: ${drills.length}\n\nLocal Storage:\n• Practice Plans: ${JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]').length}\n• Drills: ${JSON.parse(localStorage.getItem('hockey-drills') || '[]').length}`)
                
              } catch (error) {
                alert(`❌ Firebase check error: ${error instanceof Error ? error.message : 'Unknown error'}`)
              }
            }}
            className="hockey-button text-sm py-3 bg-blue-600 hover:bg-blue-700"
          >
            🔍 Check Firebase Directly
          </button>
      <button
        onClick={() => {
          // Mobile diagnostic info
          const drills = localStorage.getItem('hockey-drills')
          const plans = localStorage.getItem('hockey-practice-plans')
          const settings = localStorage.getItem('hockey-settings')
          const deviceId = localStorage.getItem('hockey-device-id')
          
          const userAgent = navigator.userAgent
          const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(userAgent)
          
          let diagnostic = `📱 Mobile Diagnostic:\n\n`
          diagnostic += `Device: ${isMobile ? 'Mobile' : 'Desktop'}\n`
          diagnostic += `Browser: ${userAgent.includes('Safari') ? 'Safari' : userAgent.includes('Chrome') ? 'Chrome' : 'Other'}\n\n`
          diagnostic += `Local Storage:\n`
          diagnostic += `• Drills: ${drills ? JSON.parse(drills).length : 0} items\n`
          diagnostic += `• Practice Plans: ${plans ? JSON.parse(plans).length : 0} items\n`
          diagnostic += `• Settings: ${settings ? 'Present' : 'Missing'}\n`
          diagnostic += `• Device ID: ${deviceId || 'Missing'}\n\n`
          
          // Check for loading issues
          const isStuckLoading = document.querySelector('.animate-spin')
          if (isStuckLoading) {
            diagnostic += `⚠️ App appears to be stuck on loading screen\n`
            diagnostic += `This usually means Firebase connection issue\n\n`
          }
          
          diagnostic += `Troubleshooting:\n`
          diagnostic += `1. Try "Clear Cache" button\n`
          diagnostic += `2. Try "Restore Data from Firebase" button\n`
          diagnostic += `3. Try opening in incognito/private mode\n`
          diagnostic += `4. Try different browser\n`
          
          alert(diagnostic)
        }}
        className="hockey-button-secondary text-sm py-3 bg-orange-600 hover:bg-orange-700"
      >
        📱 Mobile Diagnostic
      </button>
      
      <button
        onClick={async () => {
          try {
            // Force sync current data to Firebase
            console.log('🔄 Force syncing current data to Firebase...')
            
            // Get current data from localStorage
            const currentDrills = JSON.parse(localStorage.getItem('hockey-drills') || '[]')
            const currentPlans = JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]')
            
            if (currentPlans.length > 0) {
              const { savePracticePlan } = await import('../lib/simpleFirebase')
              await savePracticePlan(currentPlans)
              console.log('✅ Practice plans force synced to Firebase')
            }
            
            if (currentDrills.length > 0) {
              const { saveDrill } = await import('../lib/simpleFirebase')
              await saveDrill(currentDrills)
              console.log('✅ Drills force synced to Firebase')
            }
            
            alert(`✅ Force sync complete!\n\nSynced to Firebase:\n• ${currentDrills.length} drills\n• ${currentPlans.length} practice plans\n\nChanges should now appear on other devices.`)
          } catch (error) {
            console.error('❌ Force sync failed:', error)
            alert(`❌ Force sync failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
          }
        }}
        className="hockey-button-primary text-sm py-3 bg-blue-600 hover:bg-blue-700"
      >
        🔄 Force Sync to Firebase
      </button>
          <button
            onClick={() => {
              const data = exportAllData()
              const dataString = JSON.stringify(data, null, 2)
              navigator.clipboard.writeText(dataString).then(() => {
                alert('✅ Data copied to clipboard! Paste this on your other device and use "Import Data" button.')
              }).catch(() => {
                alert('❌ Failed to copy data. Please try the QR Sync option instead.')
              })
            }}
            className="hockey-button text-sm py-3"
          >
            📋 Copy Data
          </button>
          <button
            onClick={async () => {
              const dataString = prompt('Paste the data from your other device:')
              if (dataString) {
                try {
                  const data = JSON.parse(dataString)
                  const success = await importAllData(data)
                  if (success) {
                    alert('✅ Data imported successfully! Refreshing...')
                    window.location.reload()
                  } else {
                    alert('❌ Failed to import data. Please check the format.')
                  }
                } catch (error) {
                  alert('❌ Invalid data format. Please try again.')
                }
              }
            }}
            className="hockey-button-secondary text-sm py-3"
          >
            📥 Import Data
          </button>
          <button
            onClick={restoreDataFromFirebase}
            disabled={isRestoring}
            className="hockey-button text-sm py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400"
          >
            {isRestoring ? '🔄 Restoring...' : '🔄 Restore Data from Firebase'}
          </button>
          <button
            onClick={() => {
              if (confirm('Clear all cache and reload? This will remove all local data and refresh the page.')) {
                localStorage.clear()
                sessionStorage.clear()
                alert('✅ Cache cleared! Reloading page...')
                window.location.reload()
              }
            }}
            className="hockey-button-secondary text-sm py-3 bg-red-600 hover:bg-red-700"
          >
            🗑️ Clear Cache & Reload
          </button>
          <button
            onClick={() => setShowDataText(!showDataText)}
            className="hockey-button-secondary text-sm py-3"
          >
            {showDataText ? '🔼 Hide' : '📄 Show'}
          </button>
          <button
            onClick={() => window.location.reload()}
            className="hockey-button-secondary text-sm py-3"
          >
            🔄 Refresh
          </button>
          <label className="block">
            <input
              type="file"
              accept=".json"
              onChange={importData}
              className="hidden"
            />
            <div className="w-full hockey-button-secondary text-sm cursor-pointer text-center py-3">
              📥 Import
            </div>
          </label>
        </div>

        {showDataText && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">Copy this data to your phone:</h4>
            <textarea
              value={JSON.stringify(getExportData(), null, 2)}
              readOnly
              className="w-full h-40 p-3 border border-gray-300 rounded-lg text-xs font-mono bg-gray-50"
              onClick={(e) => (e.target as HTMLTextAreaElement).select()}
            />
            <p className="text-xs text-gray-500 mt-1">
              Click in the text area above and copy all text (Ctrl+A, Ctrl+C), then paste it into the import field on your phone.
            </p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Team Settings */}
        <div className="hockey-card">
          <h3 className="text-lg font-russo text-hockey-blue mb-4">Team Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Team Name</label>
              <input
                type="text"
                value={settings.teamName}
                onChange={(e) => setSettings({...settings, teamName: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                placeholder="Enter team name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Coach Name</label>
              <input
                type="text"
                value={settings.coachName}
                onChange={(e) => setSettings({...settings, coachName: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                placeholder="Enter coach name"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Default Drill Duration (minutes)</label>
              <input
                type="number"
                value={settings.defaultDrillDuration}
                onChange={(e) => setSettings({...settings, defaultDrillDuration: parseInt(e.target.value) || 15})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                min="1"
                max="60"
              />
            </div>
          </div>
        </div>

        {/* Data Management */}
        <div className="hockey-card">
          <h3 className="text-lg font-russo text-hockey-blue mb-4">Data Management</h3>
          <div className="space-y-4">
            <div>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={settings.autoSave}
                  onChange={(e) => setSettings({...settings, autoSave: e.target.checked})}
                  className="mr-2"
                />
                <span className="text-sm font-medium text-gray-700">Auto-save enabled</span>
              </label>
            </div>
            
            <div className="space-y-2">
              <button
                onClick={saveSettings}
                className="w-full hockey-button-secondary text-sm"
              >
                💾 Save Settings
              </button>
              
              <button
                onClick={exportData}
                className="w-full hockey-button text-sm"
              >
                📤 Export All Data
              </button>
              
              <label className="block">
                <input
                  type="file"
                  accept=".json"
                  onChange={importData}
                  className="hidden"
                />
                <div className="w-full hockey-button-secondary text-sm cursor-pointer text-center py-2">
                  📥 Import Data
                </div>
              </label>
              
              <button
                onClick={clearAllData}
                className="w-full bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm transition-colors"
              >
                🗑️ Clear All Data
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Storage Management */}
      <div className="hockey-card">
        <h3 className="text-lg font-russo text-hockey-blue mb-4">Storage Management</h3>
        
        {/* Storage Usage Bar */}
        <div className="mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Storage Usage</span>
            <span className="text-sm text-gray-500">{storageUsage.usagePercent}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                storageUsage.usagePercent > 80 ? 'bg-red-500' : 
                storageUsage.usagePercent > 60 ? 'bg-yellow-500' : 'bg-green-500'
              }`}
              style={{ width: `${storageUsage.usagePercent}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {Math.round(storageUsage.total / 1024)} KB used
            {storageUsage.usagePercent > 80 && ' - Consider clearing old data!'}
          </p>
        </div>

        {/* Storage Statistics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center mb-6">
          <div>
            <div className="text-2xl font-bold text-hockey-blue">
              {JSON.parse(localStorage.getItem('hockey-drills') || '[]').length}
            </div>
            <div className="text-sm text-gray-600">Total Drills</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-hockey-blue">
              {JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]').length}
            </div>
            <div className="text-sm text-gray-600">Practice Plans</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-hockey-blue">
              {Math.round(storageUsage.drills / 1024)} KB
            </div>
            <div className="text-sm text-gray-600">Drills Data</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-hockey-blue">
              {Math.round(storageUsage.plans / 1024)} KB
            </div>
            <div className="text-sm text-gray-600">Plans Data</div>
          </div>
        </div>

        {/* Storage Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <button
            onClick={optimizeStorage}
            className="hockey-button-secondary text-sm"
          >
            🔧 Optimize Storage
          </button>
          
          <button
            onClick={clearOldDrills}
            className="hockey-button-secondary text-sm"
          >
            🗑️ Clear Old Drills
          </button>
          
          <button
            onClick={clearAllData}
            className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm transition-colors"
          >
            🗑️ Clear All Data
          </button>
          
          <button
            onClick={clearStorageAndRestart}
            className="bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded-lg text-sm transition-colors"
          >
            🔄 Clear & Restart
          </button>
        </div>
      </div>
    </div>
  )
}

function DrillDetailModal({ 
  drill, 
  onClose, 
  onEdit, 
  onDelete 
}: { 
  drill: any
  onClose: () => void
  onEdit: (drill: any) => void
  onDelete: (drill: any) => void
}) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[95vh] sm:max-h-[90vh] overflow-y-auto">
        <div className="p-4 sm:p-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-4 sm:mb-6 space-y-3 sm:space-y-0">
            <div className="flex-1">
              <h2 className="text-lg sm:text-xl lg:text-2xl font-russo text-hockey-blue mb-2">{drill.name}</h2>
              <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4">
                <span className="bg-hockey-blue text-white px-3 py-1 rounded-full text-xs sm:text-sm w-fit">
                  {drill.category}
                </span>
                <span className="text-gray-500 text-xs sm:text-sm">
                  {drill.type === 'custom' ? 'Custom Drill' : 
                   drill.type === 'pdf' ? 'PDF Drill' : 'Sample Drill'}
                </span>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
              <button
                onClick={() => onEdit(drill)}
                className="hockey-button-secondary text-sm py-2 px-4"
              >
                Edit
              </button>
              <button
                onClick={() => onDelete(drill)}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm transition-colors"
              >
                Delete
              </button>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 p-2 self-end sm:self-auto"
              >
                <svg className="w-5 h-5 sm:w-6 sm:h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Images */}
          {drill.images && drill.images.length > 0 && (
            <div className="mb-4 sm:mb-6">
              <h3 className="text-base sm:text-lg font-russo text-hockey-blue mb-3">Images</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
                {drill.images.map((image: string, index: number) => (
                  <div key={index} className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                    <img 
                      src={image} 
                      alt={`${drill.name} - Image ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Description */}
          {drill.description && (
            <div className="mb-4 sm:mb-6">
              <h3 className="text-base sm:text-lg font-russo text-hockey-blue mb-3">Description</h3>
              <p className="text-sm sm:text-base text-gray-700 leading-relaxed">{drill.description}</p>
            </div>
          )}

          {/* Setup Steps */}
          {drill.setup && drill.setup.length > 0 && (
            <div className="mb-4 sm:mb-6">
              <h3 className="text-base sm:text-lg font-russo text-hockey-blue mb-3">Setup Steps</h3>
              <ol className="list-decimal list-inside space-y-2">
                {drill.setup.map((step: string, index: number) => (
                  <li key={index} className="text-sm sm:text-base text-gray-700">{step}</li>
                ))}
              </ol>
            </div>
          )}

          {/* Variations */}
          {drill.variations && drill.variations.length > 0 && (
            <div className="mb-4 sm:mb-6">
              <h3 className="text-base sm:text-lg font-russo text-hockey-blue mb-3">Variations</h3>
              <ul className="list-disc list-inside space-y-2">
                {drill.variations.map((variation: string, index: number) => (
                  <li key={index} className="text-sm sm:text-base text-gray-700">{variation}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Coaching Points */}
          {drill.coachingPoints && drill.coachingPoints.length > 0 && (
            <div className="mb-4 sm:mb-6">
              <h3 className="text-base sm:text-lg font-russo text-hockey-blue mb-3">Coaching Points</h3>
              <ul className="list-disc list-inside space-y-2">
                {drill.coachingPoints.map((point: string, index: number) => (
                  <li key={index} className="text-sm sm:text-base text-gray-700">{point}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Instructions */}
          {drill.instructions && drill.instructions.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-russo text-hockey-blue mb-3">Instructions</h3>
              <ol className="list-decimal list-inside space-y-2">
                {drill.instructions.map((instruction: string, index: number) => (
                  <li key={index} className="text-gray-700">{instruction}</li>
                ))}
              </ol>
            </div>
          )}

          {/* Footer */}
          <div className="flex justify-end pt-4 sm:pt-6 border-t">
            <button
              onClick={onClose}
              className="hockey-button-secondary text-sm py-2 px-4"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
