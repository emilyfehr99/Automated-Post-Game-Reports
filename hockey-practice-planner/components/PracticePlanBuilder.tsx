'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Plus, 
  Clock, 
  Users, 
  Play, 
  Edit, 
  Trash2, 
  Save,
  Share2,
  Download,
  X
} from 'lucide-react'
import DraggableDrillList from './DraggableDrillList'

interface Drill {
  id: string
  name: string
  description: string
  duration?: number // Made optional since drills don't have duration by default
  category: string
  images?: string[]
  type?: string
  setup?: string[]
  variations?: string[]
  coachingPoints?: string[]
  createdAt?: string
}

interface PracticePlan {
  id: string
  name: string
  description: string
  drills: Drill[]
  totalDuration: number
  createdAt: Date
}

interface PracticePlanBuilderProps {
  onSave: (plan: PracticePlan) => void
  onClose: () => void
  initialPlan?: PracticePlan
  availableDrills: Drill[]
}

export default function PracticePlanBuilder({ onSave, onClose, initialPlan, availableDrills }: PracticePlanBuilderProps) {
  const [plan, setPlan] = useState<PracticePlan>(
    initialPlan || {
      id: '',
      name: '',
      description: '',
      drills: [],
      totalDuration: 0,
      createdAt: new Date(),
    }
  )

  const [showDrillLibrary, setShowDrillLibrary] = useState(false)
  const [isSaving, setIsSaving] = useState(false)



  const addDrill = (drill: Drill) => {
    // Prompt for duration when adding drill to practice plan
    const duration = prompt(`Set duration for "${drill.name}" (in minutes):`, '10')
    if (duration === null) return // User cancelled
    
    const drillDuration = parseInt(duration) || 10
    const drillWithDuration = { ...drill, duration: drillDuration }
    
    const newDrills = [...plan.drills, drillWithDuration]
    const totalDuration = newDrills.reduce((sum, d) => sum + (d.duration || 0), 0)
    
    setPlan({
      ...plan,
      drills: newDrills,
      totalDuration,
    })
  }

  const removeDrill = (drillId: string) => {
    const newDrills = plan.drills.filter(d => d.id !== drillId)
    const totalDuration = newDrills.reduce((sum, d) => sum + (d.duration || 0), 0)
    
    setPlan({
      ...plan,
      drills: newDrills,
      totalDuration,
    })
  }

  const reorderDrills = (reorderedDrills: Drill[]) => {
    const totalDuration = reorderedDrills.reduce((sum, d) => sum + (d.duration || 0), 0)
    
    setPlan({
      ...plan,
      drills: reorderedDrills,
      totalDuration,
    })
  }

  const updateDrillDuration = (drillId: string, duration: number) => {
    const newDrills = plan.drills.map(d => 
      d.id === drillId ? { ...d, duration } : d
    )
    const totalDuration = newDrills.reduce((sum, d) => sum + (d.duration || 0), 0)
    
    setPlan({
      ...plan,
      drills: newDrills,
      totalDuration,
    })
  }

  const handleSave = async () => {
    if (!plan.name.trim()) {
      alert('⚠️ Please enter a practice plan name')
      return
    }
    
    setIsSaving(true)
    
    const planToSave = {
      ...plan,
      id: plan.id || Date.now().toString(),
    }
    
    
    try {
      onSave(planToSave)
      // Show success state briefly
      setTimeout(() => setIsSaving(false), 1000)
    } catch (error) {
      console.error('Error saving practice plan:', error)
      setIsSaving(false)
    }
  }

  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0) {
      return `${hours}h ${mins}m`
    }
    return `${mins}m`
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-2 sm:p-4"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white rounded-xl shadow-2xl max-w-6xl w-full max-h-[95vh] sm:max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="bg-hockey-blue text-white p-4 sm:p-6">
          <div className="flex justify-between items-center">
            <h2 className="text-lg sm:text-xl lg:text-2xl font-russo">{initialPlan ? 'Edit Practice Plan' : 'Practice Plan Builder'}</h2>
            <div className="flex space-x-4">
              <button
                onClick={handleSave}
                className="bg-white text-hockey-blue px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors flex items-center"
              >
                <Save className="w-4 h-4 mr-2" />
                {initialPlan ? 'Update Plan' : 'Save Plan'}
              </button>
              <button
                onClick={onClose}
                className="text-white hover:text-gray-300 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
          </div>
        </div>

        <div className="flex flex-col sm:flex-row h-[500px] sm:h-[600px]">
          {/* Drill Library */}
          {showDrillLibrary && (
            <div className="w-full sm:w-80 bg-gray-100 p-4 border-r border-b sm:border-b-0 overflow-y-auto">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-russo text-hockey-blue">Drill Library</h3>
                <button
                  onClick={() => setShowDrillLibrary(false)}
                  className="text-gray-500 hover:text-gray-700"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
              
              <div className="space-y-3">
                {availableDrills.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-gray-500 mb-2">No drills available</p>
                    <p className="text-sm text-gray-400">Create some drills first to build practice plans</p>
                  </div>
                ) : (
                  availableDrills.map((drill) => (
                    <div
                      key={drill.id}
                      className="bg-white rounded-lg p-3 shadow-sm hover:shadow-md transition-shadow cursor-pointer"
                      onClick={() => addDrill(drill)}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium text-sm">{drill.name}</h4>
                        <span className="text-xs bg-hockey-blue text-white px-2 py-1 rounded">
                          {drill.category}
                        </span>
                      </div>
                      <p className="text-xs text-gray-600 mb-2">{drill.description}</p>
                      <div className="flex items-center justify-between text-xs text-gray-500">
                        <div className="flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {drill.duration || 0} min
                        </div>
                        {drill.images && drill.images.length > 0 && (
                          <span className="text-hockey-blue">📷 {drill.images.length} image{drill.images.length > 1 ? 's' : ''}</span>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}

          {/* Main Content */}
          <div className="flex-1 p-6 overflow-y-auto">
            {/* Plan Details */}
            <div className="mb-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Practice Plan Name
                  </label>
                  <input
                    type="text"
                    value={plan.name}
                    onChange={(e) => setPlan({ ...plan, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                    placeholder="Enter practice plan name..."
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Total Duration
                  </label>
                  <div className="px-3 py-2 bg-gray-100 rounded-lg text-gray-700">
                    {formatTime(plan.totalDuration)}
                  </div>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <textarea
                  value={plan.description}
                  onChange={(e) => setPlan({ ...plan, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent h-20"
                  placeholder="Enter practice plan description..."
                />
              </div>
            </div>

            {/* Drills List */}
            <div className="mb-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-russo text-hockey-blue">Practice Drills</h3>
                <button
                  onClick={() => setShowDrillLibrary(true)}
                  className="hockey-button flex items-center"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Drill
                </button>
              </div>

              {plan.drills.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <Play className="w-12 h-12 mx-auto mb-4 text-gray-300" />
                  <p>No drills added yet. Click "Add Drill" to get started.</p>
                </div>
              ) : (
                <div>
                  <div className="flex justify-between items-center mb-4">
                    <h4 className="font-medium text-gray-900">Practice Drills</h4>
                    {plan.drills.length > 1 && (
                      <p className="text-sm text-gray-500">
                        Drag to reorder
                      </p>
                    )}
                  </div>
                  <DraggableDrillList
                    drills={plan.drills}
                    onReorder={reorderDrills}
                    showImages={false}
                    compact={true}
                  />
                  
                  {/* Duration controls for each drill */}
                  <div className="mt-4 space-y-2">
                    {plan.drills.map((drill) => (
                      <div key={drill.id} className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
                        <div className="flex items-center">
                          <span className="text-sm font-medium text-gray-700 mr-3">
                            {drill.name}
                          </span>
                        </div>
                        <div className="flex items-center text-sm text-gray-500">
                          <Clock className="w-4 h-4 mr-1" />
                          <input
                            type="number"
                            value={drill.duration || 0}
                            onChange={(e) => updateDrillDuration(drill.id, parseInt(e.target.value) || 0)}
                            className="w-16 px-2 py-1 border border-gray-300 rounded text-center"
                            min="1"
                          />
                          <span className="ml-1">min</span>
                          <button
                            onClick={() => removeDrill(drill.id)}
                            className="ml-3 text-red-500 hover:text-red-700 transition-colors"
                            title="Remove drill"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Summary */}
            {plan.drills.length > 0 && (
              <div className="bg-ice-blue rounded-lg p-4">
                <h4 className="font-russo text-hockey-blue mb-2">Practice Summary</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-gray-600">Total Drills:</span>
                    <span className="ml-2 font-bold">{plan.drills.length}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Total Time:</span>
                    <span className="ml-2 font-bold">{formatTime(plan.totalDuration)}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Categories:</span>
                    <span className="ml-2 font-bold">
                      {Array.from(new Set(plan.drills.map(d => d.category))).length}
                    </span>
                  </div>
                  <div>
                    <span className="text-gray-600">Avg Drill Time:</span>
                    <span className="ml-2 font-bold">
                      {Math.round(plan.totalDuration / plan.drills.length)}m
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
