'use client'

import { motion } from 'framer-motion'
import { Check, Star } from 'lucide-react'

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

export default function Pricing() {
  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl font-bold text-gray-900 mb-4"
            style={{ fontFamily: 'Russo One' }}
          >
            Choose Your Plan
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-xl text-gray-600 max-w-2xl mx-auto"
          >
            Start free and upgrade as your coaching needs grow
          </motion.p>
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

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="text-center mt-16"
        >
          <p className="text-gray-600 mb-4">
            All plans include a 14-day free trial. No credit card required.
          </p>
          <p className="text-sm text-gray-500">
            Questions? Contact us at{' '}
            <a href="mailto:support@hockeypracticepro.com" className="text-blue-600 hover:text-blue-500">
              support@hockeypracticepro.com
            </a>
          </p>
        </motion.div>
      </div>
    </div>
  )
}
