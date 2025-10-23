import { useState, useCallback, useRef } from 'react'
import { apiClient, pollJobStatus } from '@/lib/api'
import { ProcessingJob, TryOnRequest, TryOffRequest } from '@/types'

interface UseProcessingResult {
  isProcessing: boolean
  progress: number
  message: string
  job: ProcessingJob | null
  error: string | null
  startTryOn: (request: TryOnRequest) => Promise<void>
  startTryOff: (request: TryOffRequest) => Promise<void>
  cancelProcessing: () => Promise<void>
  reset: () => void
}

export function useProcessing(): UseProcessingResult {
  const [isProcessing, setIsProcessing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [message, setMessage] = useState('')
  const [job, setJob] = useState<ProcessingJob | null>(null)
  const [error, setError] = useState<string | null>(null)

  const pollingRef = useRef<NodeJS.Timeout | null>(null)

  const updateJobStatus = useCallback((jobStatus: ProcessingJob) => {
    setJob(jobStatus)
    setProgress(jobStatus.progress)
    setMessage(jobStatus.message)

    if (jobStatus.status === 'completed' || jobStatus.status === 'failed') {
      setIsProcessing(false)
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
  }, [])

  const startTryOn = useCallback(async (request: TryOnRequest) => {
    setIsProcessing(true)
    setProgress(0)
    setMessage('Initializing try-on process...')
    setError(null)

    try {
      const response = await apiClient.submitTryOn(request)

      if (!response.success || !response.data?.jobId) {
        throw new Error(response.error || 'Failed to submit try-on request')
      }

      const jobId = response.data.jobId

      // Start polling for status updates
      pollJobStatus(jobId, updateJobStatus)
        .then(() => {
          console.log('Try-on processing completed')
        })
        .catch((err) => {
          setError(err.message || 'Processing failed')
          setIsProcessing(false)
        })

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start processing')
      setIsProcessing(false)
    }
  }, [updateJobStatus])

  const startTryOff = useCallback(async (request: TryOffRequest) => {
    setIsProcessing(true)
    setProgress(0)
    setMessage('Initializing garment extraction...')
    setError(null)

    try {
      const response = await apiClient.submitTryOff(request)

      if (!response.success || !response.data?.jobId) {
        throw new Error(response.error || 'Failed to submit try-off request')
      }

      const jobId = response.data.jobId

      // Start polling for status updates
      pollJobStatus(jobId, updateJobStatus)
        .then(() => {
          console.log('Try-off processing completed')
        })
        .catch((err) => {
          setError(err.message || 'Processing failed')
          setIsProcessing(false)
        })

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start processing')
      setIsProcessing(false)
    }
  }, [updateJobStatus])

  const cancelProcessing = useCallback(async () => {
    if (!job?.id) return

    try {
      await apiClient.cancelJob(job.id)
      setIsProcessing(false)
      setProgress(0)
      setMessage('')
      setJob(null)

      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel processing')
    }
  }, [job])

  const reset = useCallback(() => {
    setIsProcessing(false)
    setProgress(0)
    setMessage('')
    setJob(null)
    setError(null)

    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [])

  return {
    isProcessing,
    progress,
    message,
    job,
    error,
    startTryOn,
    startTryOff,
    cancelProcessing,
    reset,
  }
}