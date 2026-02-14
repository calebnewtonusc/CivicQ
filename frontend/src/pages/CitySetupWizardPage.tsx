import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

interface City {
  id: number;
  name: string;
  slug: string;
  state: string;
  status: string;
  onboarding_step: number;
  onboarding_completed: boolean;
  next_election_date: string | null;
  logo_url: string | null;
  primary_color: string | null;
  secondary_color: string | null;
}

const CitySetupWizardPage: React.FC = () => {
  const { cityId } = useParams<{ cityId: string }>();

  const [city, setCity] = useState<City | null>(null);
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Get auth token
  const getToken = () => localStorage.getItem('access_token');

  useEffect(() => {
    fetchCity();
  }, [cityId]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchCity = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/cities/${cityId}`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      setCity(response.data);
      setCurrentStep(response.data.onboarding_step || 1);
      setLoading(false);
    } catch (err: any) {
      console.error('Error fetching city:', err);
      setError(err.response?.data?.detail || 'Failed to load city data');
      setLoading(false);
    }
  };

  const handleStepComplete = (nextStep: number) => {
    setCurrentStep(nextStep);
    fetchCity(); // Refresh city data
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (error || !city) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-md p-8 max-w-md">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
          <p className="text-gray-700">{error || 'City not found'}</p>
        </div>
      </div>
    );
  }

  const steps = [
    { number: 1, title: 'Verification Pending', icon: '⏳' },
    { number: 2, title: 'Import Ballot Data', icon: '🗳️' },
    { number: 3, title: 'Customize Branding', icon: '🎨' },
    { number: 4, title: 'Invite Staff', icon: '👥' },
    { number: 5, title: 'Review & Launch', icon: '🚀' },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Setup Wizard: {city.name}
          </h1>
          <p className="text-gray-600">
            Let's get your city live on CivicQ
          </p>
        </div>

        {/* Progress Steps */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <React.Fragment key={step.number}>
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl mb-2 ${
                      currentStep > step.number
                        ? 'bg-green-500 text-white'
                        : currentStep === step.number
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-500'
                    }`}
                  >
                    {currentStep > step.number ? '✓' : step.icon}
                  </div>
                  <p className={`text-sm text-center ${
                    currentStep === step.number ? 'font-semibold text-blue-600' : 'text-gray-600'
                  }`}>
                    {step.title}
                  </p>
                </div>
                {index < steps.length - 1 && (
                  <div className={`flex-1 h-1 mx-2 ${
                    currentStep > step.number ? 'bg-green-500' : 'bg-gray-200'
                  }`} />
                )}
              </React.Fragment>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-md p-8">
          {currentStep === 1 && <VerificationPendingStep city={city} />}
          {currentStep === 2 && <BallotImportStep city={city} onComplete={() => handleStepComplete(3)} />}
          {currentStep === 3 && <BrandingStep city={city} onComplete={() => handleStepComplete(4)} />}
          {currentStep === 4 && <InviteStaffStep city={city} onComplete={() => handleStepComplete(5)} />}
          {currentStep === 5 && <ReviewLaunchStep city={city} />}
        </div>
      </div>
    </div>
  );
};

// Step 1: Verification Pending
const VerificationPendingStep: React.FC<{ city: City }> = ({ city }) => {
  return (
    <div className="text-center py-8">
      <div className="text-6xl mb-4">⏳</div>
      <h2 className="text-2xl font-bold text-gray-900 mb-4">
        Verification Pending
      </h2>
      <p className="text-gray-600 mb-6 max-w-2xl mx-auto">
        Thank you for registering! Our team is reviewing your application.
        You'll receive an email once your city is verified (usually within 24 hours).
      </p>
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 max-w-2xl mx-auto">
        <p className="text-yellow-800 text-sm">
          <strong>What happens next?</strong> Our team will verify that you are an official
          representative of {city.name}, {city.state}. Once verified, you'll be able to
          import your ballot data and launch your city portal.
        </p>
      </div>
    </div>
  );
};

