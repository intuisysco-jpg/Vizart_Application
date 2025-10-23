export interface ProcessingJob {
  id: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  progress: number
  message: string
  createdAt: Date
  completedAt?: Date
  result?: JobResult
}

export interface JobResult {
  imageUrl?: string
  extractedGarments?: ExtractedGarment[]
  processingTime?: number
}

export interface ExtractedGarment {
  id: string
  type: 'upper' | 'lower' | 'full'
  imageUrl: string
  maskUrl?: string
  confidence: number
  metadata?: {
    color?: string
    pattern?: string
    style?: string
  }
}

export interface TryOnRequest {
  modelImage: File
  garmentImage: File
  options?: {
    preserveBackground?: boolean
    adjustSize?: boolean
    garmentType?: 'upper' | 'lower' | 'full'
  }
}

export interface TryOffRequest {
  modelImage: File
  options?: {
    extractAll?: boolean
    garmentTypes?: ('upper' | 'lower' | 'full')[]
    outputFormat?: 'png' | 'jpg' | 'webp'
  }
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  jobId?: string
}

export interface ErrorResponse {
  error: string
  code: string
  details?: any
}