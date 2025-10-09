import React, { useState, useEffect } from 'react'
import ImageUploader from './components/ImageUploader'
import PrivacyPolicy from './components/PrivacyPolicy'
import TermsOfService from './components/TermsOfService'
import { Camera, Download, Sparkles, Shield, Zap } from 'lucide-react'

function App() {
  const [darkMode, setDarkMode] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [showPrivacyPolicy, setShowPrivacyPolicy] = useState(false)
  const [showTerms, setShowTerms] = useState(false)

  useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => setIsLoading(false), 1000)
    return () => clearTimeout(timer)
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <div className="spinner w-12 h-12 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Passport Photo Processor...</p>
        </div>
      </div>
    )
  }

  return (
    <div className={`min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 ${darkMode ? 'dark' : ''}`}>
      {/* Header */}
      <header className="bg-white shadow-soft">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 p-2 rounded-lg">
                <Camera className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Passport Photo Processor</h1>
                <p className="text-sm text-gray-600">Professional quality, instant results</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 transition-colors"
                aria-label="Toggle dark mode"
              >
                {darkMode ? '☀️' : '🌙'}
              </button>
              <a
                href="https://github.com/your-repo"
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-outline text-sm"
              >
                View Source
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              Create Perfect{' '}
              <span className="text-gradient-primary">Passport Photos</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Upload your photo and get professional passport-sized images with automatic face detection, 
              background removal, and print-ready A4 sheets. Perfect for visa applications, ID cards, and official documents.
            </p>
            
            {/* Features */}
            <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto mb-12">
              <div className="card text-center">
                <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Sparkles className="h-6 w-6 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">AI-Powered Processing</h3>
                <p className="text-gray-600 text-sm">
                  Advanced face detection and background removal using state-of-the-art machine learning models
                </p>
              </div>
              
              <div className="card text-center">
                <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Zap className="h-6 w-6 text-green-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Lightning Fast</h3>
                <p className="text-gray-600 text-sm">
                  Process photos in under 3 seconds with optimized ONNX models and client-side preprocessing
                </p>
              </div>
              
              <div className="card text-center">
                <div className="bg-purple-100 w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Shield className="h-6 w-6 text-purple-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Privacy First</h3>
                <p className="text-gray-600 text-sm">
                  Your photos are processed securely and never stored. Complete privacy and data protection
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Application */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        <div className="card">
          <div className="card-header">
            <h3 className="text-xl font-semibold text-gray-900">Upload Your Photo</h3>
            <p className="text-gray-600 mt-2">
              Choose a clear, front-facing photo with good lighting. We'll handle the rest!
            </p>
          </div>
          
          <div className="card-content">
            <ImageUploader />
          </div>
        </div>
      </main>

      {/* Instructions Section */}
      <section className="bg-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">How It Works</h3>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Follow these simple steps to create professional passport photos
            </p>
          </div>
          
          <div className="grid md:grid-cols-4 gap-8">
            {[
              {
                step: '1',
                title: 'Upload Photo',
                description: 'Choose a clear photo from your device or take one with your webcam',
                icon: '📷'
              },
              {
                step: '2',
                title: 'AI Processing',
                description: 'Our AI detects your face, removes background, and centers the image perfectly',
                icon: '🤖'
              },
              {
                step: '3',
                title: 'Customize',
                description: 'Choose background color and adjust settings to meet your requirements',
                icon: '🎨'
              },
              {
                step: '4',
                title: 'Download',
                description: 'Get your passport photo or A4 sheet ready for printing',
                icon: '📥'
              }
            ].map((item, index) => (
              <div key={index} className="text-center">
                <div className="bg-blue-600 text-white w-12 h-12 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-4">
                  {item.step}
                </div>
                <div className="text-4xl mb-4">{item.icon}</div>
                <h4 className="font-semibold text-gray-900 mb-2">{item.title}</h4>
                <p className="text-gray-600 text-sm">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tips Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">Photo Tips</h3>
            <p className="text-gray-600">Get the best results with these guidelines</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                title: 'Good Lighting',
                description: 'Use natural light or well-lit indoor lighting. Avoid harsh shadows on your face.',
                emoji: '💡'
              },
              {
                title: 'Face Forward',
                description: 'Look directly at the camera with a neutral expression. Keep your head straight.',
                emoji: '👤'
              },
              {
                title: 'Plain Background',
                description: 'Any background works - we\'ll remove it automatically and replace with your chosen color.',
                emoji: '🖼️'
              },
              {
                title: 'Clear Image',
                description: 'Use a high-resolution image for best results. Avoid blurry or pixelated photos.',
                emoji: '📸'
              },
              {
                title: 'No Accessories',
                description: 'Remove hats, sunglasses, or anything that obscures your face unless required.',
                emoji: '👓'
              },
              {
                title: 'Proper Distance',
                description: 'Position yourself so your head and shoulders are visible in the frame.',
                emoji: '📏'
              }
            ].map((tip, index) => (
              <div key={index} className="card text-center">
                <div className="text-3xl mb-4">{tip.emoji}</div>
                <h4 className="font-semibold text-gray-900 mb-2">{tip.title}</h4>
                <p className="text-gray-600 text-sm">{tip.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <div className="bg-blue-600 p-2 rounded-lg">
                  <Camera className="h-6 w-6" />
                </div>
                <span className="text-xl font-bold">Passport Photo Processor</span>
              </div>
              <p className="text-gray-400 mb-4">
                Professional passport photo processing with AI-powered face detection and background removal. 
                Fast, secure, and compliant with international standards.
              </p>
              <div className="flex space-x-4">
                <button 
                  onClick={() => setShowPrivacyPolicy(true)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  Privacy
                </button>
                <button 
                  onClick={() => setShowTerms(true)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  Terms
                </button>
                <a href="mailto:support@passport-photo-app.com" className="text-gray-400 hover:text-white transition-colors">Support</a>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Features</h4>
              <ul className="space-y-2 text-gray-400">
                <li>Face Detection</li>
                <li>Background Removal</li>
                <li>A4 Print Sheets</li>
                <li>Multiple Formats</li>
                <li>Instant Processing</li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Specifications</h4>
              <ul className="space-y-2 text-gray-400">
                <li>600×600px @ 300 DPI</li>
                <li>Indian Passport Standard</li>
                <li>Multiple Background Colors</li>
                <li>Print-Ready Quality</li>
                <li>PDF Export</li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 pt-8 mt-8 text-center text-gray-400">
            <p>&copy; 2024 Passport Photo Processor. Built with React, FastAPI, and AI.</p>
          </div>
        </div>
      </footer>

      {/* Modals */}
      {showPrivacyPolicy && (
        <PrivacyPolicy onClose={() => setShowPrivacyPolicy(false)} />
      )}
      
      {showTerms && (
        <TermsOfService onClose={() => setShowTerms(false)} />
      )}
    </div>
  )
}

export default App