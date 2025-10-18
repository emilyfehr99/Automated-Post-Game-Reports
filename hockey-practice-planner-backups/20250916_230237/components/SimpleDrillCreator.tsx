'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Upload, 
  Save, 
  X, 
  Image as ImageIcon,
  FileText,
  Clock,
  Tag,
  Trash2
} from 'lucide-react'

interface SimpleDrillCreatorProps {
  onSave: (drillData: any) => void
  onClose: () => void
}

export default function SimpleDrillCreator({ onSave, onClose }: SimpleDrillCreatorProps) {
  const [drillName, setDrillName] = useState('')
  const [drillDescription, setDrillDescription] = useState('')
  const [drillCategory, setDrillCategory] = useState('Skills')
  const [drillDuration, setDrillDuration] = useState(10)
  const [uploadedImages, setUploadedImages] = useState<string[]>([])
  const [setupSteps, setSetupSteps] = useState<string[]>([''])
  const [variations, setVariations] = useState<string[]>([''])
  const [coachingPoints, setCoachingPoints] = useState<string[]>([''])

  const categories = ['Skills', 'Systems', 'Offensive', 'Defensive', 'Power Play', 'Penalty Kill', 'Warm-up', 'Cool-down']

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || [])
    
    files.forEach(file => {
      if (file.type.startsWith('image/')) {
        const reader = new FileReader()
        reader.onload = (e) => {
          const imageData = e.target?.result as string
          setUploadedImages(prev => [...prev, imageData])
        }
        reader.readAsDataURL(file)
      }
    })
  }

  const handlePaste = async (e: React.ClipboardEvent) => {
    const items = e.clipboardData.items
    
    for (let i = 0; i < items.length; i++) {
      const item = items[i]
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile()
        if (file) {
          const reader = new FileReader()
          reader.onload = (e) => {
            const imageData = e.target?.result as string
            setUploadedImages(prev => [...prev, imageData])
          }
          reader.readAsDataURL(file)
        }
      }
    }
  }

  const removeImage = (index: number) => {
    setUploadedImages(prev => prev.filter((_, i) => i !== index))
  }

  const addStep = (type: 'setup' | 'variations' | 'coaching') => {
    if (type === 'setup') {
      setSetupSteps(prev => [...prev, ''])
    } else if (type === 'variations') {
      setVariations(prev => [...prev, ''])
    } else {
      setCoachingPoints(prev => [...prev, ''])
    }
  }

  const updateStep = (type: 'setup' | 'variations' | 'coaching', index: number, value: string) => {
    if (type === 'setup') {
      setSetupSteps(prev => prev.map((step, i) => i === index ? value : step))
    } else if (type === 'variations') {
      setVariations(prev => prev.map((step, i) => i === index ? value : step))
    } else {
      setCoachingPoints(prev => prev.map((step, i) => i === index ? value : step))
    }
  }

  const removeStep = (type: 'setup' | 'variations' | 'coaching', index: number) => {
    if (type === 'setup') {
      setSetupSteps(prev => prev.filter((_, i) => i !== index))
    } else if (type === 'variations') {
      setVariations(prev => prev.filter((_, i) => i !== index))
    } else {
      setCoachingPoints(prev => prev.filter((_, i) => i !== index))
    }
  }

  const compressImage = (base64: string): string => {
    try {
      // If image is already small enough, return as is
      if (base64.length < 50000) {
        return base64
      }

      // Create a canvas to compress the image
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      const img = new Image()
      
      return new Promise((resolve) => {
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
          const compressed = canvas.toDataURL('image/jpeg', 0.6) // 60% quality
          resolve(compressed)
        }
        img.onerror = () => {
          resolve(base64)
        }
        img.src = base64
      }) as string
    } catch (error) {
      console.error('Failed to compress image:', error)
      return base64
    }
  }

  const generateDrillPlan = async () => {
    if (!drillName.trim()) return

    // Compress images before saving
    const compressedImages = await Promise.all(
      uploadedImages.map(img => compressImage(img))
    )

    const drillData = {
      id: Date.now().toString(),
      name: drillName,
      description: drillDescription,
      category: drillCategory,
      duration: drillDuration,
      type: 'custom',
      images: compressedImages,
      setup: setupSteps.filter(step => step.trim()),
      variations: variations.filter(step => step.trim()),
      coachingPoints: coachingPoints.filter(step => step.trim()),
      createdAt: new Date().toISOString()
    }

    console.log('Saving drill with compressed images:', drillData.images.length)
    onSave(drillData)
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
            <h2 className="text-2xl font-russo">Simple Drill Creator</h2>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-300 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div 
          className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]"
          onPaste={handlePaste}
          tabIndex={0}
        >
          <div className="space-y-6">
            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Drill Name *
                </label>
                <input
                  type="text"
                  value={drillName}
                  onChange={(e) => setDrillName(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                  placeholder="Enter drill name..."
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category
                </label>
                <select
                  value={drillCategory}
                  onChange={(e) => setDrillCategory(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                >
                  {categories.map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Duration (minutes)
                </label>
                <input
                  type="number"
                  value={drillDuration}
                  onChange={(e) => setDrillDuration(parseInt(e.target.value) || 10)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                  min="1"
                  max="60"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description
                </label>
                <input
                  type="text"
                  value={drillDescription}
                  onChange={(e) => setDrillDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                  placeholder="Brief drill description..."
                />
              </div>
            </div>

            {/* Image Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Drill Images
              </label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <input
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleImageUpload}
                  className="hidden"
                  id="image-upload"
                />
                <label
                  htmlFor="image-upload"
                  className="cursor-pointer flex flex-col items-center"
                >
                  <Upload className="w-8 h-8 text-gray-400 mb-2" />
                  <p className="text-gray-600">Click to upload drill images</p>
                  <p className="text-sm text-gray-500">PNG, JPG, GIF supported</p>
                  <p className="text-sm text-hockey-blue font-medium mt-2">Or paste from clipboard (Ctrl+V)</p>
                </label>
              </div>

              {/* Display uploaded images */}
              {uploadedImages.length > 0 && (
                <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-4">
                  {uploadedImages.map((image, index) => (
                    <div key={index} className="relative">
                      <img
                        src={image}
                        alt={`Drill image ${index + 1}`}
                        className="w-full h-32 object-cover rounded-lg border"
                      />
                      <button
                        onClick={() => removeImage(index)}
                        className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Setup Steps */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-gray-700">
                  Setup Instructions
                </label>
                <button
                  onClick={() => addStep('setup')}
                  className="text-hockey-blue hover:text-blue-800 text-sm flex items-center"
                >
                  <FileText className="w-4 h-4 mr-1" />
                  Add Step
                </button>
              </div>
              <div className="space-y-2">
                {setupSteps.map((step, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500 w-6">{index + 1}.</span>
                    <input
                      type="text"
                      value={step}
                      onChange={(e) => updateStep('setup', index, e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                      placeholder="Enter setup step..."
                    />
                    <button
                      onClick={() => removeStep('setup', index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Variations */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-gray-700">
                  Variations
                </label>
                <button
                  onClick={() => addStep('variations')}
                  className="text-hockey-blue hover:text-blue-800 text-sm flex items-center"
                >
                  <FileText className="w-4 h-4 mr-1" />
                  Add Variation
                </button>
              </div>
              <div className="space-y-2">
                {variations.map((step, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500 w-6">•</span>
                    <input
                      type="text"
                      value={step}
                      onChange={(e) => updateStep('variations', index, e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                      placeholder="Enter variation..."
                    />
                    <button
                      onClick={() => removeStep('variations', index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Coaching Points */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <label className="block text-sm font-medium text-gray-700">
                  Coaching Points
                </label>
                <button
                  onClick={() => addStep('coaching')}
                  className="text-hockey-blue hover:text-blue-800 text-sm flex items-center"
                >
                  <FileText className="w-4 h-4 mr-1" />
                  Add Point
                </button>
              </div>
              <div className="space-y-2">
                {coachingPoints.map((step, index) => (
                  <div key={index} className="flex items-center space-x-2">
                    <span className="text-sm text-gray-500 w-6">•</span>
                    <input
                      type="text"
                      value={step}
                      onChange={(e) => updateStep('coaching', index, e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                      placeholder="Enter coaching point..."
                    />
                    <button
                      onClick={() => removeStep('coaching', index)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-end space-x-4 pt-6 border-t">
              <button
                onClick={onClose}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={generateDrillPlan}
                className="px-6 py-2 bg-hockey-blue text-white rounded-lg hover:bg-blue-800 transition-colors flex items-center"
              >
                <Save className="w-4 h-4 mr-2" />
                Create Drill Plan
              </button>
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}
