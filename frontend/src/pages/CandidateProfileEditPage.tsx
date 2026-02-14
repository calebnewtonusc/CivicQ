import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layout } from '../components';
import { useAuthContext } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import SuccessMessage from '../components/SuccessMessage';

const API_BASE_URL = process.env.REACT_APP_API_URL || '${API_BASE_URL}';

// This interface is for internal use only
// eslint-disable-next-line @typescript-eslint/no-unused-vars
interface CandidateProfile {
  id: number;
  name: string;
  email: string;
  phone: string;
  website: string;
  photo_url: string;
  profile_fields: {
    bio?: string;
    education?: string;
    experience?: string;
    priorities?: string;
    endorsements?: string;
  };
}

export default function CandidateProfileEditPage() {
  const { user, isAuthenticated, isLoading: authLoading } = useAuthContext();
  const navigate = useNavigate();

  const [candidateId] = useState(1); // Replace with actual candidate ID
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    website: '',
    photo_url: '',
    bio: '',
    education: '',
    experience: '',
    priorities: '',
    endorsements: ''
  });

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login');
      return;
    }

    if (user && user.role !== 'candidate') {
      setError('You must be a candidate to access this page');
      return;
    }

    // Load current profile data
    loadProfile();
  }, [user, isAuthenticated, authLoading, navigate]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/candidates/${candidateId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load profile');
      }

      const data = await response.json();

      setFormData({
        name: data.name || '',
        email: data.email || '',
        phone: data.phone || '',
        website: data.website || '',
        photo_url: data.photo_url || '',
        bio: data.profile_fields?.bio || '',
        education: data.profile_fields?.education || '',
        experience: data.profile_fields?.experience || '',
        priorities: data.profile_fields?.priorities || '',
        endorsements: data.profile_fields?.endorsements || ''
      });
    } catch (err) {
      console.error('Failed to load profile:', err);
      setError('Failed to load profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      setSaving(true);
      setError(null);
      setSuccess(null);

      const updateData = {
        name: formData.name,
        email: formData.email,
        phone: formData.phone,
        website: formData.website,
        photo_url: formData.photo_url,
        profile_fields: {
          bio: formData.bio,
          education: formData.education,
          experience: formData.experience,
          priorities: formData.priorities,
          endorsements: formData.endorsements
        }
      };

      const response = await fetch(`${API_BASE_URL}/candidates/${candidateId}/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify(updateData)
      });

      if (!response.ok) {
        throw new Error('Failed to update profile');
      }

      setSuccess('Profile updated successfully!');

      // Redirect to dashboard after 2 seconds
      setTimeout(() => {
        navigate('/candidate/dashboard');
      }, 2000);
    } catch (err) {
      console.error('Failed to update profile:', err);
      setError('Failed to update profile. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (authLoading || loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center min-h-[60vh]">
          <LoadingSpinner size="lg" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Edit Your Profile</h1>
          <p className="mt-2 text-gray-600">
            Update your profile information to help voters learn more about you.
          </p>
        </div>

        {error && <ErrorMessage message={error} className="mb-6" />}
        {success && <SuccessMessage message={success} className="mb-6" />}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Basic Information */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>

            <div className="grid grid-cols-1 gap-6">
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
                  required
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                    Phone
                  </label>
                  <input
                    type="tel"
                    id="phone"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="website" className="block text-sm font-medium text-gray-700 mb-2">
                  Website / Campaign URL
                </label>
                <input
                  type="url"
                  id="website"
                  name="website"
                  value={formData.website}
                  onChange={handleInputChange}
                  placeholder="https://www.example.com"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label htmlFor="photo_url" className="block text-sm font-medium text-gray-700 mb-2">
                  Profile Photo URL
                </label>
                <input
                  type="url"
                  id="photo_url"
                  name="photo_url"
                  value={formData.photo_url}
                  onChange={handleInputChange}
                  placeholder="https://www.example.com/photo.jpg"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-1 text-sm text-gray-500">
                  Provide a URL to your professional headshot photo
                </p>
              </div>
            </div>
          </div>

          {/* Profile Details */}
          <div className="bg-white shadow rounded-lg p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Profile Details</h2>

            <div className="space-y-6">
              <div>
                <label htmlFor="bio" className="block text-sm font-medium text-gray-700 mb-2">
                  Biography
                </label>
                <textarea
                  id="bio"
                  name="bio"
                  value={formData.bio}
                  onChange={handleInputChange}
                  rows={4}
                  placeholder="Tell voters about yourself, your background, and why you're running..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
                <p className="mt-1 text-sm text-gray-500">
                  {formData.bio.length} characters
                </p>
              </div>

              <div>
                <label htmlFor="education" className="block text-sm font-medium text-gray-700 mb-2">
                  Education
                </label>
                <textarea
                  id="education"
                  name="education"
                  value={formData.education}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder="List your educational background..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label htmlFor="experience" className="block text-sm font-medium text-gray-700 mb-2">
                  Professional Experience
                </label>
                <textarea
                  id="experience"
                  name="experience"
                  value={formData.experience}
                  onChange={handleInputChange}
                  rows={4}
                  placeholder="Describe your relevant work experience and community involvement..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label htmlFor="priorities" className="block text-sm font-medium text-gray-700 mb-2">
                  Campaign Priorities
                </label>
                <textarea
                  id="priorities"
                  name="priorities"
                  value={formData.priorities}
                  onChange={handleInputChange}
                  rows={4}
                  placeholder="What are your top 3-5 priorities if elected?"
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label htmlFor="endorsements" className="block text-sm font-medium text-gray-700 mb-2">
                  Endorsements
                </label>
                <textarea
                  id="endorsements"
                  name="endorsements"
                  value={formData.endorsements}
                  onChange={handleInputChange}
                  rows={3}
                  placeholder="List organizations or individuals who have endorsed your campaign..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/candidate/dashboard')}
              className="px-6 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {saving ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </button>
          </div>
        </form>

        {/* Privacy Notice */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h3 className="text-sm font-medium text-blue-800 mb-2">Privacy Note</h3>
          <p className="text-sm text-blue-700">
            All information you provide here will be publicly visible to voters. Only include information
            you're comfortable sharing publicly as part of your campaign.
          </p>
        </div>
      </div>
    </Layout>
  );
}
