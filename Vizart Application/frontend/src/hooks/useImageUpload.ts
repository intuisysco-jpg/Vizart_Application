import { useState, useCallback } from 'react'
import { validateImageFile, createImagePreview } from '@/lib/utils'

interface UseImageUploadResult {
  image: File | null
  preview: string | null
  isUploading: boolean
  error: string | null
  uploadImage: (file: File) => Promise<void>
  clearImage: () => void
}

export function useImageUpload(): UseImageUploadResult {
  const [image, setImage] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const uploadImage = useCallback(async (file: File) => {
    setError(null)
    setIsUploading(true)

    try {
      // Validate file
      const validation = validateImageFile(file)
      if (!validation.isValid) {
        setError(validation.error || 'Invalid file')
        return
      }

      // Create preview
      const previewUrl = await createImagePreview(file)

      setImage(file)
      setPreview(previewUrl)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
    } finally {
      setIsUploading(false)
    }
  }, [])

  const clearImage = useCallback(() => {
    setImage(null)
    setPreview(null)
    setError(null)
  }, [])

  return {
    image,
    preview,
    isUploading,
    error,
    uploadImage,
    clearImage,
  }
}