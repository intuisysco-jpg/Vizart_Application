'use client'

import { useState } from 'react'
import ImageUpload from '@/components/ImageUpload'
import ProcessingStatus from '@/components/ProcessingStatus'
import ResultDisplay from '@/components/ResultDisplay'
import { ModeSelector } from '@/components/ModeSelector'

export default function Home() {
  const [mode, setMode] = useState<'try-on' | 'try-off'>('try-on')
  const [uploadedImages, setUploadedImages] = useState<{
    model?: File
    garment?: File
  }>({})
  const [processingStatus, setProcessingStatus] = useState<{
    isProcessing: boolean
    progress: number
    message: string
  }>({
    isProcessing: false,
    progress: 0,
    message: ''
  })
  const [result, setResult] = useState<{
    imageUrl?: string
    extractedGarments?: Array<{
      type: 'upper' | 'lower' | 'full'
      imageUrl: string
    }>
  }>({})

  const handleImageUpload = (type: 'model' | 'garment', file: File) => {
    setUploadedImages(prev => ({
      ...prev,
      [type]: file
    }))
  }

  const handleProcess = async () => {
    if (!uploadedImages.model) {
      alert('Please upload a model image')
      return
    }

    if (mode === 'try-on' && !uploadedImages.garment) {
      alert('Please upload a garment image for try-on')
      return
    }

    setProcessingStatus({
      isProcessing: true,
      progress: 0,
      message: 'Starting processing...'
    })

    try {
      const formData = new FormData()
      formData.append('model_image', uploadedImages.model)
      if (mode === 'try-on' && uploadedImages.garment) {
        formData.append('garment_image', uploadedImages.garment)
      }

      const endpoint = mode === 'try-on'
        ? '/api/v1/try-on'
        : '/api/v1/try-off'

      // Simulate API call
      simulateProgress()

      // const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
      //   method: 'POST',
      //   body: formData
      // })

      // const result = await response.json()

      setTimeout(() => {
        setResult({
          imageUrl: '/api/placeholder/400/600',
          extractedGarments: mode === 'try-off' ? [
            { type: 'upper', imageUrl: '/api/placeholder/200/300' },
            { type: 'lower', imageUrl: '/api/placeholder/200/300' }
          ] : undefined
        })
        setProcessingStatus({
          isProcessing: false,
          progress: 100,
          message: 'Processing complete!'
        })
      }, 3000)

    } catch (error) {
      console.error('Processing failed:', error)
      setProcessingStatus({
        isProcessing: false,
        progress: 0,
        message: 'Processing failed. Please try again.'
      })
    }
  }

  const simulateProgress = () => {
    let progress = 0
    const messages = [
      'Analyzing image...',
      'Detecting pose...',
      'Processing garments...',
      'Generating result...'
    ]

    const interval = setInterval(() => {
      progress += Math.random() * 30
      if (progress > 90) progress = 90

      const messageIndex = Math.floor(progress / 25)
      setProcessingStatus(prev => ({
        ...prev,
        progress: Math.min(progress, 100),
        message: messages[Math.min(messageIndex, messages.length - 1)]
      }))

      if (progress >= 90) {
        clearInterval(interval)
      }
    }, 500)
  }

  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Vizart AI Studio
          </h1>
          <p className="text-lg text-gray-600">
            AI-Powered Virtual Try-On & Try-Off Technology
          </p>
        </header>

        <ModeSelector
          selectedMode={mode}
          onModeChange={setMode}
        />

        <div className="grid md:grid-cols-2 gap-8 mb-8">
          <div className="space-y-6">
            <ImageUpload
              label="Model Image"
              onImageUpload={(file) => handleImageUpload('model', file)}
              acceptedTypes="image/*"
              className="w-full"
            />

            {mode === 'try-on' && (
              <ImageUpload
                label="Garment Image"
                onImageUpload={(file) => handleImageUpload('garment', file)}
                acceptedTypes="image/*"
                className="w-full"
              />
            )}
          </div>

          <div className="space-y-6">
            <ProcessingStatus status={processingStatus} />

            {!processingStatus.isProcessing && (
              <button
                onClick={handleProcess}
                disabled={!uploadedImages.model || (mode === 'try-on' && !uploadedImages.garment)}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {mode === 'try-on' ? 'Try On Garment' : 'Extract Garments'}
              </button>
            )}
          </div>
        </div>

        {(result.imageUrl || result.extractedGarments) && (
          <ResultDisplay
            result={result}
            mode={mode}
          />
        )}
      </div>
    </main>
  )
}