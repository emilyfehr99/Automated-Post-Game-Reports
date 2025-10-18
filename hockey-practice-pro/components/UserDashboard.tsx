'use client'

import { useState } from 'react'
import { useSession, signOut } from 'next-auth/react'
import { motion } from 'framer-motion'
import { User, Settings, LogOut, Crown, Calendar, Target } from 'lucide-react'

interface UserDashboardProps {
  onNavigate: (page: string) => void
}

export default function UserDashboard({ onNavigate }: UserDashboardProps) {
  const { data: session } = useSession()
  const [showMenu, setShowMenu] = useState(false)

  const handleSignOut = () => {
    signOut({ callbackUrl: '/auth/signin' })
  }

  const isPro = true // Everything is free now

  return (
    <div className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center cursor-pointer"
            onClick={() => onNavigate('home')}
          >
            <h1 className="text-2xl font-bold text-blue-600" style={{ fontFamily: 'Russo One' }}>
              Hockey Practice Pro
            </h1>
          </motion.div>

          {/* Navigation */}
          <nav className="hidden md:flex space-x-8">
            <button
              onClick={() => onNavigate('home')}
              className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
            >
              Dashboard
            </button>
            <button
              onClick={() => onNavigate('drills')}
              className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
            >
              Drills
            </button>
            <button
              onClick={() => onNavigate('plans')}
              className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
            >
              Practice Plans
            </button>
            <button
              onClick={() => onNavigate('drawing')}
              className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
            >
              Draw Drills
            </button>
          </nav>

          {/* User Menu */}
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="flex items-center space-x-3 text-gray-700 hover:text-blue-600"
            >
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-blue-600" />
                </div>
                <span className="hidden md:block text-sm font-medium">
                  {session?.user?.name || session?.user?.email}
                </span>
                <Crown className="w-4 h-4 text-green-500" title="Free Access" />
              </div>
            </button>

            {showMenu && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50"
              >
                <div className="px-4 py-2 border-b">
                  <p className="text-sm font-medium text-gray-900">
                    {session?.user?.name || 'User'}
                  </p>
                  <p className="text-xs text-gray-500">
                    {session?.user?.email}
                  </p>
                  <div className="flex items-center mt-1">
                    <Crown className="w-3 h-3 text-green-500 mr-1" />
                    <span className="text-xs text-green-600 font-medium">Free Access</span>
                  </div>
                </div>
                
                <button
                  onClick={() => onNavigate('settings')}
                  className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <Settings className="w-4 h-4 mr-3" />
                  Settings
                </button>
                
                <button
                  onClick={() => onNavigate('pricing')}
                  className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <Crown className="w-4 h-4 mr-3" />
                  View Features
                </button>
                
                <button
                  onClick={handleSignOut}
                  className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <LogOut className="w-4 h-4 mr-3" />
                  Sign Out
                </button>
              </motion.div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="bg-gray-50 border-t">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center">
                <Target className="w-8 h-8 text-blue-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Practice Plans</p>
                  <p className="text-2xl font-bold text-gray-900">12</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center">
                <Calendar className="w-8 h-8 text-green-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Custom Drills</p>
                  <p className="text-2xl font-bold text-gray-900">47</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center">
                <User className="w-8 h-8 text-purple-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Team Members</p>
                  <p className="text-2xl font-bold text-gray-900">{isPro ? '8' : '1'}</p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm">
              <div className="flex items-center">
                <Crown className="w-8 h-8 text-green-600 mr-3" />
                <div>
                  <p className="text-sm font-medium text-gray-600">Access</p>
                  <p className="text-2xl font-bold text-gray-900">Free</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
