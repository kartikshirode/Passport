import React from 'react'
import { X, FileText, AlertTriangle, Shield, Users, Gavel } from 'lucide-react'

export default function TermsOfService({ onClose }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          {/* Header */}
          <div className="flex justify-between items-center mb-6 border-b pb-4">
            <div className="flex items-center space-x-3">
              <FileText className="h-6 w-6 text-blue-600" />
              <h2 className="text-2xl font-bold text-gray-900">Terms of Service</h2>
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
                <FileText className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold text-blue-900">Agreement to Terms</h3>
              </div>
              <p className="text-blue-800">
                By using our Passport Photo Processor service, you agree to these terms. 
                Please read them carefully before using our service.
              </p>
            </div>

            {/* Service Description */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Service Description</h3>
              <p className="mb-3">
                Passport Photo Processor is a web-based service that automatically processes portrait photographs 
                to create passport-sized images compliant with international standards, specifically Indian passport 
                photo requirements (51×51 mm, 600×600 pixels at 300 DPI).
              </p>
              <div>
                <h4 className="font-medium mb-2">Our service includes:</h4>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>Automatic face detection and centering</li>
                  <li>Background removal and replacement</li>
                  <li>Image resizing to passport specifications</li>
                  <li>A4 sheet generation for printing multiple copies</li>
                  <li>Various background color options</li>
                </ul>
              </div>
            </section>

            {/* Acceptable Use */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>Acceptable Use</span>
              </h3>
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium text-green-700 mb-2">✅ Permitted Uses</h4>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>Personal passport and ID photo creation</li>
                    <li>Official document applications</li>
                    <li>Visa and travel document preparation</li>
                    <li>Professional headshot processing</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium text-red-700 mb-2">❌ Prohibited Uses</h4>
                  <ul className="list-disc list-inside space-y-1 ml-4">
                    <li>Processing images of minors without parental consent</li>
                    <li>Uploading inappropriate, offensive, or illegal content</li>
                    <li>Creating fake or fraudulent identification documents</li>
                    <li>Circumventing rate limits or automated attacks</li>
                    <li>Reverse engineering or attempting to extract our algorithms</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* User Responsibilities */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">User Responsibilities</h3>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                <div className="flex items-center space-x-2 mb-2">
                  <AlertTriangle className="h-5 w-5 text-yellow-600" />
                  <h4 className="font-medium text-yellow-900">Important Requirements</h4>
                </div>
                <p className="text-yellow-800">
                  You are responsible for ensuring that your uploaded images comply with the passport 
                  photo requirements of your destination country and intended use.
                </p>
              </div>
              <div>
                <h4 className="font-medium mb-2">You agree to:</h4>
                <ul className="list-disc list-inside space-y-1 ml-4">
                  <li>Only upload images you have the right to use</li>
                  <li>Ensure uploaded content is appropriate and legal</li>
                  <li>Verify that processed photos meet your specific requirements</li>
                  <li>Not attempt to abuse or overload our service</li>
                  <li>Respect intellectual property rights</li>
                </ul>
              </div>
            </section>

            {/* Image Rights and Ownership */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Image Rights and Ownership</h3>
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium">Your Images</h4>
                  <p>
                    You retain full ownership and rights to all images you upload. We do not claim any 
                    ownership rights to your content.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">Processing License</h4>
                  <p>
                    By uploading images, you grant us a temporary, limited license to process your images 
                    solely for the purpose of providing our service. This license expires immediately 
                    after processing is complete.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">Processed Results</h4>
                  <p>
                    The processed passport photos remain your property. We do not retain copies or 
                    use them for any other purpose.
                  </p>
                </div>
              </div>
            </section>

            {/* Service Limitations */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Service Limitations</h3>
              <div className="grid md:grid-cols-2 gap-4">
                <div>
                  <h4 className="font-medium">Technical Limits</h4>
                  <ul className="text-sm space-y-1 mt-1">
                    <li>• Maximum file size: 8MB per image</li>
                    <li>• Supported formats: JPG, PNG, WebP, BMP</li>
                    <li>• Rate limit: 10 requests per minute</li>
                    <li>• Processing timeout: 30 seconds</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-medium">Quality Considerations</h4>
                  <ul className="text-sm space-y-1 mt-1">
                    <li>• Results depend on input image quality</li>
                    <li>• Face detection requires clear, frontal photos</li>
                    <li>• Background removal works best with contrasting backgrounds</li>
                    <li>• Manual review may be needed for official use</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Disclaimers */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                <Shield className="h-5 w-5" />
                <span>Disclaimers and Warranties</span>
              </h3>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <h4 className="font-medium mb-2">"As Is" Service</h4>
                <p className="text-sm mb-3">
                  Our service is provided "as is" without warranties of any kind. While we strive for accuracy, 
                  we cannot guarantee that processed photos will meet all official requirements.
                </p>
                <div className="space-y-2 text-sm">
                  <div>
                    <strong>No Guarantee of Acceptance:</strong> We cannot guarantee that processed photos 
                    will be accepted by passport offices, visa authorities, or other official bodies.
                  </div>
                  <div>
                    <strong>User Verification Required:</strong> Users must verify that processed photos 
                    meet their specific requirements before official submission.
                  </div>
                  <div>
                    <strong>Technology Limitations:</strong> AI-based processing may not work perfectly 
                    with all images or lighting conditions.
                  </div>
                </div>
              </div>
            </section>

            {/* Liability */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center space-x-2">
                <Gavel className="h-5 w-5" />
                <span>Limitation of Liability</span>
              </h3>
              <div className="space-y-3">
                <p>
                  To the maximum extent permitted by law, we shall not be liable for any indirect, 
                  incidental, special, consequential, or punitive damages arising from your use of our service.
                </p>
                <div>
                  <h4 className="font-medium">Specific Limitations</h4>
                  <ul className="list-disc list-inside space-y-1 ml-4 text-sm">
                    <li>Rejection of processed photos by official authorities</li>
                    <li>Delays or costs resulting from photo rejection</li>
                    <li>Loss of data or processing errors</li>
                    <li>Service interruptions or downtime</li>
                    <li>Any damages exceeding the amount you paid for the service (free service = $0)</li>
                  </ul>
                </div>
              </div>
            </section>

            {/* Privacy */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Privacy and Data Protection</h3>
              <p>
                Your privacy is important to us. Our data handling practices are detailed in our Privacy Policy. 
                Key points:
              </p>
              <ul className="list-disc list-inside space-y-1 ml-4 mt-2">
                <li>Images are processed in memory and deleted immediately</li>
                <li>No permanent storage of your photos</li>
                <li>Minimal technical data collection for service improvement</li>
                <li>Compliance with applicable privacy laws</li>
              </ul>
            </section>

            {/* Service Changes */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Service Changes and Termination</h3>
              <div className="space-y-3">
                <div>
                  <h4 className="font-medium">Service Modifications</h4>
                  <p>
                    We may modify, suspend, or discontinue our service at any time without prior notice. 
                    We may also update these terms as needed.
                  </p>
                </div>
                <div>
                  <h4 className="font-medium">Account Termination</h4>
                  <p>
                    We may terminate or restrict access to our service for users who violate these terms 
                    or engage in prohibited activities.
                  </p>
                </div>
              </div>
            </section>

            {/* Governing Law */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Governing Law</h3>
              <p>
                These terms are governed by the laws of the jurisdiction where our service is operated. 
                Any disputes will be resolved through appropriate legal channels in that jurisdiction.
              </p>
            </section>

            {/* Contact */}
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Contact Information</h3>
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                <p className="mb-2">For questions about these terms or our service:</p>
                <ul className="space-y-1">
                  <li>• Email: support@passport-photo-app.com</li>
                  <li>• GitHub: Open an issue on our repository</li>
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
              className="btn btn-outline"
            >
              Close
            </button>
            <button
              onClick={onClose}
              className="btn btn-primary"
            >
              I Agree
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}