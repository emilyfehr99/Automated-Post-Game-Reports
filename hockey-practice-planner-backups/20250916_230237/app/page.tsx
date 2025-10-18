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
  Download
} from 'lucide-react'
import DrillDrawingTool from '@/components/DrillDrawingTool'
import PracticePlanBuilder from '@/components/PracticePlanBuilder'
import DrillPreviewModal from '@/components/DrillPreviewModal'
import SimpleDrillCreator from '@/components/SimpleDrillCreator'
import PracticePlanDetailModal from '@/components/PracticePlanDetailModal'

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
  const [settings, setSettings] = useState({
    teamName: '',
    coachName: '',
    season: '',
    level: ''
  })

  // Load data from localStorage on component mount
  useEffect(() => {
    const savedDrills = localStorage.getItem('hockey-drills')
    const savedPlans = localStorage.getItem('hockey-practice-plans')
    const savedSettings = localStorage.getItem('hockey-settings')
    
    if (savedDrills) {
      const parsedDrills = JSON.parse(savedDrills)
      setDrills(parsedDrills)
      console.log('✅ Loaded drills from previous session:', parsedDrills.length)
    }
    
    if (savedPlans) {
      const parsedPlans = JSON.parse(savedPlans)
      setPracticePlans(parsedPlans)
      console.log('✅ Loaded practice plans from previous session:', parsedPlans.length)
    }
    
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings))
      console.log('✅ Loaded settings from previous session')
    }
    
    setIsLoading(false)
    console.log('✅ Session data loaded successfully - ready to work!')
  }, [])

  // Save drills to localStorage whenever drills change (with error handling)
  useEffect(() => {
    if (drills.length === 0) return // Don't save on initial load
    
    setIsAutoSaving(true)
    
    try {
      // Simple compression - just limit image size
      const drillsData = drills.map(drill => ({
        ...drill,
        // Limit image size to prevent quota issues
        images: drill.images?.map((img: string) => {
          // If image is too large, truncate it (temporary fix)
          if (img.length > 200000) { // 200KB limit
            console.warn('Image too large, truncating:', img.length)
            return img.substring(0, 200000) // Truncate to 200KB
          }
          return img
        }) || []
      }))
      
      localStorage.setItem('hockey-drills', JSON.stringify(drillsData))
      console.log('✅ Drills auto-saved to localStorage')
      
      // Hide auto-save indicator after a short delay
      setTimeout(() => setIsAutoSaving(false), 1000)
    } catch (error) {
      console.error('Failed to save drills to localStorage:', error)
      setIsAutoSaving(false)
      // If quota exceeded, try to clear old data and save again
      if (error instanceof DOMException && error.name === 'QuotaExceededError') {
        alert('⚠️ Storage quota exceeded. Please clear some data in Settings or export your data.')
      }
    }
  }, [drills])

  // Save practice plans to localStorage whenever practicePlans change (with error handling)
  useEffect(() => {
    if (practicePlans.length === 0) return // Don't save on initial load
    
    setIsAutoSaving(true)
    
    try {
      localStorage.setItem('hockey-practice-plans', JSON.stringify(practicePlans))
      console.log('✅ Practice plans auto-saved to localStorage')
      
      // Hide auto-save indicator after a short delay
      setTimeout(() => setIsAutoSaving(false), 1000)
    } catch (error) {
      console.error('Failed to save practice plans to localStorage:', error)
      setIsAutoSaving(false)
      if (error instanceof DOMException && error.name === 'QuotaExceededError') {
        alert('⚠️ Storage quota exceeded. Please clear some data in Settings or export your data.')
      }
    }
  }, [practicePlans])

  // Save settings to localStorage whenever settings change (with error handling)
  useEffect(() => {
    try {
      localStorage.setItem('hockey-settings', JSON.stringify(settings))
      console.log('✅ Settings auto-saved to localStorage')
    } catch (error) {
      console.error('Failed to save settings to localStorage:', error)
      if (error instanceof DOMException && error.name === 'QuotaExceededError') {
        alert('⚠️ Storage quota exceeded. Please clear some data in Settings or export your data.')
      }
    }
  }, [settings])

  // Helper function to compress images (simplified)
  const compressImage = (base64: string): string => {
    try {
      // If image is already small enough, return as is
      if (base64.length < 50000) {
        return base64
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
      }) as string
    } catch (error) {
      console.error('Failed to compress image:', error)
      return base64 // Return original if compression fails
    }
  }

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Play },
    { id: 'drills', label: 'Drill Library', icon: Search },
    { id: 'practice', label: 'Practice Plans', icon: Calendar },
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
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-russo">Hockey Practice Planner</h1>
            </div>
            <div className="flex items-center space-x-4">
              {/* Auto-save indicator */}
              {isAutoSaving && (
                <div className="flex items-center text-sm text-gray-500">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-hockey-blue mr-2"></div>
                  Auto-saving...
                </div>
              )}
              
              <button 
                onClick={() => {
                  // Force save to localStorage
                  localStorage.setItem('hockey-drills', JSON.stringify(drills))
                  localStorage.setItem('hockey-practice-plans', JSON.stringify(practicePlans))
                  alert('✅ All data saved successfully!')
                }}
                className="hockey-button-secondary"
                title="Force save all data"
              >
                <Download className="w-4 h-4 mr-2" />
                Force Save
              </button>
              <button className="hockey-button-secondary">
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </button>
              <button className="hockey-button">
                <Download className="w-4 h-4 mr-2" />
                Export
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center px-3 py-4 text-sm font-medium border-b-2 transition-colors duration-200 ${
                    activeTab === tab.id
                      ? 'border-hockey-blue text-hockey-blue'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              )
            })}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
        {activeTab === 'create' && (
          <CreateView 
            onOpenPracticeBuilder={() => setShowPracticePlanBuilder(true)}
            onOpenDrillDrawing={() => setShowDrillDrawingTool(true)}
            onOpenSimpleDrillCreator={() => setShowSimpleDrillCreator(true)}
          />
        )}
        {activeTab === 'team' && <TeamView />}
        {activeTab === 'settings' && <SettingsView />}
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
            setDrills([...drills, drillData])
            setShowSimpleDrillCreator(false)
            alert(`Drill "${drillData.name}" created successfully!`)
          }}
          onClose={() => setShowSimpleDrillCreator(false)}
        />
      )}

      {showPracticePlanBuilder && (
        <PracticePlanBuilder
          onSave={(plan) => {
            setPracticePlans([...practicePlans, plan])
            setShowPracticePlanBuilder(false)
            alert('✅ Practice plan saved successfully!')
          }}
          onClose={() => setShowPracticePlanBuilder(false)}
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
            // For now, just show an alert - this would open edit mode
            alert(`Edit drill: ${drill.name}`)
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
            // TODO: Implement practice plan editing
            console.log('Edit practice plan:', plan)
          }}
          onDelete={(plan) => {
            if (confirm(`Are you sure you want to delete "${plan.name}"?`)) {
              setPracticePlans(practicePlans.filter(p => p.id !== plan.id))
              setShowPracticePlanDetail(false)
              setSelectedPracticePlan(null)
            }
          }}
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

