'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Edit, 
  Save, 
  X, 
  Clock, 
  Tag, 
  FileText,
  Image as ImageIcon
} from 'lucide-react'

interface DrillPreviewModalProps {
  drill: any
  onSave: (drill: any) => void
  onClose: () => void
}

export default function DrillPreviewModal({ drill, onSave, onClose }: DrillPreviewModalProps) {
  const [editedDrill, setEditedDrill] = useState(drill)
  const [isEditing, setIsEditing] = useState(false)

  const categories = ['Skills', 'Systems', 'Offensive', 'Defensive', 'Power Play', 'Penalty Kill', 'Warm-up', 'Cool-down']

  const handleSave = () => {
    onSave(editedDrill)
    onClose()
  }

  const handleFieldChange = (field: string, value: any) => {
    setEditedDrill({
      ...editedDrill,
      [field]: value
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="bg-hockey-blue text-white p-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-russo">Drill Preview & Edit</h2>
            <div className="flex space-x-4">
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="bg-white text-hockey-blue px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors flex items-center"
              >
                <Edit className="w-4 h-4 mr-2" />
                {isEditing ? 'Preview' : 'Edit'}
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

        <div className="flex h-[600px]">
          {/* Drill Preview/Edit */}
          <div className="flex-1 p-6">
            <div className="space-y-6">
              {/* Drill Image/Canvas */}
              <div className="aspect-video bg-ice-blue rounded-lg flex items-center justify-center border-2 border-hockey-blue">
                {editedDrill.imageData ? (
                  <img 
                    src={editedDrill.imageData} 
                    alt={editedDrill.name}
                    className="max-w-full max-h-full object-contain rounded-lg"
                  />
                ) : editedDrill.elements && editedDrill.elements.length > 0 ? (
                  <div className="text-center">
                    <div className="w-16 h-16 bg-hockey-blue rounded-full flex items-center justify-center mx-auto mb-4">
                      <span className="text-white font-bold text-lg">D</span>
                    </div>
                    <p className="text-gray-600">Custom Drill with {editedDrill.elements.length} elements</p>
                  </div>
                ) : (
                  <div className="text-center">
                    <ImageIcon className="w-16 h-16 mx-auto mb-4 text-hockey-blue" />
                    <p className="text-gray-600">Drill Preview</p>
                  </div>
                )}
              </div>

              {/* Drill Information */}
              <div className="space-y-4">
                {/* Drill Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Drill Name
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editedDrill.name}
                      onChange={(e) => handleFieldChange('name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                    />
                  ) : (
                    <h3 className="text-xl font-russo text-hockey-blue">{editedDrill.name}</h3>
                  )}
                </div>

                {/* Category and Duration */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Category
                    </label>
                    {isEditing ? (
                      <select
                        value={editedDrill.category}
                        onChange={(e) => handleFieldChange('category', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                      >
                        {categories.map(cat => (
                          <option key={cat} value={cat}>{cat}</option>
                        ))}
                      </select>
                    ) : (
                      <div className="flex items-center">
                        <Tag className="w-4 h-4 mr-2 text-gray-500" />
                        <span className="bg-hockey-blue text-white px-3 py-1 rounded-full text-sm">
                          {editedDrill.category}
                        </span>
                      </div>
                    )}
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Duration
                    </label>
                    {isEditing ? (
                      <div className="flex items-center">
                        <input
                          type="number"
                          value={editedDrill.duration}
                          onChange={(e) => handleFieldChange('duration', parseInt(e.target.value) || 10)}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                          min="1"
                          max="60"
                        />
                        <span className="ml-2 text-gray-500">min</span>
                      </div>
                    ) : (
                      <div className="flex items-center">
                        <Clock className="w-4 h-4 mr-2 text-gray-500" />
                        <span className="text-gray-700">{editedDrill.duration} minutes</span>
                      </div>
                    )}
                  </div>
                </div>

                {/* Description */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Description
                  </label>
                  {isEditing ? (
                    <textarea
                      value={editedDrill.description}
                      onChange={(e) => handleFieldChange('description', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent h-24"
                      placeholder="Enter drill description..."
                    />
                  ) : (
                    <p className="text-gray-700">{editedDrill.description}</p>
                  )}
                </div>

                {/* Drill Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Drill Type
                  </label>
                  <div className="flex items-center">
                    <FileText className="w-4 h-4 mr-2 text-gray-500" />
                    <span className="text-sm text-gray-600">
                      {editedDrill.type === 'custom' ? 'Custom Created Drill' : 
                       editedDrill.type === 'pdf' ? 'Imported from PDF' : 'Sample Drill'}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Action Panel */}
          <div className="w-80 bg-gray-100 p-6 border-l">
            <div className="space-y-4">
              <h3 className="text-lg font-russo text-hockey-blue mb-4">Actions</h3>
              
              {/* Save Button */}
              <button
                onClick={handleSave}
                className="w-full flex items-center justify-center px-4 py-3 bg-hockey-blue text-white rounded-lg hover:bg-blue-800 transition-colors"
              >
                <Save className="w-4 h-4 mr-2" />
                Save to Drill Library
              </button>

              {/* Drill Stats */}
              <div className="bg-white rounded-lg p-4 space-y-3">
                <h4 className="font-medium text-gray-700">Drill Information</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Type:</span>
                    <span className="font-medium">
                      {editedDrill.type === 'custom' ? 'Custom' : 
                       editedDrill.type === 'pdf' ? 'PDF Import' : 'Sample'}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Category:</span>
                    <span className="font-medium">{editedDrill.category}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Duration:</span>
                    <span className="font-medium">{editedDrill.duration} min</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Created:</span>
                    <span className="font-medium">
                      {new Date(editedDrill.createdAt).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Instructions */}
              <div className="bg-ice-blue rounded-lg p-4">
                <h4 className="font-medium text-hockey-blue mb-2">Instructions</h4>
                <ul className="text-sm text-gray-700 space-y-1">
                  <li>• Review the drill details</li>
                  <li>• Edit any information as needed</li>
                  <li>• Click "Save to Drill Library" to add</li>
                  <li>• The drill will be available in your library</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
