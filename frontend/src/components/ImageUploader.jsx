import React, { useState, useRef, useCallback, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import Webcam from 'react-webcam'
import { ChromePicker } from 'react-color'
import { 
  Camera, 
  Upload, 
  X, 
  Download, 
  Settings,
  Crop, 
  RefreshCw, 
  AlertCircle, 
  CheckCircle,
  FileImage,
  Palette,
  Layout,
  Zap,
  Eye,
  Loader2
} from 'lucide-react'
import { apiClient, utils } from '../api'
import CropAdjuster from './CropAdjuster'

// MediaPipe Face Detection (lazy loaded)
let FaceDetection = null
let MediaPipeCamera = null

const loadMediaPipe = async () => {
  if (!FaceDetection) {
    try {
      const faceDetectionModule = await import('@mediapipe/face_detection')
      const cameraModule = await import('@mediapipe/camera_utils')
      FaceDetection = faceDetectionModule.FaceDetection
      MediaPipeCamera = cameraModule.Camera
      return true
    } catch (error) {
      console.warn('MediaPipe not available:', error)
      return false
    }
  }
  return true
}

// Background color presets
const BACKGROUND_COLORS = [
  { name: 'White', value: 'white', hex: '#FFFFFF' },
  { name: 'Light Blue', value: 'light_blue', hex: '#ADD8E6' },
  { name: 'Blue', value: 'blue', hex: '#0066CC' },
  { name: 'Light Gray', value: 'light_gray', hex: '#D3D3D3' },
  { name: 'Red', value: 'red', hex: '#CC0000' },
  { name: 'Light Red', value: 'light_red', hex: '#FFB6C1' },
]

export default function ImageUploader() {
  // Core state
  const [selectedFile, setSelectedFile] = useState(null)
  const [processedResult, setProcessedResult] = useState(null)
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState(null)
  
  // Crop adjuster state
  const [showCropAdjuster, setShowCropAdjuster] = useState(false)
  const [cropData, setCropData] = useState(null)
  const [success, setSuccess] = useState(false)
  
  // UI state
  const [showWebcam, setShowWebcam] = useState(false)
  const [showAdvanced, setShowAdvanced] = useState(false)
  const [showColorPicker, setShowColorPicker] = useState(false)
  const [processingProgress, setProcessingProgress] = useState(0)
  
  // Processing options
  const [bgColor, setBgColor] = useState('white')
  const [customColor, setCustomColor] = useState('#FFFFFF')
  const [makeA4, setMakeA4] = useState(false)
  const [faceScale, setFaceScale] = useState(2.2)
  const [brightness, setBrightness] = useState(1.0)
  const [contrast, setContrast] = useState(1.0)
  
  // MediaPipe state
  const [faceDetectionEnabled, setFaceDetectionEnabled] = useState(true)
  const [detectedFaces, setDetectedFaces] = useState([])
  const [mediaPipeReady, setMediaPipeReady] = useState(false)
  
  // Refs
  const webcamRef = useRef(null)
  const fileInputRef = useRef(null)
  const faceDetectionRef = useRef(null)
  const canvasRef = useRef(null)
  
  // Load MediaPipe on mount
  useEffect(() => {
    loadMediaPipe().then(setMediaPipeReady)
  }, [])
  
  // File drop configuration
  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp', '.bmp']
    },
    maxSize: 8 * 1024 * 1024, // 8MB
    maxFiles: 1,
    onDrop: useCallback((acceptedFiles, rejectedFiles) => {
      if (rejectedFiles.length > 0) {
        const rejection = rejectedFiles[0]
        if (rejection.errors[0]?.code === 'file-too-large') {
          setError('File too large. Maximum size is 8MB.')
        } else if (rejection.errors[0]?.code === 'file-invalid-type') {
          setError('Invalid file type. Please use JPG, PNG, or WebP.')
        } else {
          setError('Invalid file. Please try again.')
        }
        return
      }
      
      if (acceptedFiles.length > 0) {
        handleFileSelect(acceptedFiles[0])
      }
    }, [])
  })
  
  // Handle file selection
  const handleFileSelect = async (file) => {
    try {
      setError(null)
      setSuccess(false)
      setProcessedResult(null)
      
      // Validate file
      const dimensions = await utils.getImageDimensions(file)
      
      if (dimensions.width < 200 || dimensions.height < 200) {
        setError('Image too small. Minimum 200x200 pixels required.')
        return
      }
      
      setSelectedFile(file)
      
      // Run client-side face detection if enabled and available
      if (faceDetectionEnabled && mediaPipeReady) {
        await runFaceDetection(file)
      }
      
    } catch (error) {
      console.error('File selection error:', error)
      setError('Failed to process file. Please try again.')
    }
  }
  
  // MediaPipe face detection
  const runFaceDetection = async (file) => {
    if (!FaceDetection || !file) return
    
    try {
      const imageUrl = URL.createObjectURL(file)
      const img = new Image()
      
      img.onload = async () => {
        const faceDetection = new FaceDetection({
          locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`
        })
        
        faceDetection.setOptions({
          model: 'short', // 'short' for close-range detection
          minDetectionConfidence: 0.5
        })
        
        faceDetection.onResults((results) => {
          if (results.detections && results.detections.length > 0) {
            setDetectedFaces(results.detections)
            console.log(`Detected ${results.detections.length} face(s)`)
          } else {
            console.log('No faces detected')
            setDetectedFaces([])
          }
        })
        
        await faceDetection.send({ image: img })
        URL.revokeObjectURL(imageUrl)
      }
      
      img.src = imageUrl
    } catch (error) {
      console.error('Face detection error:', error)
    }
  }
  
  // Webcam capture
  const captureWebcam = useCallback(() => {
    if (!webcamRef.current) return
    
    const imageSrc = webcamRef.current.getScreenshot()
    if (imageSrc) {
      // Convert data URL to file
      fetch(imageSrc)
        .then(res => res.blob())
        .then(blob => {
          const file = new File([blob], 'webcam-capture.jpg', { type: 'image/jpeg' })
          handleFileSelect(file)
        })
        .catch(error => {
          console.error('Webcam capture error:', error)
          setError('Failed to capture photo. Please try again.')
        })
    }
    
    setShowWebcam(false)
  }, [])
  
  // Process photo
  const processPhoto = async () => {
    if (!selectedFile) {
      setError('Please select a file first')
      return
    }
    
    setProcessing(true)
    setError(null)
    setSuccess(false)
    setProcessingProgress(0)
    
    try {
      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProcessingProgress(prev => Math.min(prev + 10, 90))
      }, 200)
      
      const result = await apiClient.processPhoto({
        file: selectedFile,
        bgColor: bgColor === 'custom' ? customColor : bgColor,
        makeA4,
        faceScale,
        brightness,
        contrast,
        cropData
      })
      
      clearInterval(progressInterval)
      setProcessingProgress(100)
      
      setProcessedResult(result)
      setSuccess(true)
      
      // Show success animation
      setTimeout(() => setSuccess(false), 3000)
      
    } catch (error) {
      console.error('Processing error:', error)
      setError(error.message || 'Processing failed. Please try again.')
    } finally {
      setProcessing(false)
      setProcessingProgress(0)
    }
  }
  
  // Download result
  const downloadResult = () => {
    if (!processedResult?.file) return
    
    try {
      const filename = processedResult.is_pdf 
        ? 'passport-photos-a4.pdf' 
        : 'passport-photo.png'
      
      utils.downloadFromDataUri(processedResult.file, filename)
    } catch (error) {
      console.error('Download error:', error)
      setError('Failed to download file. Please try again.')
    }
  }
  
  // Reset form
  const resetForm = () => {
    setSelectedFile(null)
    setProcessedResult(null)
    setError(null)
    setSuccess(false)
    setDetectedFaces([])
    setProcessingProgress(0)
    setCropData(null)
    setShowCropAdjuster(false)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }
  
  // Get current background color for preview
  const getCurrentBgColor = () => {
    if (bgColor === 'custom') return customColor
    const preset = BACKGROUND_COLORS.find(c => c.value === bgColor)
    return preset?.hex || '#FFFFFF'
  }

  // Crop adjuster handlers
  const handleShowCropAdjuster = () => {
    if (!selectedFile) {
      setError('Please select a file first')
      return
    }
    setShowCropAdjuster(true)
  }

  const handleApplyCrop = (newCropData) => {
    setCropData(newCropData)
    setShowCropAdjuster(false)
  }

  const handleCancelCrop = () => {
    setShowCropAdjuster(false)
  }
  
  return (
    <div className="space-y-6">
      {/* Error Display */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3 error-shake">
          <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
          <span className="text-red-700">{error}</span>
          <button
            onClick={() => setError(null)}
            className="ml-auto text-red-500 hover:text-red-700"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      )}
      
      {/* Success Display */}
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 flex items-center space-x-3 success-bounce">
          <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
          <span className="text-green-700">Photo processed successfully!</span>
        </div>
      )}
      
      {/* File Upload Area */}
      {!selectedFile && (
        <div className="space-y-4">
          {/* Dropzone */}
          <div
            {...getRootProps()}
            className={`dropzone ${isDragActive ? 'dropzone-active' : ''} ${isDragReject ? 'dropzone-error' : ''}`}
          >
            <input {...getInputProps()} ref={fileInputRef} />
            <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">
              {isDragActive ? 'Drop your photo here' : 'Upload your photo'}
            </p>
            <p className="text-gray-600 mb-4">
              Drag and drop an image, or click to browse
            </p>
            <div className="flex flex-wrap justify-center gap-2 text-sm text-gray-500">
              <span>Supports:</span>
              <span className="bg-gray-100 px-2 py-1 rounded">JPG</span>
              <span className="bg-gray-100 px-2 py-1 rounded">PNG</span>
              <span className="bg-gray-100 px-2 py-1 rounded">WebP</span>
              <span className="text-gray-400">• Max 8MB</span>
            </div>
          </div>
          
          {/* Alternative Options */}
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => setShowWebcam(true)}
              className="btn btn-outline flex items-center space-x-2"
            >
              <Camera className="h-4 w-4" />
              <span>Use Webcam</span>
            </button>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="btn btn-primary flex items-center space-x-2"
            >
              <FileImage className="h-4 w-4" />
              <span>Browse Files</span>
            </button>
          </div>
        </div>
      )}
      
      {/* Webcam Modal */}
      {showWebcam && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-xl max-w-2xl w-full p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Take a Photo</h3>
              <button
                onClick={() => setShowWebcam(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="webcam-container mb-4">
              <Webcam
                ref={webcamRef}
                audio={false}
                screenshotFormat="image/jpeg"
                className="w-full rounded-lg"
                videoConstraints={{
                  width: 1280,
                  height: 720,
                  facingMode: "user"
                }}
              />
            </div>
            
            <div className="flex justify-center space-x-4">
              <button
                onClick={() => setShowWebcam(false)}
                className="btn btn-outline"
              >
                Cancel
              </button>
              <button
                onClick={captureWebcam}
                className="btn btn-primary flex items-center space-x-2"
              >
                <Camera className="h-4 w-4" />
                <span>Capture Photo</span>
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Selected File Preview */}
      {selectedFile && (
        <div className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Original Image */}
            <div className="card">
              <div className="card-header">
                <h4 className="font-semibold text-gray-900 flex items-center space-x-2">
                  <Eye className="h-4 w-4" />
                  <span>Original Photo</span>
                </h4>
                <p className="text-sm text-gray-600 mt-1">
                  {selectedFile.name} • {utils.formatFileSize(selectedFile.size)}
                </p>
              </div>
              
              <div className="card-content">
                <div className="image-preview relative">
                  <img
                    src={URL.createObjectURL(selectedFile)}
                    alt="Original"
                    className="w-full h-auto max-h-80 object-contain"
                  />
                  
                  {/* Face Detection Overlay */}
                  {detectedFaces.length > 0 && (
                    <div className="absolute inset-0">
                      {detectedFaces.map((detection, index) => {
                        const bbox = detection.boundingBox
                        return (
                          <div
                            key={index}
                            className="face-detection-box"
                            style={{
                              left: `${bbox.xCenter * 100 - (bbox.width * 100) / 2}%`,
                              top: `${bbox.yCenter * 100 - (bbox.height * 100) / 2}%`,
                              width: `${bbox.width * 100}%`,
                              height: `${bbox.height * 100}%`,
                            }}
                          />
                        )
                      })}
                    </div>
                  )}
                  
                  {/* Crop Indicator */}
                  {cropData && (
                    <div className="absolute top-2 right-2 bg-green-500 text-white px-2 py-1 rounded text-xs">
                      Custom Crop Applied
                    </div>
                  )}
                </div>
                
                {detectedFaces.length > 0 && (
                  <div className="mt-2 text-sm text-green-600 flex items-center space-x-1">
                    <CheckCircle className="h-4 w-4" />
                    <span>Face detected ({detectedFaces.length})</span>
                  </div>
                )}
              </div>
            </div>
            
            {/* Settings Panel */}
            <div className="card">
              <div className="card-header">
                <h4 className="font-semibold text-gray-900 flex items-center space-x-2">
                  <Settings className="h-4 w-4" />
                  <span>Processing Options</span>
                </h4>
              </div>
              
              <div className="card-content space-y-4">
                {/* Background Color */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Background Color
                  </label>
                  <div className="grid grid-cols-3 gap-2 mb-2">
                    {BACKGROUND_COLORS.map((color) => (
                      <button
                        key={color.value}
                        onClick={() => setBgColor(color.value)}
                        className={`color-option ${bgColor === color.value ? 'color-option-selected' : ''}`}
                        style={{ backgroundColor: color.hex }}
                        title={color.name}
                      />
                    ))}
                  </div>
                  
                  <button
                    onClick={() => setShowColorPicker(!showColorPicker)}
                    className="btn btn-outline btn-sm flex items-center space-x-2 w-full"
                  >
                    <Palette className="h-4 w-4" />
                    <span>Custom Color</span>
                  </button>
                  
                  {showColorPicker && (
                    <div className="mt-2">
                      <ChromePicker
                        color={customColor}
                        onChange={(color) => {
                          setCustomColor(color.hex)
                          setBgColor('custom')
                        }}
                        disableAlpha
                      />
                    </div>
                  )}
                </div>
                
                {/* A4 Sheet Option */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Layout className="h-4 w-4 text-gray-600" />
                    <span className="text-sm font-medium text-gray-700">Generate A4 Sheet</span>
                  </div>
                  <button
                    onClick={() => setMakeA4(!makeA4)}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      makeA4 ? 'bg-primary-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        makeA4 ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
                
                {/* Advanced Settings */}
                <div>
                  <button
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="btn btn-outline btn-sm w-full flex items-center justify-center space-x-2"
                  >
                    <Settings className="h-4 w-4" />
                    <span>Advanced Settings</span>
                  </button>
                  
                  {showAdvanced && (
                    <div className="mt-4 space-y-4 border-t pt-4">
                      {/* Face Scale */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Face Scale: {faceScale}
                        </label>
                        <input
                          type="range"
                          min="1.5"
                          max="3.0"
                          step="0.1"
                          value={faceScale}
                          onChange={(e) => setFaceScale(parseFloat(e.target.value))}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500">
                          <span>Tight</span>
                          <span>Loose</span>
                        </div>
                      </div>
                      
                      {/* Brightness */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Brightness: {brightness}
                        </label>
                        <input
                          type="range"
                          min="0.5"
                          max="1.5"
                          step="0.1"
                          value={brightness}
                          onChange={(e) => setBrightness(parseFloat(e.target.value))}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500">
                          <span>Dark</span>
                          <span>Bright</span>
                        </div>
                      </div>
                      
                      {/* Contrast */}
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                          Contrast: {contrast}
                        </label>
                        <input
                          type="range"
                          min="0.5"
                          max="1.5"
                          step="0.1"
                          value={contrast}
                          onChange={(e) => setContrast(parseFloat(e.target.value))}
                          className="w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-500">
                          <span>Low</span>
                          <span>High</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          {/* Process Button */}
          <div className="flex justify-center space-x-4">
            <button
              onClick={resetForm}
              className="btn btn-outline flex items-center space-x-2"
              disabled={processing}
            >
              <RefreshCw className="h-4 w-4" />
              <span>Reset</span>
            </button>
            
            <button
              onClick={handleShowCropAdjuster}
              disabled={!selectedFile || processing}
              className="btn btn-outline flex items-center space-x-2"
            >
              <Crop className="h-4 w-4" />
              <span>Adjust Crop</span>
            </button>
            
            <button
              onClick={processPhoto}
              disabled={processing}
              className="btn btn-primary flex items-center space-x-2 min-w-[200px]"
            >
              {processing ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <>
                  <Zap className="h-4 w-4" />
                  <span>Process Photo</span>
                </>
              )}
            </button>
          </div>
          
          {/* Processing Progress */}
          {processing && (
            <div className="space-y-2">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${processingProgress}%` }}
                />
              </div>
              <p className="text-center text-sm text-gray-600">
                {processingProgress < 30 && 'Detecting face...'}
                {processingProgress >= 30 && processingProgress < 60 && 'Removing background...'}
                {processingProgress >= 60 && processingProgress < 90 && 'Applying effects...'}
                {processingProgress >= 90 && 'Finalizing...'}
              </p>
            </div>
          )}
        </div>
      )}
      
      {/* Processed Result */}
      {processedResult && (
        <div className="card animate-fade-in">
          <div className="card-header">
            <h4 className="font-semibold text-gray-900 flex items-center space-x-2">
              <CheckCircle className="h-4 w-4 text-green-500" />
              <span>Processed Result</span>
            </h4>
            <p className="text-sm text-gray-600 mt-1">
              {processedResult.is_pdf ? 'A4 PDF Sheet' : 'Passport Photo'} • 
              {processedResult.format} • 
              {processedResult.size || '600×600'}
              {processedResult.dpi && ` @ ${processedResult.dpi} DPI`}
            </p>
          </div>
          
          <div className="card-content">
            {/* Preview */}
            <div className="text-center mb-6">
              {processedResult.is_pdf ? (
                <div className="bg-gray-100 rounded-lg p-8 inline-block">
                  <FileImage className="h-24 w-24 text-gray-400 mx-auto mb-2" />
                  <p className="text-gray-600">PDF Ready for Download</p>
                  {processedResult.copies && (
                    <p className="text-sm text-gray-500">{processedResult.copies} copies</p>
                  )}
                </div>
              ) : (
                <div className="inline-block">
                  <img
                    src={processedResult.file}
                    alt="Processed passport photo"
                    className="max-w-sm max-h-80 object-contain rounded-lg shadow-medium"
                    style={{ backgroundColor: getCurrentBgColor() }}
                  />
                </div>
              )}
            </div>
            
            {/* Download Button */}
            <div className="text-center">
              <button
                onClick={downloadResult}
                className="btn btn-success flex items-center space-x-2 mx-auto"
              >
                <Download className="h-4 w-4" />
                <span>
                  Download {processedResult.is_pdf ? 'A4 PDF' : 'PNG'}
                </span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Crop Adjuster Modal */}
      {showCropAdjuster && selectedFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-screen overflow-auto">
            <div className="p-6">
              <h3 className="text-xl font-semibold mb-4">Adjust Crop</h3>
              <CropAdjuster
                imageFile={selectedFile}
                detectedFaces={detectedFaces}
                onApply={handleApplyCrop}
                onCancel={handleCancelCrop}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}