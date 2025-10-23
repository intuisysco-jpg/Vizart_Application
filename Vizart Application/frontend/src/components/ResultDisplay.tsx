'use client'

import { Download, Share, Heart } from 'lucide-react'

interface ResultDisplayProps {
  result: {
    imageUrl?: string
    extractedGarments?: Array<{
      type: 'upper' | 'lower' | 'full'
      imageUrl: string
    }>
  }
  mode: 'try-on' | 'try-off'
}

export default function ResultDisplay({ result, mode }: ResultDisplayProps) {
  const handleDownload = (imageUrl: string, filename: string) => {
    const link = document.createElement('a')
    link.href = imageUrl
    link.download = filename
    link.click()
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        {mode === 'try-on' ? 'Try-On Result' : 'Extracted Garments'}
      </h3>

      {mode === 'try-on' && result.imageUrl && (
        <div className="space-y-4">
          <div className="relative">
            <img
              src={result.imageUrl}
              alt="Try-on result"
              className="w-full h-96 object-contain bg-gray-50 rounded-lg"
            />
          </div>

          <div className="flex justify-center space-x-4">
            <button
              onClick={() => handleDownload(result.imageUrl!, 'try-on-result.png')}
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Download className="w-4 h-4" />
              Download
            </button>
            <button className="flex items-center gap-2 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors">
              <Share className="w-4 h-4" />
              Share
            </button>
          </div>
        </div>
      )}

      {mode === 'try-off' && result.extractedGarments && (
        <div className="space-y-6">
          <div className="grid md:grid-cols-3 gap-4">
            {result.extractedGarments.map((garment, index) => (
              <div key={index} className="space-y-3">
                <div className="relative">
                  <img
                    src={garment.imageUrl}
                    alt={`Extracted ${garment.type} garment`}
                    className="w-full h-48 object-contain bg-gray-50 rounded-lg"
                  />
                  <span className="absolute top-2 left-2 bg-blue-600 text-white text-xs px-2 py-1 rounded">
                    {garment.type.charAt(0).toUpperCase() + garment.type.slice(1)}
                  </span>
                </div>

                <div className="flex justify-center space-x-2">
                  <button
                    onClick={() => handleDownload(garment.imageUrl, `extracted-${garment.type}-garment.png`)}
                    className="flex items-center gap-1 bg-blue-600 text-white px-3 py-1.5 rounded text-sm hover:bg-blue-700 transition-colors"
                  >
                    <Download className="w-3 h-3" />
                    Download
                  </button>
                  <button className="flex items-center gap-1 bg-gray-200 text-gray-700 px-3 py-1.5 rounded text-sm hover:bg-gray-300 transition-colors">
                    <Heart className="w-3 h-3" />
                    Save
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div className="border-t pt-4">
            <h4 className="font-medium text-gray-900 mb-2">Batch Download</h4>
            <div className="flex justify-center">
              <button className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
                <Download className="w-4 h-4" />
                Download All Garments
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}