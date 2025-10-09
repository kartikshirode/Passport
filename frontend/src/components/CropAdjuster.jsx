import React, { useState, useRef, useEffect } from 'react'
import { Move, RotateCw, ZoomIn, ZoomOut, Square, Check, X } from 'lucide-react'

export default function CropAdjuster({ 
  imageFile, 
  detectedFaces, 
  onCropChange, 
  onApply, 
  onCancel 
}) {
  const canvasRef = useRef(null)
  const [image, setImage] = useState(null)
  const [cropArea, setCropArea] = useState({ x: 0, y: 0, width: 300, height: 300 })
  const [scale, setScale] = useState(1)
  const [rotation, setRotation] = useState(0)
  const [isDragging, setIsDragging] = useState(false)
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 })
  const [imageLoaded, setImageLoaded] = useState(false)

  // Load image when component mounts
  useEffect(() => {
    if (imageFile) {
      const img = new Image()
      img.onload = () => {
        setImage(img)
        setImageLoaded(true)
        
        // Initialize crop area based on detected face or center
        if (detectedFaces && detectedFaces.length > 0) {
          const face = detectedFaces[0] // Use first detected face
          const faceX = face.boundingBox.xCenter * img.width - (face.boundingBox.width * img.width) / 2
          const faceY = face.boundingBox.yCenter * img.height - (face.boundingBox.height * img.height) / 2
          const faceSize = Math.max(face.boundingBox.width, face.boundingBox.height) * img.width * 2.2
          
          setCropArea({
            x: Math.max(0, faceX - faceSize / 2),
            y: Math.max(0, faceY - faceSize / 2),
            width: Math.min(faceSize, img.width),
            height: Math.min(faceSize, img.height)
          })
        } else {
          // Center crop if no face detected
          const size = Math.min(img.width, img.height) * 0.8
          setCropArea({
            x: (img.width - size) / 2,
            y: (img.height - size) / 2,
            width: size,
            height: size
          })
        }
      }
      img.src = URL.createObjectURL(imageFile)
    }
  }, [imageFile, detectedFaces])

  // Draw canvas
  useEffect(() => {
    if (image && imageLoaded && canvasRef.current) {
      const canvas = canvasRef.current
      const ctx = canvas.getContext('2d')
      
      // Set canvas size
      const containerWidth = 600
      const containerHeight = 400
      canvas.width = containerWidth
      canvas.height = containerHeight
      
      // Calculate image display size
      const imageAspect = image.width / image.height
      const containerAspect = containerWidth / containerHeight
      
      let displayWidth, displayHeight, offsetX, offsetY
      
      if (imageAspect > containerAspect) {
        displayWidth = containerWidth * scale
        displayHeight = (containerWidth / imageAspect) * scale
        offsetX = (containerWidth - displayWidth) / 2
        offsetY = (containerHeight - displayHeight) / 2
      } else {
        displayWidth = (containerHeight * imageAspect) * scale
        displayHeight = containerHeight * scale
        offsetX = (containerWidth - displayWidth) / 2
        offsetY = (containerHeight - displayHeight) / 2
      }
      
      // Clear canvas
      ctx.clearRect(0, 0, containerWidth, containerHeight)
      
      // Save context for rotation
      ctx.save()
      ctx.translate(containerWidth / 2, containerHeight / 2)
      ctx.rotate((rotation * Math.PI) / 180)
      ctx.translate(-containerWidth / 2, -containerHeight / 2)
      
      // Draw image
      ctx.drawImage(image, offsetX, offsetY, displayWidth, displayHeight)
      
      // Restore context
      ctx.restore()
      
      // Draw crop overlay
      drawCropOverlay(ctx, containerWidth, containerHeight, displayWidth, displayHeight, offsetX, offsetY)
    }
  }, [image, imageLoaded, cropArea, scale, rotation])

  const drawCropOverlay = (ctx, canvasWidth, canvasHeight, imgWidth, imgHeight, imgX, imgY) => {
    // Calculate crop area position on canvas
    const scaleX = imgWidth / image.width
    const scaleY = imgHeight / image.height
    const cropX = imgX + (cropArea.x * scaleX)
    const cropY = imgY + (cropArea.y * scaleY)
    const cropWidth = cropArea.width * scaleX
    const cropHeight = cropArea.height * scaleY
    
    // Draw semi-transparent overlay
    ctx.fillStyle = 'rgba(0, 0, 0, 0.5)'
    ctx.fillRect(0, 0, canvasWidth, canvasHeight)
    
    // Clear crop area
    ctx.clearRect(cropX, cropY, cropWidth, cropHeight)
    
    // Draw crop border
    ctx.strokeStyle = '#22c55e'
    ctx.lineWidth = 2
    ctx.strokeRect(cropX, cropY, cropWidth, cropHeight)
    
    // Draw corner handles
    const handleSize = 8
    ctx.fillStyle = '#22c55e'
    
    // Top-left
    ctx.fillRect(cropX - handleSize/2, cropY - handleSize/2, handleSize, handleSize)
    // Top-right
    ctx.fillRect(cropX + cropWidth - handleSize/2, cropY - handleSize/2, handleSize, handleSize)
    // Bottom-left
    ctx.fillRect(cropX - handleSize/2, cropY + cropHeight - handleSize/2, handleSize, handleSize)
    // Bottom-right
    ctx.fillRect(cropX + cropWidth - handleSize/2, cropY + cropHeight - handleSize/2, handleSize, handleSize)
    
    // Draw center point
    ctx.fillStyle = '#ffffff'
    ctx.fillRect(cropX + cropWidth/2 - 2, cropY + cropHeight/2 - 2, 4, 4)
    
    // Draw rule of thirds grid
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)'
    ctx.lineWidth = 1
    
    // Vertical lines
    ctx.beginPath()
    ctx.moveTo(cropX + cropWidth/3, cropY)
    ctx.lineTo(cropX + cropWidth/3, cropY + cropHeight)
    ctx.moveTo(cropX + (2*cropWidth)/3, cropY)
    ctx.lineTo(cropX + (2*cropWidth)/3, cropY + cropHeight)
    ctx.stroke()
    
    // Horizontal lines
    ctx.beginPath()
    ctx.moveTo(cropX, cropY + cropHeight/3)
    ctx.lineTo(cropX + cropWidth, cropY + cropHeight/3)
    ctx.moveTo(cropX, cropY + (2*cropHeight)/3)
    ctx.lineTo(cropX + cropWidth, cropY + (2*cropHeight)/3)
    ctx.stroke()
  }

  const handleMouseDown = (e) => {
    setIsDragging(true)
    const rect = canvasRef.current.getBoundingClientRect()
    setDragStart({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    })
  }

  const handleMouseMove = (e) => {
    if (!isDragging) return
    
    const rect = canvasRef.current.getBoundingClientRect()
    const currentX = e.clientX - rect.left
    const currentY = e.clientY - rect.top
    
    const deltaX = currentX - dragStart.x
    const deltaY = currentY - dragStart.y
    
    // Update crop area position
    setCropArea(prev => ({
      ...prev,
      x: Math.max(0, Math.min(image.width - prev.width, prev.x + deltaX / scale)),
      y: Math.max(0, Math.min(image.height - prev.height, prev.y + deltaY / scale))
    }))
    
    setDragStart({ x: currentX, y: currentY })
  }

  const handleMouseUp = () => {
    setIsDragging(false)
  }

  const handleScaleChange = (newScale) => {
    setScale(Math.max(0.5, Math.min(3, newScale)))
  }

  const handleRotation = (angle) => {
    setRotation((prev) => (prev + angle) % 360)
  }

  const resetCrop = () => {
    if (detectedFaces && detectedFaces.length > 0) {
      const face = detectedFaces[0]
      const faceX = face.boundingBox.xCenter * image.width - (face.boundingBox.width * image.width) / 2
      const faceY = face.boundingBox.yCenter * image.height - (face.boundingBox.height * image.height) / 2
      const faceSize = Math.max(face.boundingBox.width, face.boundingBox.height) * image.width * 2.2
      
      setCropArea({
        x: Math.max(0, faceX - faceSize / 2),
        y: Math.max(0, faceY - faceSize / 2),
        width: Math.min(faceSize, image.width),
        height: Math.min(faceSize, image.height)
      })
    } else {
      const size = Math.min(image.width, image.height) * 0.8
      setCropArea({
        x: (image.width - size) / 2,
        y: (image.height - size) / 2,
        width: size,
        height: size
      })
    }
    setScale(1)
    setRotation(0)
  }

  const applyCrop = () => {
    const cropData = {
      x: Math.round(cropArea.x),
      y: Math.round(cropArea.y),
      width: Math.round(cropArea.width),
      height: Math.round(cropArea.height),
      scale,
      rotation
    }
    onApply(cropData)
  }

  if (!imageLoaded) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-100 rounded-lg">
        <div className="text-center">
          <div className="spinner w-8 h-8 mx-auto mb-2"></div>
          <p className="text-gray-600">Loading image...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Canvas */}
      <div className="relative bg-gray-900 rounded-lg overflow-hidden">
        <canvas
          ref={canvasRef}
          className="cursor-move"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        />
        
        {/* Canvas overlay instructions */}
        <div className="absolute top-4 left-4 bg-black bg-opacity-70 text-white px-3 py-2 rounded text-sm">
          Drag to reposition • Use controls below to adjust
        </div>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Scale Controls */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Zoom</label>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleScaleChange(scale - 0.1)}
              className="p-2 border border-gray-300 rounded hover:bg-gray-50"
            >
              <ZoomOut className="h-4 w-4" />
            </button>
            <span className="text-sm font-mono min-w-[4ch] text-center">
              {scale.toFixed(1)}x
            </span>
            <button
              onClick={() => handleScaleChange(scale + 0.1)}
              className="p-2 border border-gray-300 rounded hover:bg-gray-50"
            >
              <ZoomIn className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Rotation Controls */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Rotation</label>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => handleRotation(-90)}
              className="p-2 border border-gray-300 rounded hover:bg-gray-50"
            >
              <RotateCw className="h-4 w-4 transform rotate-180" />
            </button>
            <span className="text-sm font-mono min-w-[4ch] text-center">
              {rotation}°
            </span>
            <button
              onClick={() => handleRotation(90)}
              className="p-2 border border-gray-300 rounded hover:bg-gray-50"
            >
              <RotateCw className="h-4 w-4" />
            </button>
          </div>
        </div>

        {/* Crop Size */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Crop Size</label>
          <div className="flex items-center space-x-2">
            <Square className="h-4 w-4 text-gray-400" />
            <span className="text-sm">
              {Math.round(cropArea.width)} × {Math.round(cropArea.height)}
            </span>
          </div>
        </div>

        {/* Reset */}
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700">Reset</label>
          <button
            onClick={resetCrop}
            className="w-full p-2 border border-gray-300 rounded hover:bg-gray-50 text-sm"
          >
            Reset Crop
          </button>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end space-x-4 pt-4 border-t">
        <button
          onClick={onCancel}
          className="btn btn-outline flex items-center space-x-2"
        >
          <X className="h-4 w-4" />
          <span>Cancel</span>
        </button>
        <button
          onClick={applyCrop}
          className="btn btn-primary flex items-center space-x-2"
        >
          <Check className="h-4 w-4" />
          <span>Apply Crop</span>
        </button>
      </div>
    </div>
  )
}