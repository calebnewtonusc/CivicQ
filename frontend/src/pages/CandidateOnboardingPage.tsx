import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';

type OnboardingStep = 'welcome' | 'verify' | 'profile' | 'complete';

export default function CandidateOnboardingPage() {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState<OnboardingStep>('welcome');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    filingId: '',
    name: '',
    email: '',
    phone: '',
    website: '',
    bio: '',
    agreeToTerms: false
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value, type } = e.target;
    const checked = type === 'checkbox' ? (e.target as HTMLInputElement).checked : undefined;

    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleNextStep = async () => {
    setError(null);

    switch (currentStep) {
      case 'welcome':
        setCurrentStep('verify');
        break;

      case 'verify':
        if (!formData.filingId) {
          setError('Please enter your candidate filing ID');
          return;
        }
        // In production, verify the filing ID
        setLoading(true);
        setTimeout(() => {
          setLoading(false);
          setCurrentStep('profile');
        }, 1500);
        break;

      case 'profile':
        if (!formData.name || !formData.email) {
          setError('Please complete all required fields');
          return;
        }
        if (!formData.agreeToTerms) {
          setError('Please agree to the terms and conditions');
          return;
        }
        setLoading(true);
        setTimeout(() => {
          setLoading(false);
          setCurrentStep('complete');
        }, 1500);
        break;

      case 'complete':
        navigate('/candidate/dashboard');
        break;
    }
  };

  const renderWelcomeStep = () => (
    <div className="text-center">
      <div className="mx-auto h-24 w-24 bg-blue-100 rounded-full flex items-center justify-center mb-6">
        <svg className="h-12 w-12 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
        </svg>
      </div>

      <h2 className="text-3xl font-bold text-gray-900 mb-4">
        Welcome to CivicQ!
      </h2>

      <p className="text-lg text-gray-600 mb-6">
        Thank you for joining our platform. CivicQ helps you connect directly with voters
        through structured, transparent Q&A.
      </p>

      <div className="bg-blue-50 rounded-lg p-6 mb-8 text-left">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">What to Expect:</h3>
        <ul className="space-y-3 text-gray-700">
          <li className="flex items-start">
            <svg className="h-6 w-6 text-blue-600 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>View questions voters are asking in your race</span>
          </li>
          <li className="flex items-start">
            <svg className="h-6 w-6 text-blue-600 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Record video answers directly in your browser</span>
          </li>
          <li className="flex items-start">
            <svg className="h-6 w-6 text-blue-600 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Build trust through authentic, unedited responses</span>
          </li>
          <li className="flex items-start">
            <svg className="h-6 w-6 text-blue-600 mr-3 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>Equal visibility with all other candidates - no pay-to-win</span>
          </li>
        </ul>
      </div>

      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-8 text-left">
        <div className="flex">
          <svg className="h-5 w-5 text-yellow-400 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
          <div>
            <p className="text-sm font-medium text-yellow-800">
              Important: All video answers are permanent and cannot be edited
            </p>
            <p className="text-sm text-yellow-700 mt-1">
              This ensures authenticity and builds voter trust in the platform.
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderVerifyStep = () => (
    <div>
      <div className="text-center mb-8">
        <div className="mx-auto h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
          <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Verify Your Candidacy</h2>
        <p className="text-gray-600">
          We need to verify that you're an official candidate for this race
        </p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow">
        <div className="mb-6">
          <label htmlFor="filingId" className="block text-sm font-medium text-gray-700 mb-2">
            Candidate Filing ID *
          </label>
          <input
            type="text"
            id="filingId"
            name="filingId"
            value={formData.filingId}
            onChange={handleInputChange}
            placeholder="Enter your official filing ID"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
          <p className="mt-2 text-sm text-gray-500">
            This is the ID assigned when you filed to run for office. Contact your elections office if you need help finding it.
          </p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Why do we verify?</h4>
          <p className="text-sm text-gray-600">
            Verification ensures that only legitimate candidates can answer questions and post content.
            This protects voters from impersonation and maintains platform integrity.
          </p>
        </div>
      </div>
    </div>
  );

  const renderProfileStep = () => (
    <div>
      <div className="text-center mb-8">
        <div className="mx-auto h-16 w-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
          <svg className="h-8 w-8 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Complete Your Profile</h2>
        <p className="text-gray-600">
          Help voters learn more about you
        </p>
      </div>

      <div className="bg-white p-6 rounded-lg shadow space-y-6">
        <div>
          <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
            Full Name *
          </label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            placeholder="Your full name as it appears on the ballot"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
            Email Address *
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            placeholder="your.email@example.com"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
            Phone Number
          </label>
          <input
            type="tel"
            id="phone"
            name="phone"
            value={formData.phone}
            onChange={handleInputChange}
            placeholder="(555) 123-4567"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label htmlFor="website" className="block text-sm font-medium text-gray-700 mb-2">
            Campaign Website
          </label>
          <input
            type="url"
            id="website"
            name="website"
            value={formData.website}
            onChange={handleInputChange}
            placeholder="https://www.yoursite.com"
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div>
          <label htmlFor="bio" className="block text-sm font-medium text-gray-700 mb-2">
            Brief Bio
          </label>
          <textarea
            id="bio"
            name="bio"
            value={formData.bio}
            onChange={handleInputChange}
            rows={4}
            placeholder="Tell voters about yourself in a few sentences..."
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <div className="flex items-start">
          <div className="flex items-center h-5">
            <input
              type="checkbox"
              id="agreeToTerms"
              name="agreeToTerms"
              checked={formData.agreeToTerms}
              onChange={handleInputChange}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
          </div>
          <div className="ml-3">
            <label htmlFor="agreeToTerms" className="text-sm text-gray-700">
              I agree to the CivicQ <a href="#" className="text-blue-600 hover:text-blue-500">Terms of Service</a> and{' '}
              <a href="#" className="text-blue-600 hover:text-blue-500">Community Guidelines</a>. I understand that all video
              answers are permanent and publicly visible.
            </label>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCompleteStep = () => (
    <div className="text-center">
      <div className="mx-auto h-24 w-24 bg-green-100 rounded-full flex items-center justify-center mb-6">
        <svg className="h-12 w-12 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>

      <h2 className="text-3xl font-bold text-gray-900 mb-4">
        You're All Set!
      </h2>

      <p className="text-lg text-gray-600 mb-8">
        Your candidate account is ready. Let's start answering voter questions!
      </p>

      <div className="bg-blue-50 rounded-lg p-6 mb-8 text-left">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Next Steps:</h3>
        <ol className="space-y-3 text-gray-700 list-decimal list-inside">
          <li>Review the questions voters are asking in your race</li>
          <li>Start recording video answers to top-ranked questions</li>
          <li>Complete your full profile to help voters learn about you</li>
          <li>Check back regularly for new questions from your community</li>
        </ol>
      </div>

      <div className="bg-green-50 border-l-4 border-green-400 p-4 text-left">
        <div className="flex">
          <svg className="h-5 w-5 text-green-400 mr-3 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
          <div>
            <p className="text-sm font-medium text-green-800">
              Tip: Candidates who answer questions early often see higher voter engagement
            </p>
            <p className="text-sm text-green-700 mt-1">
              Start building trust with voters by being one of the first to respond!
            </p>
          </div>
        </div>
      </div>
    </div>
  );

  const steps = [
    { key: 'welcome', label: 'Welcome' },
    { key: 'verify', label: 'Verify' },
    { key: 'profile', label: 'Profile' },
    { key: 'complete', label: 'Complete' }
  ];

  const currentStepIndex = steps.findIndex(s => s.key === currentStep);

  return (
    <Layout>
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Progress Bar */}
        <div className="mb-12">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <React.Fragment key={step.key}>
                <div className="flex flex-col items-center">
                  <div
                    className={`h-10 w-10 rounded-full flex items-center justify-center ${
                      index <= currentStepIndex
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-500'
                    }`}
                  >
                    {index < currentStepIndex ? (
                      <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      <span>{index + 1}</span>
                    )}
                  </div>
                  <span className="text-xs mt-2 font-medium text-gray-600">{step.label}</span>
                </div>
                {index < steps.length - 1 && (
                  <div
                    className={`flex-1 h-1 mx-4 ${
                      index < currentStepIndex ? 'bg-blue-600' : 'bg-gray-200'
                    }`}
                  />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Content */}
        <div className="mb-8">
          {error && <ErrorMessage message={error} className="mb-6" />}

          {currentStep === 'welcome' && renderWelcomeStep()}
          {currentStep === 'verify' && renderVerifyStep()}
          {currentStep === 'profile' && renderProfileStep()}
          {currentStep === 'complete' && renderCompleteStep()}
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between items-center">
          {currentStep !== 'welcome' && currentStep !== 'complete' && (
            <button
              onClick={() => {
                const prevIndex = Math.max(0, currentStepIndex - 1);
                setCurrentStep(steps[prevIndex].key as OnboardingStep);
              }}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Back
            </button>
          )}

          <button
            onClick={handleNextStep}
            disabled={loading}
            className={`px-8 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center ${
              currentStep === 'welcome' || currentStep === 'complete' ? 'ml-auto' : ''
            }`}
          >
            {loading ? (
              <>
                <LoadingSpinner size="small" className="mr-2" />
                Processing...
              </>
            ) : currentStep === 'complete' ? (
              'Go to Dashboard'
            ) : (
              'Continue'
            )}
          </button>
        </div>
      </div>
    </Layout>
  );
}
