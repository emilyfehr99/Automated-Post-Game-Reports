'use client'

import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Clock, 
  GripVertical,
  Eye
} from 'lucide-react'

interface Drill {
  id: string
  name: string
  description: string
  duration?: number
  category: string
  images?: string[]
  type?: string
  setup?: string[]
  variations?: string[]
  coachingPoints?: string[]
  createdAt?: string
}

interface DraggableDrillListProps {
  drills: Drill[]
  onReorder: (reorderedDrills: Drill[]) => void
  onViewDrill?: (drill: Drill) => void
  showImages?: boolean
  compact?: boolean
}

export default function DraggableDrillList({ 
  drills, 
  onReorder, 
  onViewDrill,
  showImages = true,
  compact = false
}: DraggableDrillListProps) {
  const [draggedIndex, setDraggedIndex] = useState<number | null>(null)
  const [dragOverIndex, setDragOverIndex] = useState<number | null>(null)

  const handleDragStart = (e: React.DragEvent<HTMLDivElement>, index: number) => {
    setDraggedIndex(index)
    e.dataTransfer.effectAllowed = 'move'
    e.dataTransfer.setData('text/html', '') // Required for some browsers
  }

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>, index: number) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'move'
    setDragOverIndex(index)
  }

  const handleDragLeave = () => {
    setDragOverIndex(null)
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>, dropIndex: number) => {
    e.preventDefault()
    
    if (draggedIndex === null || draggedIndex === dropIndex) {
      setDraggedIndex(null)
      setDragOverIndex(null)
      return
    }

    const newDrills = [...drills]
    const draggedDrill = newDrills[draggedIndex]
    
    // Remove the dragged drill
    newDrills.splice(draggedIndex, 1)
    
    // Insert at new position
    newDrills.splice(dropIndex, 0, draggedDrill)
    
    onReorder(newDrills)
    setDraggedIndex(null)
    setDragOverIndex(null)
  }

  const handleDragEnd = () => {
    setDraggedIndex(null)
    setDragOverIndex(null)
  }

  if (drills.length === 0) {
    return (
      <div className="text-center py-8 bg-gray-50 rounded-lg">
        <p className="text-gray-500">No drills added yet</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {drills.map((drill, index) => (
        <div
          key={drill.id}
          draggable
          onDragStart={(e: React.DragEvent<HTMLDivElement>) => handleDragStart(e, index)}
          onDragOver={(e: React.DragEvent<HTMLDivElement>) => handleDragOver(e, index)}
          onDragLeave={handleDragLeave}
          onDrop={(e: React.DragEvent<HTMLDivElement>) => handleDrop(e, index)}
          onDragEnd={handleDragEnd}
          className={`
            bg-gray-50 rounded-lg border-l-4 border-hockey-blue cursor-move
            transition-all duration-200 hover:shadow-md hover:scale-102
            ${draggedIndex === index ? 'opacity-50 scale-95' : ''}
            ${dragOverIndex === index && draggedIndex !== index ? 'border-hockey-blue border-l-8 bg-hockey-blue bg-opacity-10' : ''}
            ${compact ? 'p-3' : 'p-4'}
          `}
        >
          <div className="flex items-start gap-3">
            {/* Drag Handle */}
            <div className="flex-shrink-0 mt-1">
              <GripVertical className="w-5 h-5 text-gray-400 hover:text-gray-600" />
            </div>
            
            {/* Drill Number */}
            <div className="flex-shrink-0">
              <span className="bg-hockey-blue text-white text-xs px-2 py-1 rounded-full">
                {index + 1}
              </span>
            </div>
            
            {/* Drill Content */}
            <div className="flex-1 min-w-0">
              <div className="flex justify-between items-start mb-2">
                <h4 className="font-medium text-gray-900 truncate">{drill.name}</h4>
                <div className="flex items-center gap-2 ml-2">
                  {drill.duration && (
                    <div className="flex items-center text-sm text-gray-500">
                      <Clock className="w-4 h-4 mr-1" />
                      {drill.duration} min
                    </div>
                  )}
                  {onViewDrill && (
                    <button
                      onClick={() => onViewDrill(drill)}
                      className="text-hockey-blue hover:text-hockey-blue-dark p-1"
                      title="View drill details"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
              
              {!compact && (
                <div className="ml-0">
                  <p className="text-sm text-gray-600 mb-2 line-clamp-2">{drill.description}</p>
                  
                  {/* Drill Images */}
                  {showImages && drill.images && drill.images.length > 0 && (
                    <div className="mb-3">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                        {drill.images.slice(0, 2).map((image: string, imgIndex: number) => (
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
                      {drill.images.length > 2 && (
                        <p className="text-xs text-gray-500 mt-1">
                          +{drill.images.length - 2} more images
                        </p>
                      )}
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
              )}
            </div>
          </div>
        </div>
      ))}
      
      {/* Drop zone at the end */}
      <div
        onDragOver={(e: React.DragEvent<HTMLDivElement>) => handleDragOver(e, drills.length)}
        onDragLeave={handleDragLeave}
        onDrop={(e: React.DragEvent<HTMLDivElement>) => handleDrop(e, drills.length)}
        className={`
          h-8 rounded-lg border-2 border-dashed border-gray-300
          ${dragOverIndex === drills.length ? 'border-hockey-blue bg-hockey-blue bg-opacity-10' : ''}
          ${drills.length === 0 ? 'hidden' : ''}
        `}
      />
    </div>
  )
}
