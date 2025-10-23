'use client'

import { Loader2 } from 'lucide-react'

interface ProcessingStatusProps {
  status: {
    isProcessing: boolean
    progress: number
    message: string
  }
}

export default function ProcessingStatus({ status }: ProcessingStatusProps) {
  if (!status.isProcessing && status.progress === 0) {
    return null
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center space-x-3 mb-4">
        <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
        <h3 className="text-lg font-semibold text-gray-900">
          {status.isProcessing ? 'Processing...' : 'Complete!'}
        </h3>
      </div>

      <div className="space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-gray-600">{status.message}</span>
          <span className="font-medium text-gray-900">
            {Math.round(status.progress)}%
          </span>
        </div>

        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${status.progress}%` }}
          />
        </div>

        {status.isProcessing && (
          <p className="text-xs text-gray-500 mt-2">
            This may take a few moments depending on image complexity...
          </p>
        )}
      </div>
    </div>
  )
}