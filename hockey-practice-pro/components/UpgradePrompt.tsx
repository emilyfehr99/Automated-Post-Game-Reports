'use client'

import { motion } from 'framer-motion'
import { Crown, X, ArrowRight } from 'lucide-react'
import { useRouter } from 'next/navigation'

interface UpgradePromptProps {
  isOpen: boolean
  onClose: () => void
  feature: string
  currentPlan: string
  requiredPlan: string
}

export default function UpgradePrompt({ 
  isOpen, 
  onClose, 
  feature, 
  currentPlan, 
  requiredPlan 
}: UpgradePromptProps) {
  const router = useRouter()

  if (!isOpen) return null

  const getPlanBenefits = (plan: string) => {
    switch (plan) {
      case 'pro':
        return [
          'Unlimited practice plans',
          'Unlimited custom drills',
          'Advanced drill drawing tool',
          'PDF export functionality',
          'Team collaboration features',
          'Priority support'
        ]
      case 'team':
        return [
          'Everything in Pro',
          'Up to 10 team members',
          'Advanced analytics',
          'Custom branding',
          'API access',
          'Dedicated account manager'
        ]
      default:
        return []
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white rounded-lg max-w-md w-full p-6"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Crown className="w-6 h-6 text-yellow-500 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900" style={{ fontFamily: 'Russo One' }}>
              Upgrade Required
            </h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="mb-6">
          <p className="text-gray-600 mb-4">
            The <strong>{feature}</strong> feature requires a <strong>{requiredPlan}</strong> plan or higher.
            You're currently on the <strong>{currentPlan}</strong> plan.
          </p>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-2">
              Upgrade to {requiredPlan === 'pro' ? 'Pro' : 'Team'} and get:
            </h4>
            <ul className="text-sm text-blue-800 space-y-1">
              {getPlanBenefits(requiredPlan).map((benefit, index) => (
                <li key={index} className="flex items-center">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-2"></div>
                  {benefit}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="flex space-x-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
          >
            Maybe Later
          </button>
          <button
            onClick={() => {
              router.push('/pricing')
              onClose()
            }}
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center"
          >
            Upgrade Now
            <ArrowRight className="w-4 h-4 ml-2" />
          </button>
        </div>
      </motion.div>
    </div>
  )
}
