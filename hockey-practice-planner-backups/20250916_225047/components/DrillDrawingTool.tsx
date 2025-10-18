'use client'

import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { 
  Circle, 
  Square, 
  Triangle, 
  ArrowRight, 
  ArrowLeft, 
  ArrowUp, 
  ArrowDown,
  RotateCcw,
  Save,
  Download,
  X,
  Upload,
  FileText
} from 'lucide-react'
import { pdfProcessor } from '@/utils/pdfProcessor'

interface DrillDrawingToolProps {
  onSave: (drillData: any) => void
  onClose: () => void
  onPreview: (drillData: any) => void
}

interface DrillElement {
  id: string
  type: 'player' | 'puck' | 'arrow' | 'cone' | 'line' | 'coach' | 'text'
  x: number
  y: number
  x2?: number
  y2?: number
  color?: string
  direction?: string
  text?: string
  size?: number
}

export default function DrillDrawingTool({ onSave, onClose, onPreview }: DrillDrawingToolProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [selectedTool, setSelectedTool] = useState('select')
  const [drillName, setDrillName] = useState('')
  const [drillDescription, setDrillDescription] = useState('')
  const [drillCategory, setDrillCategory] = useState('Skills')
  const [drillDuration, setDrillDuration] = useState(10)
  const [elements, setElements] = useState<DrillElement[]>([])
  const [isDrawing, setIsDrawing] = useState(false)
  const [showPdfUpload, setShowPdfUpload] = useState(false)
  const [startPoint, setStartPoint] = useState<{x: number, y: number} | null>(null)
  const [selectedColor, setSelectedColor] = useState('#003366')

  const categories = ['Skills', 'Systems', 'Offensive', 'Defensive', 'Power Play', 'Penalty Kill', 'Warm-up', 'Cool-down']

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    canvas.width = 800
    canvas.height = 400

    // Draw hockey rink
    drawHockeyRink(ctx)
  }, [])

  const drawHockeyRink = (ctx: CanvasRenderingContext2D) => {
    // Clear canvas
    ctx.clearRect(0, 0, 800, 400)
    
    // Set background
    ctx.fillStyle = '#E6F3FF'
    ctx.fillRect(0, 0, 800, 400)

    // Rink outline
    ctx.strokeStyle = '#003366'
    ctx.lineWidth = 3
    ctx.strokeRect(50, 50, 700, 300)

    // Center line
    ctx.beginPath()
    ctx.moveTo(400, 50)
    ctx.lineTo(400, 350)
    ctx.stroke()

    // Center circle
    ctx.beginPath()
    ctx.arc(400, 200, 30, 0, 2 * Math.PI)
    ctx.stroke()

    // Goal lines
    ctx.beginPath()
    ctx.moveTo(50, 200)
    ctx.lineTo(150, 200)
    ctx.stroke()

    ctx.beginPath()
    ctx.moveTo(650, 200)
    ctx.lineTo(750, 200)
    ctx.stroke()

    // Goals
    ctx.fillStyle = '#CC0000'
    ctx.fillRect(30, 180, 20, 40)
    ctx.fillRect(750, 180, 20, 40)

    // Face-off circles
    ctx.beginPath()
    ctx.arc(200, 150, 25, 0, 2 * Math.PI)
    ctx.stroke()

    ctx.beginPath()
    ctx.arc(600, 150, 25, 0, 2 * Math.PI)
    ctx.stroke()

    ctx.beginPath()
    ctx.arc(200, 250, 25, 0, 2 * Math.PI)
    ctx.stroke()

    ctx.beginPath()
    ctx.arc(600, 250, 25, 0, 2 * Math.PI)
    ctx.stroke()

    // Blue lines
    ctx.beginPath()
    ctx.moveTo(200, 50)
    ctx.lineTo(200, 350)
    ctx.stroke()

    ctx.beginPath()
    ctx.moveTo(600, 50)
    ctx.lineTo(600, 350)
    ctx.stroke()

    // Goal crease
    ctx.beginPath()
    ctx.arc(50, 200, 20, -Math.PI/2, Math.PI/2)
    ctx.stroke()

    ctx.beginPath()
    ctx.arc(750, 200, 20, Math.PI/2, -Math.PI/2)
    ctx.stroke()

    // IHS Logo placeholder
    ctx.fillStyle = '#003366'
    ctx.font = 'bold 16px Arial'
    ctx.textAlign = 'center'
    ctx.fillText('IHS', 400, 210)
  }

  const redrawCanvas = () => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Redraw rink
    drawHockeyRink(ctx)

    // Draw elements
    elements.forEach(element => {
      drawElement(ctx, element)
    })
  }

  const drawElement = (ctx: CanvasRenderingContext2D, element: DrillElement) => {
    ctx.save()
    
    switch (element.type) {
      case 'player':
        ctx.fillStyle = element.color || '#003366'
        ctx.beginPath()
        ctx.arc(element.x, element.y, 10, 0, 2 * Math.PI)
        ctx.fill()
        ctx.strokeStyle = '#FFFFFF'
        ctx.lineWidth = 2
        ctx.stroke()
        break
        
      case 'puck':
        ctx.fillStyle = '#000000'
        ctx.beginPath()
        ctx.arc(element.x, element.y, 5, 0, 2 * Math.PI)
        ctx.fill()
        break
        
      case 'cone':
        ctx.fillStyle = element.color || '#FFD700'
        ctx.beginPath()
        ctx.moveTo(element.x, element.y - 8)
        ctx.lineTo(element.x - 6, element.y + 8)
        ctx.lineTo(element.x + 6, element.y + 8)
        ctx.closePath()
        ctx.fill()
        ctx.strokeStyle = '#000000'
        ctx.lineWidth = 1
        ctx.stroke()
        break
        
      case 'line':
        ctx.strokeStyle = element.color || '#FFD700'
        ctx.lineWidth = 3
        ctx.beginPath()
        ctx.moveTo(element.x, element.y)
        ctx.lineTo(element.x2 || element.x, element.y2 || element.y)
        ctx.stroke()
        break
        
      case 'coach':
        ctx.fillStyle = '#FF6B6B'
        ctx.beginPath()
        ctx.arc(element.x, element.y, 8, 0, 2 * Math.PI)
        ctx.fill()
        ctx.strokeStyle = '#FFFFFF'
        ctx.lineWidth = 2
        ctx.stroke()
        // Add "Co" text
        ctx.fillStyle = '#FFFFFF'
        ctx.font = 'bold 10px Arial'
        ctx.textAlign = 'center'
        ctx.fillText('Co', element.x, element.y + 3)
        break
        
      case 'text':
        ctx.fillStyle = element.color || '#000000'
        ctx.font = `${element.size || 12}px Arial`
        ctx.textAlign = 'center'
        ctx.fillText(element.text || '', element.x, element.y)
        break
        
      case 'arrow':
        ctx.strokeStyle = element.color || '#FFD700'
        ctx.lineWidth = 3
        ctx.beginPath()
        
        const length = 30
        let endX = element.x
        let endY = element.y
        
        switch (element.direction) {
          case 'right':
            endX = element.x + length
            break
          case 'left':
            endX = element.x - length
            break
          case 'up':
            endY = element.y - length
            break
          case 'down':
            endY = element.y + length
            break
        }
        
        ctx.moveTo(element.x, element.y)
        ctx.lineTo(endX, endY)
        ctx.stroke()
        
        // Draw arrowhead
        const headLength = 10
        const angle = Math.atan2(endY - element.y, endX - element.x)
        
        ctx.beginPath()
        ctx.moveTo(endX, endY)
        ctx.lineTo(
          endX - headLength * Math.cos(angle - Math.PI / 6),
          endY - headLength * Math.sin(angle - Math.PI / 6)
        )
        ctx.moveTo(endX, endY)
        ctx.lineTo(
          endX - headLength * Math.cos(angle + Math.PI / 6),
          endY - headLength * Math.sin(angle + Math.PI / 6)
        )
        ctx.stroke()
        break
    }
    
    ctx.restore()
  }

  const handleCanvasClick = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (selectedTool === 'select') return

    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    if (selectedTool === 'line') {
      if (!startPoint) {
        setStartPoint({ x, y })
        return
      } else {
        const newElement: DrillElement = {
          id: Date.now().toString(),
          type: 'line',
          x: startPoint.x,
          y: startPoint.y,
          x2: x,
          y2: y,
          color: selectedColor
        }
        setElements([...elements, newElement])
        setStartPoint(null)
        return
      }
    }

    if (selectedTool === 'text') {
      const text = prompt('Enter text:')
      if (text) {
        const newElement: DrillElement = {
          id: Date.now().toString(),
          type: 'text',
          x,
          y,
          text,
          color: selectedColor,
          size: 14
        }
        setElements([...elements, newElement])
      }
      return
    }

    const newElement: DrillElement = {
      id: Date.now().toString(),
      type: selectedTool as any,
      x,
      y,
      color: selectedColor,
      direction: selectedTool === 'arrow' ? 'right' : undefined
    }

    setElements([...elements, newElement])
  }

  const clearCanvas = () => {
    setElements([])
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    drawHockeyRink(ctx)
  }

  const saveDrill = () => {
    if (!drillName.trim()) return

    const drillData = {
      id: Date.now().toString(),
      name: drillName,
      description: drillDescription,
      category: drillCategory,
      duration: drillDuration,
      elements: elements,
      type: 'custom',
      createdAt: new Date().toISOString()
    }

    onPreview(drillData)
  }

  const handlePdfUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    try {
      // Process the PDF to extract drill images
      const drillImages = await pdfProcessor.processPDF(file)
      
      // Convert the first image to a drill
      if (drillImages.length > 0) {
        const drillData = await pdfProcessor.convertImageToDrill(
          drillImages[0].imageData,
          drillImages[0].name,
          drillImages[0].description
        )
        
        drillData.category = drillCategory
        drillData.duration = drillDuration
        
        onPreview(drillData)
        setShowPdfUpload(false)
      }
    } catch (error) {
      console.error('Error processing PDF:', error)
      alert('Error processing PDF file. Please try again.')
    }
  }

  const tools = [
    { id: 'select', label: 'Select', icon: null },
    { id: 'player', label: 'Player', icon: Circle },
    { id: 'puck', label: 'Puck', icon: Circle },
    { id: 'cone', label: 'Cone', icon: Triangle },
    { id: 'coach', label: 'Coach', icon: Circle },
    { id: 'line', label: 'Line', icon: null },
    { id: 'arrow', label: 'Arrow', icon: ArrowRight },
    { id: 'text', label: 'Text', icon: FileText },
  ]

  // Redraw when elements change
  useEffect(() => {
    redrawCanvas()
  }, [elements])

  // Draw temporary line when drawing
  useEffect(() => {
    if (selectedTool === 'line' && startPoint) {
      const canvas = canvasRef.current
      if (!canvas) return

      const ctx = canvas.getContext('2d')
      if (!ctx) return

      const handleMouseMove = (e: MouseEvent) => {
        const rect = canvas.getBoundingClientRect()
        const x = e.clientX - rect.left
        const y = e.clientY - rect.top

        redrawCanvas()
        
        // Draw temporary line
        ctx.save()
        ctx.strokeStyle = selectedColor
        ctx.lineWidth = 3
        ctx.setLineDash([5, 5])
        ctx.beginPath()
        ctx.moveTo(startPoint.x, startPoint.y)
        ctx.lineTo(x, y)
        ctx.stroke()
        ctx.restore()
      }

      canvas.addEventListener('mousemove', handleMouseMove)
      return () => canvas.removeEventListener('mousemove', handleMouseMove)
    }
  }, [selectedTool, startPoint, selectedColor])

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white rounded-xl shadow-2xl max-w-6xl w-full mx-4 max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="bg-hockey-blue text-white p-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-russo">Drill Creation Tool</h2>
            <div className="flex space-x-4">
              <button
                onClick={() => setShowPdfUpload(true)}
                className="bg-white text-hockey-blue px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors flex items-center"
              >
                <Upload className="w-4 h-4 mr-2" />
                Upload PDF
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
          {/* Toolbar */}
          <div className="w-64 bg-gray-100 p-4 border-r overflow-y-auto">
            <div className="space-y-4">
              {/* Drill Info */}
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
                <textarea
                  value={drillDescription}
                  onChange={(e) => setDrillDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent h-20"
                  placeholder="Enter drill description..."
                />
              </div>

              {/* Color Selection */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Color</h3>
                <div className="grid grid-cols-4 gap-2">
                  {[
                    { color: '#003366', name: 'Blue' },
                    { color: '#CC0000', name: 'Red' },
                    { color: '#FFD700', name: 'Gold' },
                    { color: '#000000', name: 'Black' },
                    { color: '#FFFFFF', name: 'White' },
                    { color: '#00FF00', name: 'Green' },
                    { color: '#FF6B6B', name: 'Pink' },
                    { color: '#8B4513', name: 'Brown' }
                  ].map((colorOption) => (
                    <button
                      key={colorOption.color}
                      onClick={() => setSelectedColor(colorOption.color)}
                      className={`w-8 h-8 rounded border-2 ${
                        selectedColor === colorOption.color ? 'border-gray-800' : 'border-gray-300'
                      }`}
                      style={{ backgroundColor: colorOption.color }}
                      title={colorOption.name}
                    />
                  ))}
                </div>
              </div>

              {/* Tools */}
              <div>
                <h3 className="text-sm font-medium text-gray-700 mb-3">Drawing Tools</h3>
                <div className="space-y-2">
                  {tools.map((tool) => {
                    const Icon = tool.icon
                    return (
                      <button
                        key={tool.id}
                        onClick={() => {
                          setSelectedTool(tool.id)
                          if (tool.id === 'line') setStartPoint(null)
                        }}
                        className={`w-full flex items-center px-3 py-2 rounded-lg transition-colors ${
                          selectedTool === tool.id
                            ? 'bg-hockey-blue text-white'
                            : 'bg-white text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {Icon && <Icon className="w-4 h-4 mr-2" />}
                        {tool.label}
                        {tool.id === 'line' && startPoint && (
                          <span className="ml-auto text-xs">(Click to end)</span>
                        )}
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Actions */}
              <div className="space-y-2">
                <button
                  onClick={clearCanvas}
                  className="w-full flex items-center justify-center px-3 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                >
                  <RotateCcw className="w-4 h-4 mr-2" />
                  Clear Canvas
                </button>
                <button
                  onClick={saveDrill}
                  className="w-full flex items-center justify-center px-3 py-2 bg-hockey-blue text-white rounded-lg hover:bg-blue-800 transition-colors"
                >
                  <Save className="w-4 h-4 mr-2" />
                  Preview & Save Drill
                </button>
              </div>
            </div>
          </div>

          {/* Canvas Area */}
          <div className="flex-1 p-4">
            <div className="h-full flex items-center justify-center">
              <canvas
                ref={canvasRef}
                onClick={handleCanvasClick}
                className="rink-canvas cursor-crosshair border-2 border-hockey-blue rounded-lg"
                style={{ width: '800px', height: '400px' }}
              />
            </div>
            <div className="mt-4 text-center text-sm text-gray-600">
              {selectedTool === 'select' ? 'Select tool - click elements to move them' :
               selectedTool === 'line' ? 'Line tool - click start point, then end point' :
               selectedTool === 'text' ? 'Text tool - click to add text' :
               `Click on the rink to add ${selectedTool}s`}
            </div>
          </div>
        </div>

        {/* PDF Upload Modal */}
        {showPdfUpload && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-60">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-russo text-hockey-blue mb-4">Upload Drill PDF</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select PDF File
                  </label>
                  <input
                    type="file"
                    accept=".pdf"
                    onChange={handlePdfUpload}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                  />
                </div>
                <div className="flex space-x-4">
                  <button
                    onClick={() => setShowPdfUpload(false)}
                    className="flex-1 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </motion.div>
    </motion.div>
  )
}