// Step 2: Ballot Import (continuing in next part due to length...)
const BallotImportStep: React.FC<{ city: City; onComplete: () => void }> = ({ city, onComplete }) => {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Import Ballot Data</h2>
      <p className="text-gray-600">
        Import your election ballot data to get started. You can do this manually or via API.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Manual Import */}
        <div className="border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Manual Entry
          </h3>
          <p className="text-gray-600 mb-4">
            Manually enter your ballot contests and candidates
          </p>
          <button
            onClick={() => navigate(`/city/${city.id}/import/manual`)}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Start Manual Entry
          </button>
        </div>

        {/* API Import */}
        <div className="border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            API Import
          </h3>
          <p className="text-gray-600 mb-4">
            Import from VotingWorks, Democracy Works, or custom API
          </p>
          <button
            onClick={() => navigate(`/city/${city.id}/import/api`)}
            className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700"
          >
            Configure API Import
          </button>
        </div>
      </div>

      <div className="pt-6 border-t">
        <button
          onClick={onComplete}
          className="px-6 py-2 text-blue-600 hover:text-blue-700"
        >
          Skip for now →
        </button>
      </div>
    </div>
  );
};

// Step 3: Branding
const BrandingStep: React.FC<{ city: City; onComplete: () => void }> = ({ city, onComplete }) => {
  const [logoUrl, setLogoUrl] = useState(city.logo_url || '');
  const [primaryColor, setPrimaryColor] = useState(city.primary_color || '#3B82F6');
  const [secondaryColor, setSecondaryColor] = useState(city.secondary_color || '#1E40AF');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getToken = () => localStorage.getItem('access_token');

  const handleSave = async () => {
    setSaving(true);
    setError(null);

    try {
      await axios.put(
        `${API_BASE_URL}/cities/${city.id}/branding`,
        {
          logo_url: logoUrl || null,
          primary_color: primaryColor,
          secondary_color: secondaryColor,
        },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      onComplete();
    } catch (err: any) {
      console.error('Error saving branding:', err);
      setError(err.response?.data?.detail || 'Failed to save branding');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Customize Your Branding</h2>
      <p className="text-gray-600">
        Add your city's logo and colors to personalize the voter experience
      </p>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Logo URL
          </label>
          <input
            type="url"
            value={logoUrl}
            onChange={(e) => setLogoUrl(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="https://example.com/logo.png"
          />
          <p className="text-sm text-gray-500 mt-1">
            Upload your logo to a hosting service and paste the URL here
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Primary Color
            </label>
            <div className="flex space-x-2">
              <input
                type="color"
                value={primaryColor}
                onChange={(e) => setPrimaryColor(e.target.value)}
                className="h-10 w-20 border border-gray-300 rounded cursor-pointer"
              />
              <input
                type="text"
                value={primaryColor}
                onChange={(e) => setPrimaryColor(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="#3B82F6"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Secondary Color
            </label>
            <div className="flex space-x-2">
              <input
                type="color"
                value={secondaryColor}
                onChange={(e) => setSecondaryColor(e.target.value)}
                className="h-10 w-20 border border-gray-300 rounded cursor-pointer"
              />
              <input
                type="text"
                value={secondaryColor}
                onChange={(e) => setSecondaryColor(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="#1E40AF"
              />
            </div>
          </div>
        </div>

        {/* Preview */}
        <div className="border border-gray-300 rounded-lg p-6" style={{ backgroundColor: primaryColor + '10' }}>
          <h3 className="text-lg font-semibold mb-2" style={{ color: primaryColor }}>
            Preview
          </h3>
          <p className="text-gray-700 mb-4">
            This is how your city's branding will appear to voters
          </p>
          <button
            style={{ backgroundColor: primaryColor, color: 'white' }}
            className="px-4 py-2 rounded-md font-semibold"
          >
            Sample Button
          </button>
        </div>
      </div>

      <div className="flex justify-between pt-6 border-t">
        <button
          onClick={onComplete}
          className="px-6 py-2 text-gray-600 hover:text-gray-700"
        >
          Skip for now
        </button>
        <button
          onClick={handleSave}
          disabled={saving}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {saving ? 'Saving...' : 'Save & Continue'}
        </button>
      </div>
    </div>
  );
};

// Step 4: Invite Staff
const InviteStaffStep: React.FC<{ city: City; onComplete: () => void }> = ({ city, onComplete }) => {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('viewer');
  const [inviting, setInviting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const getToken = () => localStorage.getItem('access_token');

  const handleInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    setInviting(true);
    setError(null);
    setSuccess(false);

    try {
      await axios.post(
        `${API_BASE_URL}/cities/${city.id}/staff/invite`,
        { email, role },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      setSuccess(true);
      setEmail('');
    } catch (err: any) {
      console.error('Error inviting staff:', err);
      setError(err.response?.data?.detail || 'Failed to send invitation');
    } finally {
      setInviting(false);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Invite City Staff</h2>
      <p className="text-gray-600">
        Invite colleagues to help manage your city's CivicQ portal
      </p>

      <form onSubmit={handleInvite} className="space-y-4">
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
            Invitation sent successfully!
          </div>
        )}

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email Address
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="colleague@example.com"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Role
          </label>
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="viewer">Viewer - Read-only access</option>
            <option value="moderator">Moderator - Can moderate questions</option>
            <option value="editor">Editor - Can edit ballots and content</option>
            <option value="admin">Admin - Full administrative access</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={inviting}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400"
        >
          {inviting ? 'Sending...' : 'Send Invitation'}
        </button>
      </form>

      <div className="flex justify-between pt-6 border-t">
        <button
          onClick={onComplete}
          className="px-6 py-2 text-blue-600 hover:text-blue-700"
        >
          Skip for now →
        </button>
      </div>
    </div>
  );
};

// Step 5: Review & Launch
const ReviewLaunchStep: React.FC<{ city: City }> = ({ city }) => {
  const navigate = useNavigate();
  const [launching, setLaunching] = useState(false);

  const getToken = () => localStorage.getItem('access_token');

  const handleLaunch = async () => {
    setLaunching(true);
    try {
      await axios.post(
        `${API_BASE_URL}/cities/${city.id}/complete-onboarding`,
        {},
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      navigate(`/city/${city.id}/dashboard`);
    } catch (err) {
      console.error('Error completing onboarding:', err);
      alert('Failed to complete onboarding');
    } finally {
      setLaunching(false);
    }
  };

  return (
    <div className="space-y-6 text-center py-8">
      <div className="text-6xl mb-4">🚀</div>
      <h2 className="text-3xl font-bold text-gray-900">
        You're All Set!
      </h2>
      <p className="text-lg text-gray-600 max-w-2xl mx-auto">
        Your city is ready to launch on CivicQ. Click the button below to complete setup
        and start engaging with your voters!
      </p>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 max-w-2xl mx-auto">
        <h3 className="text-lg font-semibold text-blue-900 mb-4">
          Next Steps
        </h3>
        <ul className="text-left space-y-2 text-blue-800">
          <li className="flex items-start">
            <span className="mr-2">✓</span>
            <span>Access your city dashboard to manage ballots and questions</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">✓</span>
            <span>Share your city's CivicQ URL with voters</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">✓</span>
            <span>Monitor voter engagement and question activity</span>
          </li>
          <li className="flex items-start">
            <span className="mr-2">✓</span>
            <span>Invite candidates to answer voter questions</span>
          </li>
        </ul>
      </div>

      <button
        onClick={handleLaunch}
        disabled={launching}
        className="px-8 py-4 bg-blue-600 text-white text-lg font-semibold rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
      >
        {launching ? 'Launching...' : 'Launch My City Portal'}
      </button>
    </div>
  );
};

export default CitySetupWizardPage;
