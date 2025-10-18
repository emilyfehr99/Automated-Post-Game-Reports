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

export default function LandingPage() {
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

  const plans = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      description: 'Perfect for getting started',
      features: [
        'Up to 5 practice plans',
        'Up to 20 custom drills',
        'Basic drill drawing tool',
        'Community drill library access',
        'Email support'
      ],
      popular: false
    },
    {
      name: 'Pro',
      price: '$19',
      period: 'per month',
      description: 'For serious coaches and teams',
      features: [
        'Unlimited practice plans',
        'Unlimited custom drills',
        'Advanced drill drawing tool',
        'Full drill library access',
        'Team collaboration features',
        'PDF export functionality',
        'Priority support',
        'Mobile app access',
        'Video drill integration'
      ],
      popular: true
    },
    {
      name: 'Team',
      price: '$49',
      period: 'per month',
      description: 'For organizations and clubs',
      features: [
        'Everything in Pro',
        'Up to 10 team members',
        'Advanced analytics',
        'Custom branding',
        'API access',
        'Dedicated account manager',
        'Custom training sessions'
      ],
      popular: false
    }
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

      {/* Pricing Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4" style={{ fontFamily: 'Russo One' }}>
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600">
              Start free and upgrade as your coaching needs grow
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map((plan, index) => (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className={`relative bg-white rounded-2xl shadow-lg p-8 ${
                  plan.popular ? 'ring-2 ring-blue-500 scale-105' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-medium flex items-center">
                      <Star className="w-4 h-4 mr-1" />
                      Most Popular
                    </div>
                  </div>
                )}

                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2" style={{ fontFamily: 'Russo One' }}>
                    {plan.name}
                  </h3>
                  <div className="mb-2">
                    <span className="text-4xl font-bold text-gray-900">{plan.price}</span>
                    <span className="text-gray-600 ml-1">/{plan.period}</span>
                  </div>
                  <p className="text-gray-600">{plan.description}</p>
                </div>

                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => router.push('/auth/signup')}
                  className={`w-full py-3 px-6 rounded-lg font-medium transition-colors ${
                    plan.popular
                      ? 'bg-blue-600 text-white hover:bg-blue-700'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  {plan.name === 'Free' ? 'Get Started' : 'Start Free Trial'}
                </button>
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
            Join thousands of coaches who trust Hockey Practice Pro
          </motion.p>
          <motion.button
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            onClick={() => router.push('/auth/signup')}
            className="bg-white text-blue-600 px-8 py-3 rounded-lg text-lg font-medium hover:bg-gray-100 transition-colors"
          >
            Start Your Free Trial Today
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
