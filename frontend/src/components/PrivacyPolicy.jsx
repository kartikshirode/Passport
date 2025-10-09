import React, { useState } from 'react'
import { X, Shield, Eye, FileText, Clock, Globe, Lock } from 'lucide-react'

export default function PrivacyPolicy({ onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6 border-b pb-4">
            <div className="flex items-center space-x-3">
              <Shield className="h-6 w-6 text-blue-600" />
              <h2 className="text-2xl font-bold text-gray-900">Privacy Policy</h2>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="h-6 w-6" />
            </button>
          </div>

          {/* Content */}
          <div className="space-y-6 text-gray-700">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Lock className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold text-blue-900">Privacy First Approach</h3>
              </div>
              <p className="text-blue-800">
                Your privacy is our top priority. We process your photos in memory and never store them permanently. 
                All data is deleted immediately after processing.
              </p>
            </div>

            {/* Information We Collect */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                <Eye className="h-5 w-5" />
                <span>Information We Process</span>
              </h3>
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium">Images You Upload</h4>
                  <p>We temporarily process the photos you upload to create passport-sized images. These images are:</p>
                  <ul className="list-disc list-inside mt-2 space-y-1 ml-4">
                    <li>Processed entirely in server memory</li>
                    <li>Never written to permanent storage</li>
                    <li>Automatically deleted after processing</li>
                    <li>Not accessible to anyone except our processing algorithms</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium">Technical Information</h4>
                  <p>We may collect minimal technical data for service improvement:</p>
                  <ul className="list-disc list-inside mt-2 space-y-1 ml-4">
                    <li>IP address (for rate limiting and security)</li>
                    <li>Browser type and version</li>
                    <li>Processing time and success rates</li>
                    <li>Error logs (without personal data)</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* How We Use Information */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">How We Use Your Information</h3>
              <div className="space-y-2">
                <div className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                  <p><strong>Photo Processing:</strong> To detect faces, remove backgrounds, and create passport-sized images</p>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                  <p><strong>Service Improvement:</strong> To analyze processing performance and fix technical issues</p>
                </div>
                <div className="flex items-start space-x-2">
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0"></div>
                  <p><strong>Security:</strong> To prevent abuse and protect our services</p>
                </div>
              </div>
            </section>

            {/* Data Retention */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                <Clock className="h-5 w-5" />
                <span>Data Retention</span>
              </h3>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <h4 className="font-medium text-green-900 mb-2">Immediate Deletion Policy</h4>
                <ul className="space-y-1 text-green-800">
                  <li>• Original uploaded images: Deleted immediately after processing</li>
                  <li>• Processed passport photos: Available for download, then deleted</li>
                  <li>• Temporary processing data: Cleared from memory within seconds</li>
                  <li>• Technical logs: Anonymized and retained for 30 days maximum</li>
                </ul>
              </div>
            </section>

            {/* Data Sharing */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Data Sharing and Third Parties</h3>
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <h4 className="font-medium text-red-900 mb-2">We DO NOT Share Your Images</h4>
                <p className="text-red-800">
                  Your photos are never shared, sold, or transmitted to third parties. All processing 
                  happens on our secure servers. We do not use your images for training AI models or any other purpose.
                </p>
              </div>
              <div className="mt-4">
                <p>We may share anonymized technical data with service providers for:</p>
                <ul className="list-disc list-inside mt-2 space-y-1 ml-4">
                  <li>Hosting and infrastructure (Render, Vercel)</li>
                  <li>Error monitoring and performance analytics</li>
                  <li>Security and abuse prevention</li>
                </ul>
              </div>
            </section>

            {/* Your Rights */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Your Rights</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium">Right to Control</h4>
                  <ul className="text-sm space-y-1 mt-1">
                    <li>• Upload only the images you choose</li>
                    <li>• Download your processed photos</li>
                    <li>• Stop using the service at any time</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium">Right to Information</h4>
                  <ul className="text-sm space-y-1 mt-1">
                    <li>• Know how your data is processed</li>
                    <li>• Understand our security measures</li>
                    <li>• Contact us with questions</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* International Users */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                <Globe className="h-5 w-5" />
                <span>International Users & GDPR</span>
              </h3>
              <div className="space-y-3">
                <p>
                  This service is available globally. For users in the European Union, we comply with GDPR requirements:
                </p>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>Legal basis for processing: Legitimate interest in providing the service</li>
                  <li>Data processing location: Servers in the United States</li>
                  <li>Your right to request data deletion (though we don't store personal data)</li>
                  <li>Right to file complaints with your local data protection authority</li>
                </ul>
              </div>
            </section>

            {/* Security */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Security Measures</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium">Technical Safeguards</h4>
                  <ul className="text-sm space-y-1 mt-1">
                    <li>• HTTPS encryption for all communications</li>
                    <li>• Memory-only processing (no disk storage)</li>
                    <li>• Rate limiting to prevent abuse</li>
                    <li>• Content validation and filtering</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium">Operational Security</h4>
                  <ul className="text-sm space-y-1 mt-1">
                    <li>• Regular security updates</li>
                    <li>• Monitoring and logging</li>
                    <li>• Incident response procedures</li>
                    <li>• Limited access controls</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Updates */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Policy Updates</h3>
              <p>
                We may update this privacy policy to reflect changes in our practices or legal requirements. 
                Updates will be posted on this page with the effective date. We encourage you to review this 
                policy periodically.
              </p>
            </section>

            {/* Contact */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Contact Us</h3>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <p className="mb-2">If you have questions about this privacy policy or our data practices:</p>
                <ul className="space-y-1">
                  <li>• Email: privacy@passport-photo-app.com</li>
                  <li>• GitHub Issues: Open an issue on our repository</li>
                  <li>• Response time: We aim to respond within 48 hours</li>
                </ul>
              </div>
            </section>

            <div className="border-t pt-4 text-sm text-gray-500">
              <p>Last updated: October 9, 2024</p>
              <p>Effective date: October 9, 2024</p>
            </div>
          </div>

          {/* Footer */}
          <div className="flex justify-end space-x-4 mt-8 pt-4 border-t">
            <button
              onClick={onClose}
              className="btn btn-primary"
            >
              I Understand
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}