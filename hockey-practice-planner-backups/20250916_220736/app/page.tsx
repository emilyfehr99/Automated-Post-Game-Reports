'use client'

import { useState } from 'react'
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

export default function Home() {
  const [activeTab, setActiveTab] = useState('dashboard')
  const [showDrillDrawingTool, setShowDrillDrawingTool] = useState(false)
  const [showSimpleDrillCreator, setShowSimpleDrillCreator] = useState(false)
  const [showPracticePlanBuilder, setShowPracticePlanBuilder] = useState(false)
  const [showDrillPreview, setShowDrillPreview] = useState(false)
  const [previewDrill, setPreviewDrill] = useState<any>(null)
  const [practicePlans, setPracticePlans] = useState<any[]>([])
  const [drills, setDrills] = useState<any[]>([
    {
      id: '1',
      name: 'Warm-up Skating',
      description: 'Basic skating drills to get players moving',
      category: 'Warm-up',
      duration: 10,
      type: 'sample'
    },
    {
      id: '2',
      name: 'Passing Drill',
      description: 'Partner passing with focus on accuracy',
      category: 'Skills',
      duration: 15,
      type: 'sample'
    },
    {
      id: '3',
      name: 'Power Play Setup',
      description: 'Practice power play positioning and movement',
      category: 'Systems',
      duration: 20,
      type: 'sample'
    },
    {
      id: '4',
      name: 'Breakout Drill',
      description: 'Defensive zone breakout patterns',
      category: 'Systems',
      duration: 15,
      type: 'sample'
    },
    {
      id: '5',
      name: 'Shooting Practice',
      description: 'Various shooting scenarios and techniques',
      category: 'Skills',
      duration: 25,
      type: 'sample'
    },
    {
      id: '6',
      name: 'Cool Down',
      description: 'Light skating and stretching',
      category: 'Cool-down',
      duration: 10,
      type: 'sample'
    }
  ])

  const tabs = [
    { id: 'dashboard', label: 'Dashboard', icon: Play },
    { id: 'drills', label: 'Drill Library', icon: Search },
    { id: 'practice', label: 'Practice Plans', icon: Calendar },
    { id: 'create', label: 'Create', icon: Plus },
    { id: 'team', label: 'Team', icon: Users },
    { id: 'settings', label: 'Settings', icon: Settings },
  ]

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
          />
        )}
        {activeTab === 'practice' && (
          <PracticePlansView 
            onOpenPracticeBuilder={() => setShowPracticePlanBuilder(true)}
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
          }}
          onClose={() => setShowPracticePlanBuilder(false)}
        />
      )}
    </div>
  )
}

function DashboardView({ 
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
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="font-medium">Power Play Practice</p>
              <p className="text-sm text-gray-600">Created 2 days ago</p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="font-medium">Defensive Zone Coverage</p>
              <p className="text-sm text-gray-600">Created 1 week ago</p>
            </div>
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
              <span className="font-bold">47</span>
            </div>
            <div className="flex justify-between">
              <span>Practice Plans:</span>
              <span className="font-bold">12</span>
            </div>
            <div className="flex justify-between">
              <span>Team Members:</span>
              <span className="font-bold">23</span>
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
  onAddDrillToPlan 
}: { 
  onOpenDrillDrawing: () => void
  onOpenSimpleDrillCreator: () => void
  drills: any[]
  onAddDrillToPlan: (drill: any) => void
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
            className="hockey-card hover:shadow-xl transition-shadow duration-200"
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
                onClick={() => onAddDrillToPlan(drill)}
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

function PracticePlansView({ onOpenPracticeBuilder }: { onOpenPracticeBuilder: () => void }) {
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

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4, 5, 6].map((i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="hockey-card hover:shadow-xl transition-shadow duration-200 cursor-pointer"
          >
            <div className="flex justify-between items-start mb-4">
              <h3 className="font-russo text-lg">Practice Plan {i}</h3>
              <div className="flex space-x-2">
                <button className="text-gray-400 hover:text-gray-600">
                  <Share2 className="w-4 h-4" />
                </button>
                <button className="text-gray-400 hover:text-gray-600">
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
            <p className="text-gray-600 text-sm mb-4">Created 2 days ago</p>
            <div className="space-y-2">
              <div className="flex items-center text-sm">
                <FileText className="w-4 h-4 mr-2 text-gray-400" />
                <span>8 drills</span>
              </div>
              <div className="flex items-center text-sm">
                <Video className="w-4 h-4 mr-2 text-gray-400" />
                <span>3 videos</span>
              </div>
              <div className="flex items-center text-sm">
                <Image className="w-4 h-4 mr-2 text-gray-400" />
                <span>5 images</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
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
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-russo text-hockey-blue">Settings</h2>
      <div className="hockey-card">
        <p className="text-gray-600">Settings panel coming soon...</p>
      </div>
    </div>
  )
}
