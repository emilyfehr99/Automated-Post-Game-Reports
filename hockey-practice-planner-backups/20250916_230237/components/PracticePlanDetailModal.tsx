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

interface PracticePlanDetailModalProps {
  practicePlan: any
  onClose: () => void
  onEdit: (plan: any) => void
  onDelete: (plan: any) => void
}

export default function PracticePlanDetailModal({
  practicePlan,
  onClose,
  onEdit,
  onDelete
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
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-start mb-6">
            <div>
              <h2 className="text-2xl font-russo text-hockey-blue mb-2">{practicePlan.name}</h2>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
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
            <div className="flex space-x-2">
              <button
                onClick={() => onEdit(practicePlan)}
                className="hockey-button-secondary text-sm"
              >
                <Edit className="w-4 h-4 mr-1" />
                Edit
              </button>
              <button
                onClick={() => onDelete(practicePlan)}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg text-sm transition-colors flex items-center"
              >
                <Trash2 className="w-4 h-4 mr-1" />
                Delete
              </button>
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-6 h-6" />
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
            <h3 className="text-lg font-russo text-hockey-blue mb-4">Practice Plan Drills</h3>
            {practicePlan.drills.length === 0 ? (
              <div className="text-center py-8 bg-gray-50 rounded-lg">
                <p className="text-gray-500">No drills added to this practice plan yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {practicePlan.drills.map((drill: any, index: number) => (
                  <div
                    key={drill.id}
                    className="bg-gray-50 rounded-lg p-4 border-l-4 border-hockey-blue"
                  >
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex items-center">
                        <span className="bg-hockey-blue text-white text-xs px-2 py-1 rounded-full mr-3">
                          {index + 1}
                        </span>
                        <h4 className="font-medium text-gray-900">{drill.name}</h4>
                      </div>
                      <div className="flex items-center text-sm text-gray-500">
                        <Clock className="w-4 h-4 mr-1" />
                        {drill.duration} min
                      </div>
                    </div>
                    
                    <div className="ml-8">
                      <p className="text-sm text-gray-600 mb-2">{drill.description}</p>
                      
                      {/* Drill Images */}
                      {drill.images && drill.images.length > 0 && (
                        <div className="mb-3">
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                            {drill.images.map((image: string, imgIndex: number) => (
                              <div key={imgIndex} className="aspect-video bg-gray-100 rounded-lg overflow-hidden">
                                <img
                                  src={image}
                                  alt={`${drill.name} - Image ${imgIndex + 1}`}
                                  className="w-full h-full object-cover hover:scale-105 transition-transform cursor-pointer"
                                  onClick={() => window.open(image, '_blank')}
                                />
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between">
                        <span className="text-xs bg-gray-200 text-gray-700 px-2 py-1 rounded">
                          {drill.category}
                        </span>
                        {drill.images && drill.images.length > 0 && (
                          <span className="text-xs text-hockey-blue">
                            📷 {drill.images.length} image{drill.images.length > 1 ? 's' : ''}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
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
