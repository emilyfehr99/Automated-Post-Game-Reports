'use client'

import { motion } from 'framer-motion'
import { 
  X, 
  Clock, 
  Users, 
  Play, 
  Edit, 
  Trash2,
  Calendar,
  FileText
} from 'lucide-react'
import DraggableDrillList from './DraggableDrillList'

interface PracticePlanDetailModalProps {
  practicePlan: any
  onClose: () => void
  onEdit: (plan: any) => void
  onDelete: (plan: any) => void
  onReorder?: (plan: any) => void
}

export default function PracticePlanDetailModal({
  practicePlan,
  onClose,
  onEdit,
  onDelete,
  onReorder
}: PracticePlanDetailModalProps) {
  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    if (hours > 0) {
      return `${hours}h ${mins}m`
    }
    return `${mins}m`
  }

  const formatDate = (date: Date | string) => {
    const d = new Date(date)
    return d.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
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
        className="bg-white rounded-lg max-w-4xl w-full max-h-[95vh] sm:max-h-[90vh] overflow-y-auto"
      >
        <div className="p-4 sm:p-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-4 sm:mb-6 space-y-3 sm:space-y-0">
            <div className="flex-1">
              <h2 className="text-lg sm:text-xl lg:text-2xl font-russo text-hockey-blue mb-2">{practicePlan.name}</h2>
              <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0 sm:space-x-4 text-xs sm:text-sm text-gray-600">
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  {formatTime(practicePlan.totalDuration)}
                </div>
                <div className="flex items-center">
                  <Users className="w-4 h-4 mr-1" />
                  {practicePlan.drills.length} drill{practicePlan.drills.length !== 1 ? 's' : ''}
                </div>
                <div className="flex items-center">
                  <Calendar className="w-4 h-4 mr-1" />
                  {formatDate(practicePlan.createdAt)}
                </div>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
              <button
                onClick={() => onEdit(practicePlan)}
                className="hockey-button-secondary text-sm py-2 px-4"
              >
                <Edit className="w-4 h-4 mr-1" />
                Edit
              </button>
              <button
                onClick={() => onDelete(practicePlan)}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm transition-colors flex items-center justify-center"
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Delete
              </button>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 p-2 self-end sm:self-auto"
              >
                <X className="w-5 h-5 sm:w-6 sm:h-6" />
              </button>
            </div>
          </div>

          {/* Description */}
          {practicePlan.description && (
            <div className="mb-6">
              <h3 className="text-lg font-russo text-hockey-blue mb-3">Description</h3>
              <p className="text-gray-700 leading-relaxed">{practicePlan.description}</p>
            </div>
          )}

          {/* Drills List */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-russo text-hockey-blue">Practice Plan Drills</h3>
              {practicePlan.drills.length > 1 && (
                <p className="text-sm text-gray-500">
                  Drag drills to reorder
                </p>
              )}
            </div>
            <DraggableDrillList
              drills={practicePlan.drills}
              onReorder={(reorderedDrills) => {
                if (onReorder) {
                  const updatedPlan = {
                    ...practicePlan,
                    drills: reorderedDrills
                  }
                  onReorder(updatedPlan)
                }
              }}
              showImages={true}
              compact={false}
            />
          </div>

          {/* Practice Plan Summary */}
          <div className="bg-hockey-blue bg-opacity-10 rounded-lg p-4">
            <h3 className="text-lg font-russo text-hockey-blue mb-3">Practice Plan Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-hockey-blue">{practicePlan.drills.length}</div>
                <div className="text-sm text-gray-600">Total Drills</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-hockey-blue">{formatTime(practicePlan.totalDuration)}</div>
                <div className="text-sm text-gray-600">Total Duration</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-hockey-blue">
                  {Array.from(new Set(practicePlan.drills.map((d: any) => d.category))).length}
                </div>
                <div className="text-sm text-gray-600">Categories</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-hockey-blue">
                  {practicePlan.drills.filter((d: any) => d.images && d.images.length > 0).length}
                </div>
                <div className="text-sm text-gray-600">Drills with Images</div>
              </div>
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end space-x-4 pt-6 border-t mt-6">
            <button
              onClick={onClose}
              className="hockey-button-secondary"
            >
              Close
            </button>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
