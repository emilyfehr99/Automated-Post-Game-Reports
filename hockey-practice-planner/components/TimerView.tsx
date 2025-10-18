'use client'

import { useState, useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { 
  Play, 
  Pause, 
  Square, 
  Plus, 
  Trash2, 
  Clock, 
  Timer as TimerIcon,
  RotateCcw,
  Volume2,
  VolumeX
} from 'lucide-react'

interface Timer {
  id: string
  name: string
  duration: number // in seconds
  isRunning: boolean
  timeLeft: number
  originalDuration: number
}

export default function TimerView() {
  const [timers, setTimers] = useState<Timer[]>([])
  const [soundEnabled, setSoundEnabled] = useState(true)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // Initialize with default timers
  useEffect(() => {
    if (timers.length === 0) {
      const defaultTimers: Timer[] = [
        {
          id: 'warmup',
          name: 'Warm-up',
          duration: 300, // 5 minutes
          isRunning: false,
          timeLeft: 300,
          originalDuration: 300
        },
        {
          id: 'drill',
          name: 'Drill Time',
          duration: 180, // 3 minutes
          isRunning: false,
          timeLeft: 180,
          originalDuration: 180
        },
        {
          id: 'break',
          name: 'Break',
          duration: 60, // 1 minute
          isRunning: false,
          timeLeft: 60,
          originalDuration: 60
        }
      ]
      setTimers(defaultTimers)
    }
  }, [timers.length])

  // Timer logic
  useEffect(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
    }

    const runningTimers = timers.filter(t => t.isRunning)
    if (runningTimers.length > 0) {
      intervalRef.current = setInterval(() => {
        setTimers(prevTimers => {
          const updatedTimers = prevTimers.map(timer => {
            if (!timer.isRunning) return timer

            const newTimeLeft = timer.timeLeft - 1
            if (newTimeLeft <= 0) {
              // Timer finished
              if (soundEnabled) {
                playNotificationSound()
              }
              return {
                ...timer,
                timeLeft: 0,
                isRunning: false
              }
            }
            return {
              ...timer,
              timeLeft: newTimeLeft
            }
          })

          return updatedTimers
        })
      }, 1000)
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [timers, soundEnabled])

  const playNotificationSound = () => {
    if (audioRef.current) {
      audioRef.current.play().catch(console.error)
    }
  }

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  const toggleTimer = (id: string) => {
    setTimers(prevTimers =>
      prevTimers.map(timer =>
        timer.id === id
          ? { ...timer, isRunning: !timer.isRunning }
          : timer
      )
    )
  }

  const resetTimer = (id: string) => {
    setTimers(prevTimers =>
      prevTimers.map(timer =>
        timer.id === id
          ? {
              ...timer,
              timeLeft: timer.originalDuration,
              isRunning: false
            }
          : timer
      )
    )
  }

  const updateTimerDuration = (id: string, duration: number) => {
    setTimers(prevTimers =>
      prevTimers.map(timer =>
        timer.id === id
          ? {
              ...timer,
              duration,
              originalDuration: duration,
              timeLeft: duration
            }
          : timer
      )
    )
  }

  const addTimer = () => {
    const newTimer: Timer = {
      id: `timer_${Date.now()}`,
      name: 'New Timer',
      duration: 120, // 2 minutes
      isRunning: false,
      timeLeft: 120,
      originalDuration: 120
    }
    setTimers(prevTimers => [...prevTimers, newTimer])
  }

  const removeTimer = (id: string) => {
    setTimers(prevTimers => prevTimers.filter(timer => timer.id !== id))
  }

  const updateTimerName = (id: string, name: string) => {
    setTimers(prevTimers =>
      prevTimers.map(timer =>
        timer.id === id ? { ...timer, name } : timer
      )
    )
  }

  const runningCount = timers.filter(t => t.isRunning).length
  const finishedCount = timers.filter(t => t.timeLeft === 0).length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4">
        <div>
          <h2 className="text-2xl font-russo text-hockey-blue mb-2">Practice Timer</h2>
          <p className="text-gray-600">Manage multiple timers for your practice sessions</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            className={`p-2 rounded-lg transition-colors ${
              soundEnabled 
                ? 'bg-hockey-blue text-white' 
                : 'bg-gray-200 text-gray-600'
            }`}
            title={soundEnabled ? 'Sound enabled' : 'Sound disabled'}
          >
            {soundEnabled ? <Volume2 className="w-5 h-5" /> : <VolumeX className="w-5 h-5" />}
          </button>
          <button
            onClick={addTimer}
            className="hockey-button-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Add Timer
          </button>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center">
            <TimerIcon className="w-8 h-8 text-hockey-blue mr-3" />
            <div>
              <p className="text-sm text-gray-600">Total Timers</p>
              <p className="text-2xl font-bold text-hockey-blue">{timers.length}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center">
            <Play className="w-8 h-8 text-green-500 mr-3" />
            <div>
              <p className="text-sm text-gray-600">Running</p>
              <p className="text-2xl font-bold text-green-500">{runningCount}</p>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center">
            <Clock className="w-8 h-8 text-red-500 mr-3" />
            <div>
              <p className="text-sm text-gray-600">Finished</p>
              <p className="text-2xl font-bold text-red-500">{finishedCount}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Timer Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {timers.map((timer) => (
          <motion.div
            key={timer.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className={`bg-white rounded-lg p-6 border-2 transition-all duration-300 ${
              timer.isRunning 
                ? 'border-green-500 shadow-lg' 
                : timer.timeLeft === 0 
                  ? 'border-red-500' 
                  : 'border-gray-200'
            }`}
          >
            {/* Timer Header */}
            <div className="flex justify-between items-start mb-4">
              <input
                type="text"
                value={timer.name}
                onChange={(e) => updateTimerName(timer.id, e.target.value)}
                className="font-medium text-lg bg-transparent border-none outline-none focus:bg-gray-50 rounded px-1 -ml-1"
                disabled={timer.isRunning}
              />
              {timers.length > 1 && (
                <button
                  onClick={() => removeTimer(timer.id)}
                  className="text-red-500 hover:text-red-700 transition-colors"
                  disabled={timer.isRunning}
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>

            {/* Timer Display */}
            <div className="text-center mb-4">
              <div className={`text-4xl font-mono font-bold mb-2 ${
                timer.timeLeft === 0 
                  ? 'text-red-500' 
                  : timer.isRunning 
                    ? 'text-green-500' 
                    : 'text-hockey-blue'
              }`}>
                {formatTime(timer.timeLeft)}
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-1000 ${
                    timer.timeLeft === 0 
                      ? 'bg-red-500' 
                      : timer.isRunning 
                        ? 'bg-green-500' 
                        : 'bg-hockey-blue'
                  }`}
                  style={{
                    width: `${((timer.originalDuration - timer.timeLeft) / timer.originalDuration) * 100}%`
                  }}
                />
              </div>
            </div>

            {/* Duration Control */}
            {!timer.isRunning && (
              <div className="mb-4">
                <label className="block text-sm text-gray-600 mb-2">Duration (minutes)</label>
                <input
                  type="number"
                  min="1"
                  max="60"
                  value={Math.floor(timer.duration / 60)}
                  onChange={(e) => updateTimerDuration(timer.id, parseInt(e.target.value) * 60)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-hockey-blue focus:border-transparent"
                />
              </div>
            )}

            {/* Controls */}
            <div className="flex justify-center gap-2">
              <button
                onClick={() => toggleTimer(timer.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                  timer.isRunning
                    ? 'bg-red-500 hover:bg-red-600 text-white'
                    : 'bg-green-500 hover:bg-green-600 text-white'
                }`}
              >
                {timer.isRunning ? (
                  <>
                    <Pause className="w-4 h-4" />
                    Pause
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Start
                  </>
                )}
              </button>
              
              <button
                onClick={() => resetTimer(timer.id)}
                className="flex items-center gap-2 px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded-lg font-medium transition-colors"
                disabled={timer.isRunning}
              >
                <RotateCcw className="w-4 h-4" />
                Reset
              </button>
            </div>

            {/* Status */}
            {timer.timeLeft === 0 && (
              <div className="mt-3 text-center">
                <p className="text-red-500 font-medium">⏰ Timer Finished!</p>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      {/* Audio element for notifications */}
      <audio ref={audioRef} preload="auto">
        <source src="data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQdBTuBzvPZizEIHm7A7+OZURE=" type="audio/wav" />
      </audio>
    </div>
  )
}