function SettingsView() {
  const [settings, setSettings] = useState({
    teamName: 'My Hockey Team',
    coachName: '',
    defaultDrillDuration: 15,
    autoSave: true,
    theme: 'hockey'
  })

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
    const data = {
      drills: JSON.parse(localStorage.getItem('hockey-drills') || '[]'),
      practicePlans: JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]'),
      settings: settings,
      exportDate: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `hockey-practice-planner-backup-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const importData = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target?.result as string)
          if (data.drills) localStorage.setItem('hockey-drills', JSON.stringify(data.drills))
          if (data.practicePlans) localStorage.setItem('hockey-practice-plans', JSON.stringify(data.practicePlans))
          if (data.settings) {
            setSettings(data.settings)
            localStorage.setItem('hockey-settings', JSON.stringify(data.settings))
          }
          alert('✅ Data imported successfully! Please refresh the page.')
        } catch (error) {
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
        images: await Promise.all(drill.images?.map(async (img: string) => {
          if (img.length > 50000) { // Compress images larger than 50KB
            return await compressImage(img)
          }
          return img
        }) || [])
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
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-russo text-hockey-blue mb-2">{drill.name}</h2>
              <div className="flex items-center space-x-4">
                <span className="bg-hockey-blue text-white px-3 py-1 rounded-full text-sm">
                  {drill.category}
                </span>
                <span className="text-gray-600">
                  {drill.duration} minutes
                </span>
                <span className="text-gray-500 text-sm">
                  {drill.type === 'custom' ? 'Custom Drill' : 
                   drill.type === 'pdf' ? 'PDF Drill' : 'Sample Drill'}
                </span>
              </div>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => onEdit(drill)}
                className="hockey-button-secondary text-sm"
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
                className="text-gray-400 hover:text-gray-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Images */}
          {drill.images && drill.images.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-russo text-hockey-blue mb-3">Images</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
            <div className="mb-6">
              <h3 className="text-lg font-russo text-hockey-blue mb-3">Description</h3>
              <p className="text-gray-700 leading-relaxed">{drill.description}</p>
            </div>
          )}

          {/* Setup Steps */}
          {drill.setupSteps && drill.setupSteps.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-russo text-hockey-blue mb-3">Setup Steps</h3>
              <ol className="list-decimal list-inside space-y-2">
                {drill.setupSteps.map((step: string, index: number) => (
                  <li key={index} className="text-gray-700">{step}</li>
                ))}
              </ol>
            </div>
          )}

          {/* Variations */}
          {drill.variations && drill.variations.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-russo text-hockey-blue mb-3">Variations</h3>
              <ul className="list-disc list-inside space-y-2">
                {drill.variations.map((variation: string, index: number) => (
                  <li key={index} className="text-gray-700">{variation}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Coaching Points */}
          {drill.coachingPoints && drill.coachingPoints.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-russo text-hockey-blue mb-3">Coaching Points</h3>
              <ul className="list-disc list-inside space-y-2">
                {drill.coachingPoints.map((point: string, index: number) => (
                  <li key={index} className="text-gray-700">{point}</li>
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
          <div className="flex justify-end space-x-4 pt-6 border-t">
            <button
              onClick={onClose}
              className="hockey-button-secondary"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
