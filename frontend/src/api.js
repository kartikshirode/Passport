import axios from 'axios'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout for image processing
  headers: {
    'Content-Type': 'multipart/form-data',
  },
})

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`)
    return config
  },
  (error) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log('Response received:', response.status)
    return response
  },
  (error) => {
    console.error('Response error:', error.response?.data || error.message)
    
    // Handle different error types
    if (error.code === 'ECONNABORTED') {
      throw new Error('Request timed out. Please try again.')
    }
    
    if (error.response?.status === 413) {
      throw new Error('File too large. Please use an image smaller than 8MB.')
    }
    
    if (error.response?.status === 400) {
      throw new Error(error.response.data?.detail || 'Invalid request')
    }
    
    if (error.response?.status >= 500) {
      throw new Error('Server error. Please try again later.')
    }
    
    throw error
  }
)

// API Functions
export const apiClient = {
  // Health check
  async healthCheck() {
    try {
      const response = await api.get('/health')
      return response.data
    } catch (error) {
      console.error('Health check failed:', error)
      throw new Error('API is not available')
    }
  },

  // Process single photo
  async processPhoto({
    file,
    bgColor = 'white',
    makeA4 = false,
    faceScale = 2.2,
    brightness = 1.0,
    contrast = 1.0,
    cropData = null
  }) {
    try {
      // Validate file
      if (!file) {
        throw new Error('No file provided')
      }

      if (!file.type.startsWith('image/')) {
        throw new Error('File must be an image')
      }

      // Check file size (8MB limit)
      const maxSize = 8 * 1024 * 1024
      if (file.size > maxSize) {
        throw new Error('File size must be less than 8MB')
      }

      // Create form data
      const formData = new FormData()
      formData.append('file', file)
      formData.append('bg_color', bgColor)
      formData.append('make_a4', makeA4.toString())
      formData.append('face_scale', faceScale.toString())
      formData.append('brightness', brightness.toString())
      formData.append('contrast', contrast.toString())
      
      // Add crop data if provided
      if (cropData) {
        formData.append('crop_x', cropData.x.toString())
        formData.append('crop_y', cropData.y.toString())
        formData.append('crop_width', cropData.width.toString())
        formData.append('crop_height', cropData.height.toString())
        if (cropData.rotation) {
          formData.append('crop_rotation', cropData.rotation.toString())
        }
      }

      console.log('Processing photo with params:', {
        filename: file.name,
        size: file.size,
        bgColor,
        makeA4,
        faceScale,
        brightness,
        contrast
      })

      const response = await api.post('/process', formData)
      return response.data
    } catch (error) {
      console.error('Photo processing failed:', error)
      throw error
    }
  },

  // Batch process multiple photos
  async batchProcessPhotos({
    files,
    bgColor = 'white',
    makeA4 = true
  }) {
    try {
      if (!files || files.length === 0) {
        throw new Error('No files provided')
      }

      if (files.length > 10) {
        throw new Error('Maximum 10 files allowed')
      }

      // Validate all files
      for (const file of files) {
        if (!file.type.startsWith('image/')) {
          throw new Error(`${file.name} is not an image file`)
        }
        
        if (file.size > 8 * 1024 * 1024) {
          throw new Error(`${file.name} is too large (max 8MB)`)
        }
      }

      // Create form data
      const formData = new FormData()
      files.forEach(file => {
        formData.append('files', file)
      })
      formData.append('bg_color', bgColor)
      formData.append('make_a4', makeA4.toString())

      console.log('Batch processing photos:', {
        fileCount: files.length,
        bgColor,
        makeA4
      })

      const response = await api.post('/batch-process', formData)
      return response.data
    } catch (error) {
      console.error('Batch processing failed:', error)
      throw error
    }
  },

  // Get API info
  async getApiInfo() {
    try {
      const response = await api.get('/')
      return response.data
    } catch (error) {
      console.error('Failed to get API info:', error)
      throw error
    }
  }
}

// Utility functions
export const utils = {
  // Convert file to base64
  fileToBase64(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.readAsDataURL(file)
      reader.onload = () => resolve(reader.result)
      reader.onerror = error => reject(error)
    })
  },

  // Download file from data URI
  downloadFromDataUri(dataUri, filename) {
    try {
      const link = document.createElement('a')
      link.href = dataUri
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    } catch (error) {
      console.error('Download failed:', error)
      throw new Error('Failed to download file')
    }
  },

  // Format file size
  formatFileSize(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    if (bytes === 0) return '0 Bytes'
    const i = Math.floor(Math.log(bytes) / Math.log(1024))
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
  },

  // Validate image dimensions
  async getImageDimensions(file) {
    return new Promise((resolve) => {
      const img = new Image()
      img.onload = () => {
        resolve({
          width: img.naturalWidth,
          height: img.naturalHeight,
          aspectRatio: img.naturalWidth / img.naturalHeight
        })
      }
      img.src = URL.createObjectURL(file)
    })
  },

  // Generate thumbnail
  async generateThumbnail(file, maxWidth = 300, maxHeight = 300) {
    return new Promise((resolve) => {
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      const img = new Image()
      
      img.onload = () => {
        // Calculate thumbnail dimensions
        let { width, height } = img
        
        if (width > height) {
          if (width > maxWidth) {
            height = (height * maxWidth) / width
            width = maxWidth
          }
        } else {
          if (height > maxHeight) {
            width = (width * maxHeight) / height
            height = maxHeight
          }
        }
        
        canvas.width = width
        canvas.height = height
        
        // Draw and convert to blob
        ctx.drawImage(img, 0, 0, width, height)
        canvas.toBlob(resolve, 'image/jpeg', 0.8)
      }
      
      img.src = URL.createObjectURL(file)
    })
  }
}

export default api