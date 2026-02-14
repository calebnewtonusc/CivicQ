import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

interface City {
  id: number;
  name: string;
  state: string;
  status: string;
  primary_contact_email: string;
}

const CityPendingVerificationPage: React.FC = () => {
  const { cityId } = useParams<{ cityId: string }>();
  const navigate = useNavigate();

  const [city, setCity] = useState<City | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const getToken = () => localStorage.getItem('access_token');

  useEffect(() => {
    fetchCity();
    // Poll for status changes every 30 seconds
    const interval = setInterval(fetchCity, 30000);
    return () => clearInterval(interval);
  }, [cityId]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchCity = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/cities/${cityId}`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      const cityData = response.data;
      setCity(cityData);
      setLoading(false);

      // If verified, redirect to setup
      if (cityData.status === 'active') {
        navigate(`/city/${cityId}/setup`);
      }
    } catch (err: any) {
      console.error('Error fetching city:', err);
      setError(err.response?.data?.detail || 'Failed to load city');
      setLoading(false);
    }
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
          <button
            onClick={() => navigate('/')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-3xl mx-auto px-4">
        {/* Success Banner */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-8">
          <div className="flex items-center">
            <svg className="w-12 h-12 text-green-600 mr-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            <div>
              <h2 className="text-xl font-bold text-green-900 mb-1">
                Registration Successful!
              </h2>
              <p className="text-green-700">
                Thank you for registering {city.name}, {city.state}
              </p>
            </div>
          </div>
        </div>

        {/* Status Card */}
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <div className="text-6xl mb-4">⏳</div>

          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            Verification Pending
          </h1>

          <p className="text-lg text-gray-600 mb-6">
            Your city registration is under review by our team.
          </p>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8 text-left">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">
              What's Next?
            </h3>
            <ul className="space-y-3 text-blue-800">
              <li className="flex items-start">
                <span className="font-bold mr-2">1.</span>
                <span>
                  Our team will verify that you are an official representative of {city.name}, {city.state}
                </span>
              </li>
              <li className="flex items-start">
                <span className="font-bold mr-2">2.</span>
                <span>
                  We'll check your official email domain and documentation
                </span>
              </li>
              <li className="flex items-start">
                <span className="font-bold mr-2">3.</span>
                <span>
                  You'll receive an email at <strong>{city.primary_contact_email}</strong> once verified
                </span>
              </li>
              <li className="flex items-start">
                <span className="font-bold mr-2">4.</span>
                <span>
                  Then you can complete the setup wizard and launch your city portal!
                </span>
              </li>
            </ul>
          </div>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
            <p className="text-yellow-800 text-sm">
              <strong>Verification typically takes 24 hours.</strong> We'll review your application
              during business hours (Monday-Friday, 9am-5pm EST).
            </p>
          </div>

          <div className="border-t pt-6">
            <p className="text-gray-600 mb-4">
              Questions about your registration?
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="mailto:cities@civicq.org"
                className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Contact Support
              </a>
              <a
                href="https://docs.civicq.org/cities"
                target="_blank"
                rel="noopener noreferrer"
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                View Documentation
              </a>
            </div>
          </div>
        </div>

        {/* What to Prepare */}
        <div className="mt-8 bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            While You Wait: Prepare Your Data
          </h2>
          <p className="text-gray-600 mb-6">
            Get ready for a quick setup by gathering the following:
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">
                Ballot Information
              </h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Election date</li>
                <li>• List of contests (Mayor, Council, etc.)</li>
                <li>• Candidate names and contact info</li>
                <li>• Ballot measures (if any)</li>
              </ul>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">
                Branding Assets
              </h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• City logo (PNG or SVG)</li>
                <li>• Primary brand color (hex code)</li>
                <li>• Secondary brand color</li>
                <li>• City website URL</li>
              </ul>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">
                Team Members
              </h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Email addresses of colleagues</li>
                <li>• Their roles (Admin, Editor, etc.)</li>
                <li>• Who will moderate questions</li>
                <li>• Who will import ballots</li>
              </ul>
            </div>

            <div className="border border-gray-200 rounded-lg p-4">
              <h3 className="font-semibold text-gray-900 mb-2">
                Communication Plan
              </h3>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Social media announcement</li>
                <li>• Email to residents</li>
                <li>• City website banner</li>
                <li>• Press release (optional)</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Benefits Reminder */}
        <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 text-center">
            Why CivicQ?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-4xl mb-2">💬</div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Voter Engagement
              </h3>
              <p className="text-sm text-gray-600">
                Residents can ask questions and see what matters to their neighbors
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-2">📹</div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Video Answers
              </h3>
              <p className="text-sm text-gray-600">
                Candidates record video responses to top community questions
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-2">🗳️</div>
              <h3 className="font-semibold text-gray-900 mb-2">
                Informed Voting
              </h3>
              <p className="text-sm text-gray-600">
                Voters make informed decisions based on real candidate positions
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            This page will automatically update when your city is verified.
          </p>
          <button
            onClick={fetchCity}
            className="mt-2 text-blue-600 hover:text-blue-700 underline"
          >
            Check Status Now
          </button>
        </div>
      </div>
    </div>
  );
};

export default CityPendingVerificationPage;
