'use client'

import { motion } from 'framer-motion'
import { useRouter } from 'next/navigation'
import { 
  Play, 
  Users, 
  Calendar, 
  Target, 
  Crown, 
  Check,
  ArrowRight,
  Star
} from 'lucide-react'

export default function Home() {
  const router = useRouter()

  const features = [
    {
      icon: Target,
      title: 'Interactive Drill Drawing',
      description: 'Create custom drills with our intuitive hockey rink canvas tool'
    },
    {
      icon: Calendar,
      title: 'Practice Plan Builder',
      description: 'Structure complete practice sessions with timing and organization'
    },
    {
      icon: Users,
      title: 'Team Collaboration',
      description: 'Share drills and plans with your coaching staff and players'
    },
    {
      icon: Play,
      title: 'Drill Library',
      description: 'Access hundreds of professional drills or create your own'
    }
  ]

  const freeFeatures = [
    'Unlimited practice plans',
    'Unlimited custom drills',
    'Interactive drill drawing tool',
    'Complete drill library access',
    'Team collaboration features',
    'PDF export functionality',
    'Mobile responsive design',
    'Video drill integration',
    'Advanced analytics',
    'Custom branding options',
    'API access',
    'Priority support'
  ]

    return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-blue-600" style={{ fontFamily: 'Russo One' }}>
                Hockey Practice Pro
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <button 
                onClick={() => router.push('/auth/signin')}
                className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium"
              >
                Sign In
              </button>
                <button
                onClick={() => router.push('/auth/signup')}
                className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-blue-700"
              >
                Get Started
                </button>
          </div>
        </div>
    </div>
      </header>

      {/* Hero Section */}
      <section className="bg-gradient-to-br from-blue-900 to-blue-700 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
              className="text-4xl md:text-6xl font-bold mb-6"
              style={{ fontFamily: 'Russo One' }}
            >
              Professional Hockey Practice Planning
            </motion.h1>
            <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
              className="text-xl md:text-2xl mb-8 text-blue-100"
            >
              Create, manage, and share practice plans with advanced drill drawing tools
            </motion.p>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
              className="flex flex-col sm:flex-row gap-4 justify-center"
            >
          <button 
                onClick={() => router.push('/auth/signup')}
                className="bg-white text-blue-600 px-8 py-3 rounded-lg text-lg font-medium hover:bg-gray-100 transition-colors flex items-center justify-center"
          >
                Start Free Trial
                <ArrowRight className="w-5 h-5 ml-2" />
          </button>
              <button 
                onClick={() => router.push('/pricing')}
                className="border-2 border-white text-white px-8 py-3 rounded-lg text-lg font-medium hover:bg-white hover:text-blue-600 transition-colors"
              >
                View Pricing
              </button>
          </motion.div>
      </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4" style={{ fontFamily: 'Russo One' }}>
              Everything You Need to Plan Perfect Practices
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Professional-grade tools designed specifically for hockey coaches at all levels
            </p>
      </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const Icon = feature.icon
              return (
            <motion.div
                  key={index}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
                  className="bg-white p-6 rounded-lg shadow-lg text-center"
                >
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Icon className="w-8 h-8 text-blue-600" />
                </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2" style={{ fontFamily: 'Russo One' }}>
                    {feature.title}
                  </h3>
                  <p className="text-gray-600">{feature.description}</p>
            </motion.div>
              )
            })}
        </div>
        </div>
      </section>

      {/* Tool Preview Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4" style={{ fontFamily: 'Russo One' }}>
              See It In Action
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Get a glimpse of the powerful tools that will transform your practice planning
            </p>
    </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Drill Drawing Tool Preview */}
        <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-6"
            >
              <div className="bg-gray-100 rounded-lg p-8 text-center">
                <div className="w-full h-64 bg-white rounded-lg shadow-lg flex items-center justify-center mb-4">
          <div className="text-center">
                    <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Target className="w-10 h-10 text-blue-600" />
            </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2" style={{ fontFamily: 'Russo One' }}>
                      Interactive Drill Drawing Tool
                    </h3>
                    <p className="text-gray-600 text-sm">
                      Draw custom drills on a hockey rink canvas with players, pucks, and movement arrows
                    </p>
          </div>
            </div>
                <div className="grid grid-cols-3 gap-2 text-xs text-gray-500">
                  <div className="bg-white p-2 rounded">Add Players</div>
                  <div className="bg-white p-2 rounded">Draw Arrows</div>
                  <div className="bg-white p-2 rounded">Save Drill</div>
                </div>
          </div>
        </motion.div>

            {/* Practice Plan Builder Preview */}
        <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="space-y-6"
        >
              <div className="bg-gray-100 rounded-lg p-8 text-center">
                <div className="w-full h-64 bg-white rounded-lg shadow-lg flex items-center justify-center mb-4">
          <div className="text-center">
                    <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Calendar className="w-10 h-10 text-green-600" />
            </div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-2" style={{ fontFamily: 'Russo One' }}>
                      Practice Plan Builder
                    </h3>
                    <p className="text-gray-600 text-sm">
                      Create structured practice sessions with timing, drills, and detailed instructions
                    </p>
          </div>
      </div>
                <div className="grid grid-cols-2 gap-2 text-xs text-gray-500">
                  <div className="bg-white p-2 rounded">Warm-up (10min)</div>
                  <div className="bg-white p-2 rounded">Skills (15min)</div>
                  <div className="bg-white p-2 rounded">Systems (20min)</div>
                  <div className="bg-white p-2 rounded">Cool-down (5min)</div>
    </div>
      </div>
            </motion.div>
    </div>

          {/* Dashboard Preview */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="mt-16"
          >
            <div className="bg-gray-100 rounded-lg p-8">
              <div className="w-full h-80 bg-white rounded-lg shadow-lg flex items-center justify-center">
                <div className="text-center">
                  <div className="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Play className="w-12 h-12 text-blue-600" />
        </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-2" style={{ fontFamily: 'Russo One' }}>
                    Coach Dashboard
                  </h3>
                  <p className="text-gray-600 mb-4">
                    Your central hub for managing drills, practice plans, and team collaboration
                  </p>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-2xl font-bold text-blue-600">47</div>
                      <div className="text-gray-600">Custom Drills</div>
            </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-2xl font-bold text-green-600">12</div>
                      <div className="text-gray-600">Practice Plans</div>
          </div>
                    <div className="bg-gray-50 p-3 rounded">
                      <div className="text-2xl font-bold text-purple-600">8</div>
                      <div className="text-gray-600">Team Members</div>
        </div>
          </div>
        </div>
        </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-blue-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4" style={{ fontFamily: 'Russo One' }}>
              How It Works
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Get started in minutes with our simple 3-step process
            </p>
      </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center"
            >
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                1
            </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2" style={{ fontFamily: 'Russo One' }}>
                Create Your Account
              </h3>
              <p className="text-gray-600">
                Sign up for free and get instant access to our drill library and basic tools
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-center"
            >
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                2
                </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2" style={{ fontFamily: 'Russo One' }}>
                Design Your Drills
              </h3>
              <p className="text-gray-600">
                Use our interactive rink canvas to create custom drills or browse our library
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-center"
            >
              <div className="w-16 h-16 bg-blue-600 text-white rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                3
            </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2" style={{ fontFamily: 'Russo One' }}>
                Build Practice Plans
              </h3>
              <p className="text-gray-600">
                Organize drills into complete practice sessions with timing and instructions
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* What You Get Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4" style={{ fontFamily: 'Russo One' }}>
              Everything You Need - Completely Free
            </h2>
            <p className="text-xl text-gray-600">
              No subscriptions, no limits, no hidden fees. Just powerful tools for hockey coaches.
          </p>
        </div>

          <div className="bg-gradient-to-r from-blue-50 to-green-50 rounded-2xl p-8 mb-12">
            <div className="text-center">
              <div className="w-20 h-20 bg-green-500 text-white rounded-full flex items-center justify-center mx-auto mb-4">
                <Check className="w-10 h-10" />
            </div>
              <h3 className="text-3xl font-bold text-gray-900 mb-2" style={{ fontFamily: 'Russo One' }}>
                100% Free Forever
              </h3>
              <p className="text-xl text-gray-600 mb-6">
                All features included at no cost
              </p>
          <button
                onClick={() => router.push('/auth/signup')}
                className="bg-green-600 text-white px-8 py-3 rounded-lg text-lg font-medium hover:bg-green-700 transition-colors"
          >
                Get Started Now - It's Free!
          </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {freeFeatures.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white p-6 rounded-lg shadow-lg border-l-4 border-blue-500"
              >
                <div className="flex items-start">
                  <Check className="w-6 h-6 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700 font-medium">{feature}</span>
        </div>
              </motion.div>
            ))}
      </div>
    </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-600 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-3xl md:text-4xl font-bold text-white mb-4"
            style={{ fontFamily: 'Russo One' }}
          >
            Ready to Transform Your Practice Planning?
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xl text-blue-100 mb-8"
          >
            Join thousands of coaches who trust Hockey Practice Pro - completely free!
          </motion.p>
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            onClick={() => router.push('/auth/signup')}
            className="bg-white text-blue-600 px-8 py-3 rounded-lg text-lg font-medium hover:bg-gray-100 transition-colors"
          >
            Get Started Now - It's Free!
          </motion.button>
            </div>
      </section>

          {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-2xl font-bold mb-4" style={{ fontFamily: 'Russo One' }}>
              Hockey Practice Pro
            </h3>
            <p className="text-gray-400 mb-4">
              Professional hockey practice planning and drill management platform
            </p>
            <p className="text-sm text-gray-500">
              © 2024 Hockey Practice Pro. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}