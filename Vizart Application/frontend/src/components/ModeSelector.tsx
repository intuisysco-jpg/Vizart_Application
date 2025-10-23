'use client'

import { Shirt, Package } from 'lucide-react'

interface ModeSelectorProps {
  selectedMode: 'try-on' | 'try-off'
  onModeChange: (mode: 'try-on' | 'try-off') => void
}

export function ModeSelector({ selectedMode, onModeChange }: ModeSelectorProps) {
  return (
    <div className="flex justify-center mb-8">
      <div className="bg-white rounded-lg shadow-md p-1 inline-flex">
        <button
          onClick={() => onModeChange('try-on')}
          className={`flex items-center gap-2 px-6 py-3 rounded-md font-medium transition-all ${
            selectedMode === 'try-on'
              ? 'bg-blue-600 text-white'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Shirt className="w-5 h-5" />
          Try On
        </button>
        <button
          onClick={() => onModeChange('try-off')}
          className={`flex items-center gap-2 px-6 py-3 rounded-md font-medium transition-all ${
            selectedMode === 'try-off'
              ? 'bg-blue-600 text-white'
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          <Package className="w-5 h-5" />
          Try Off
        </button>
      </div>
    </div>
  )
}