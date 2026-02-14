import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

interface TwoFactorSetupData {
  secret: string;
  qr_code: string;
  backup_codes: string[];
}

const TwoFactorSetupPage: React.FC = () => {
  const navigate = useNavigate();
  const [setupData, setSetupData] = useState<TwoFactorSetupData | null>(null);
  const [verificationCode, setVerificationCode] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'setup' | 'verify' | 'backup'>('setup');
  const [copiedCodes, setCopiedCodes] = useState(false);

  useEffect(() => {
    setup2FA();
  }, []);

  const setup2FA = async () => {
    try {
      const response = await api.post('/auth/2fa/setup');
      setSetupData(response.data);
      setIsLoading(false);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to setup 2FA');
      setIsLoading(false);
    }
  };

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsVerifying(true);

    try {
      await api.post('/auth/2fa/enable', {
        code: verificationCode,
        secret: setupData?.secret,
      });

      setStep('backup');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid verification code');
    } finally {
      setIsVerifying(false);
    }
  };

  const handleCopyBackupCodes = () => {
    if (setupData?.backup_codes) {
      const codesText = setupData.backup_codes.join('\n');
      navigator.clipboard.writeText(codesText);
      setCopiedCodes(true);
      setTimeout(() => setCopiedCodes(false), 2000);
    }
  };

  const handleFinish = () => {
    navigate('/settings', { state: { message: '2FA enabled successfully!' } });
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-indigo-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-gray-600">Setting up two-factor authentication...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Progress Indicator */}
          <div className="mb-8">
            <div className="flex items-center justify-between">
              <div className={`flex items-center ${step === 'setup' || step === 'verify' || step === 'backup' ? 'text-indigo-600' : 'text-gray-400'}`}>
                <div className={`h-10 w-10 rounded-full flex items-center justify-center ${step === 'setup' || step === 'verify' || step === 'backup' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}>
                  1
                </div>
                <span className="ml-2 font-medium">Scan QR Code</span>
              </div>
              <div className="flex-1 h-1 mx-4 bg-gray-200">
                <div className={`h-full ${step === 'verify' || step === 'backup' ? 'bg-indigo-600' : 'bg-gray-200'}`} />
              </div>
              <div className={`flex items-center ${step === 'verify' || step === 'backup' ? 'text-indigo-600' : 'text-gray-400'}`}>
                <div className={`h-10 w-10 rounded-full flex items-center justify-center ${step === 'verify' || step === 'backup' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}>
                  2
                </div>
                <span className="ml-2 font-medium">Verify</span>
              </div>
              <div className="flex-1 h-1 mx-4 bg-gray-200">
                <div className={`h-full ${step === 'backup' ? 'bg-indigo-600' : 'bg-gray-200'}`} />
              </div>
              <div className={`flex items-center ${step === 'backup' ? 'text-indigo-600' : 'text-gray-400'}`}>
                <div className={`h-10 w-10 rounded-full flex items-center justify-center ${step === 'backup' ? 'bg-indigo-600 text-white' : 'bg-gray-200'}`}>
                  3
                </div>
                <span className="ml-2 font-medium">Backup Codes</span>
              </div>
            </div>
          </div>

          {/* Step 1: Setup */}
          {step === 'setup' && setupData && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Setup Two-Factor Authentication
              </h2>
              <p className="text-gray-600 mb-6">
                Scan this QR code with your authenticator app (Google Authenticator, Authy, 1Password, etc.)
              </p>

              <div className="bg-gray-50 p-6 rounded-lg mb-6 text-center">
                <img
                  src={setupData.qr_code}
                  alt="2FA QR Code"
                  className="mx-auto mb-4"
                  style={{ maxWidth: '256px' }}
                />
                <p className="text-sm text-gray-600 mb-2">Can't scan? Enter this code manually:</p>
                <div className="bg-white border border-gray-300 rounded px-4 py-2 font-mono text-sm break-all">
                  {setupData.secret}
                </div>
              </div>

              <button
                onClick={() => setStep('verify')}
                className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
              >
                Continue to Verification
              </button>
            </div>
          )}

          {/* Step 2: Verify */}
          {step === 'verify' && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Verify Your Setup
              </h2>
              <p className="text-gray-600 mb-6">
                Enter the 6-digit code from your authenticator app to verify the setup.
              </p>

              {error && (
                <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded mb-6">
                  <div className="flex items-center">
                    <svg className="h-5 w-5 text-red-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <p className="text-sm text-red-700">{error}</p>
                  </div>
                </div>
              )}

              <form onSubmit={handleVerify} className="space-y-6">
                <div>
                  <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-2">
                    Verification Code
                  </label>
                  <input
                    id="code"
                    type="text"
                    required
                    maxLength={6}
                    value={verificationCode}
                    onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-center text-2xl font-mono tracking-widest"
                    placeholder="000000"
                    disabled={isVerifying}
                  />
                </div>

                <div className="flex space-x-4">
                  <button
                    type="button"
                    onClick={() => setStep('setup')}
                    className="flex-1 bg-gray-200 text-gray-700 py-3 px-4 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
                    disabled={isVerifying}
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={isVerifying || verificationCode.length !== 6}
                    className="flex-1 bg-indigo-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isVerifying ? 'Verifying...' : 'Verify & Enable 2FA'}
                  </button>
                </div>
              </form>
            </div>
          )}

          {/* Step 3: Backup Codes */}
          {step === 'backup' && setupData && (
            <div>
              <div className="text-center mb-6">
                <div className="mx-auto h-16 w-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                  <svg className="h-8 w-8 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  2FA Enabled Successfully!
                </h2>
                <p className="text-gray-600">
                  Save these backup codes in a secure location. Each code can be used once to access your account if you lose your authenticator device.
                </p>
              </div>

              <div className="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded mb-6">
                <div className="flex items-start">
                  <svg className="h-5 w-5 text-yellow-500 mt-0.5 mr-2" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <p className="text-sm text-yellow-700">
                    <strong>Important:</strong> Store these codes securely. You won't be able to see them again.
                  </p>
                </div>
              </div>

              <div className="bg-gray-50 border border-gray-300 rounded-lg p-6 mb-6">
                <div className="grid grid-cols-2 gap-3 font-mono text-sm">
                  {setupData.backup_codes.map((code, index) => (
                    <div key={index} className="bg-white border border-gray-200 rounded px-3 py-2 text-center">
                      {code}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex space-x-4">
                <button
                  onClick={handleCopyBackupCodes}
                  className="flex-1 bg-gray-200 text-gray-700 py-3 px-4 rounded-lg font-semibold hover:bg-gray-300 transition-colors flex items-center justify-center"
                >
                  {copiedCodes ? (
                    <>
                      <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      Copied!
                    </>
                  ) : (
                    <>
                      <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      Copy Codes
                    </>
                  )}
                </button>
                <button
                  onClick={handleFinish}
                  className="flex-1 bg-indigo-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-indigo-700 transition-colors"
                >
                  Finish
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TwoFactorSetupPage;
