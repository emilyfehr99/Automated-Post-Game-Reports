'use client'

import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { X, QrCode, Camera, Download, Upload } from 'lucide-react'
import QRCode from 'qrcode'

interface QRCodeSyncProps {
  onClose: () => void
  onImport: (data: any) => void
}

export default function QRCodeSync({ onClose, onImport }: QRCodeSyncProps) {
  const [mode, setMode] = useState<'generate' | 'scan'>('generate')
  const [qrCodeUrl, setQrCodeUrl] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const generateQRCode = async () => {
    setIsGenerating(true)
    try {
      // Get all data from localStorage
      const data = {
        drills: JSON.parse(localStorage.getItem('hockey-drills') || '[]'),
        practicePlans: JSON.parse(localStorage.getItem('hockey-practice-plans') || '[]'),
        settings: JSON.parse(localStorage.getItem('hockey-settings') || '{}'),
        customCategories: JSON.parse(localStorage.getItem('hockey-custom-categories') || '[]'),
        exportDate: new Date().toISOString()
      }

      // Compress data for QR code (QR codes have size limits)
      const compressedData = JSON.stringify(data)
      
      // Check if data is too large for QR code (QR codes max ~2953 chars)
      if (compressedData.length > 2500) {
        alert('⚠️ Your data is too large for QR code sync. Please use the file export/import method instead.')
        setIsGenerating(false)
        return
      }

      // Generate QR code
      const url = await QRCode.toDataURL(compressedData, {
        width: 300,
        margin: 2,
        color: {
          dark: '#1e40af', // Hockey blue
          light: '#ffffff'
        }
      })
      
      setQrCodeUrl(url)
    } catch (error) {
      console.error('Error generating QR code:', error)
      alert('❌ Error generating QR code. Please try the file export method instead.')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target?.result as string)
          onImport(data)
          onClose()
        } catch (error) {
          alert('❌ Error reading file. Please check the file format.')
        }
      }
      reader.readAsText(file)
    }
  }

  const downloadQRCode = () => {
    if (qrCodeUrl) {
      const link = document.createElement('a')
      link.download = `hockey-sync-qr-${new Date().toISOString().split('T')[0]}.png`
      link.href = qrCodeUrl
      link.click()
    }
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
        className="bg-white rounded-xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="bg-hockey-blue text-white p-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-russo">📱 Mobile Sync</h2>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-300 transition-colors"
            >
              <X className="w-6 h-6" />
            </button>
          </div>
        </div>

        <div className="p-6">
          {/* Mode Selection */}
          <div className="flex space-x-2 mb-6">
            <button
              onClick={() => setMode('generate')}
              className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                mode === 'generate'
                  ? 'bg-hockey-blue text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <QrCode className="w-4 h-4 inline mr-2" />
              Generate QR Code
            </button>
            <button
              onClick={() => setMode('scan')}
              className={`flex-1 py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                mode === 'scan'
                  ? 'bg-hockey-blue text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Camera className="w-4 h-4 inline mr-2" />
              Import Data
            </button>
          </div>

          {/* Generate QR Code Mode */}
          {mode === 'generate' && (
            <div className="space-y-4">
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-4">
                  Generate a QR code with your data to scan with your phone
                </p>
                
                <button
                  onClick={generateQRCode}
                  disabled={isGenerating}
                  className="hockey-button mb-4"
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Generating...
                    </>
                  ) : (
                    <>
                      <QrCode className="w-4 h-4 mr-2" />
                      Generate QR Code
                    </>
                  )}
                </button>
              </div>

              {qrCodeUrl && (
                <div className="text-center">
                  <div className="bg-white p-4 rounded-lg border-2 border-gray-200 inline-block">
                    <img src={qrCodeUrl} alt="QR Code for data sync" className="w-48 h-48" />
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Scan this QR code with your phone to import data
                  </p>
                  <button
                    onClick={downloadQRCode}
                    className="mt-2 text-hockey-blue hover:text-blue-800 text-sm flex items-center mx-auto"
                  >
                    <Download className="w-4 h-4 mr-1" />
                    Download QR Code
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Import Data Mode */}
          {mode === 'scan' && (
            <div className="space-y-4">
              <div className="text-center">
                <p className="text-sm text-gray-600 mb-4">
                  Import data from a file exported from your computer
                </p>
                
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="hockey-button"
                >
                  <Upload className="w-4 h-4 mr-2" />
                  Choose File to Import
                </button>
                
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".json"
                  onChange={handleFileUpload}
                  className="hidden"
                />
              </div>

              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">📱 How to sync with your phone:</h4>
                <ol className="text-sm text-blue-800 list-decimal list-inside space-y-1">
                  <li>Generate QR code on your computer</li>
                  <li>Open camera app on your phone</li>
                  <li>Point camera at QR code</li>
                  <li>Tap the notification to open in browser</li>
                  <li>Your data will be imported automatically!</li>
                </ol>
              </div>

              <div className="bg-yellow-50 border-l-4 border-yellow-500 p-3 mt-4">
                <p className="text-sm text-yellow-800">
                  <strong>⚠️ Note:</strong> This is a one-time sync. Changes made after this won't automatically sync between devices.
                </p>
              </div>
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  )
}
