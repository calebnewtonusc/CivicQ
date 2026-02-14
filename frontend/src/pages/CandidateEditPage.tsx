import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useQuery } from '@tantml:invoke>react-query';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import LoadingSpinner from '../components/LoadingSpinner';
import api from '../api/axios';
import {
  UserIcon,
  BuildingOfficeIcon,
  GlobeAltIcon,
  EnvelopeIcon,
  PhoneIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

export default function CandidateEditPage() {
  const { candidateId } = useParams<{ candidateId: string }>();
  const navigate = useNavigate();
  const [isSaving, setIsSaving] = useState(false);

  const { data: candidate, isLoading } = useQuery({
    queryKey: ['candidate', candidateId],
    queryFn: async () => {
      const response = await api.get(`/candidates/${candidateId}`);
      return response.data;
    }
  });

  const [formData, setFormData] = useState({
    full_name: candidate?.full_name || '',
    party: candidate?.party || '',
    bio: candidate?.bio || '',
    website: candidate?.website || '',
    email: candidate?.email || '',
    phone: candidate?.phone || '',
    facebook_url: candidate?.facebook_url || '',
    twitter_url: candidate?.twitter_url || '',
    instagram_url: candidate?.instagram_url || '',
    linkedin_url: candidate?.linkedin_url || '',
    campaign_platform: candidate?.campaign_platform || '',
    education: candidate?.education || '',
    experience: candidate?.experience || '',
    endorsements: candidate?.endorsements || ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      await api.put(`/candidates/${candidateId}`, formData);
      navigate(`/candidate/${candidateId}`);
    } catch (error) {
      console.error('Failed to update candidate profile:', error);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>Edit Profile - {candidate?.full_name} - CivicQ</title>
        <meta name="description" content="Edit candidate profile" />
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        <Navbar />

        <main className="pt-16">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Header */}
            <div className="mb-8">
              <nav className="text-sm text-gray-600 mb-4">
                <Link to={`/candidate/${candidateId}`} className="hover:text-blue-600">
                  {candidate?.full_name}
                </Link>
                <span className="mx-2">→</span>
                <span className="text-gray-900">Edit Profile</span>
              </nav>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 flex items-center gap-3">
                <UserIcon className="h-10 w-10 text-blue-600" />
                Edit Candidate Profile
              </h1>
              <p className="text-gray-600 mt-2">
                Update your public profile information
              </p>
            </div>

            {/* Form */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <form onSubmit={handleSubmit}>
                {/* Basic Information */}
                <div className="p-8 border-b border-gray-200">
                  <h2 className="text-xl font-bold text-gray-900 mb-6">Basic Information</h2>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Full Name <span className="text-red-500">*</span>
                      </label>
                      <input
                        type="text"
                        name="full_name"
                        required
                        value={formData.full_name}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Party Affiliation
                      </label>
                      <select
                        name="party"
                        value={formData.party}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="">Select party</option>
                        <option value="Democratic">Democratic</option>
                        <option value="Republican">Republican>
                        <option value="Independent">Independent</option>
                        <option value="Libertarian">Libertarian</option>
                        <option value="Green">Green</option>
                        <option value="Other">Other</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Bio
                      </label>
                      <textarea
                        name="bio"
                        value={formData.bio}
                        onChange={handleChange}
                        rows={4}
                        placeholder="Tell voters about yourself..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      />
                    </div>
                  </div>
                </div>

                {/* Contact Information */}
                <div className="p-8 border-b border-gray-200">
                  <h2 className="text-xl font-bold text-gray-900 mb-6">Contact Information</h2>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <EnvelopeIcon className="h-4 w-4 inline mr-1" />
                        Email
                      </label>
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="campaign@example.com"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <PhoneIcon className="h-4 w-4 inline mr-1" />
                        Phone
                      </label>
                      <input
                        type="tel"
                        name="phone"
                        value={formData.phone}
                        onChange={handleChange}
                        placeholder="(555) 123-4567"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        <GlobeAltIcon className="h-4 w-4 inline mr-1" />
                        Campaign Website
                      </label>
                      <input
                        type="url"
                        name="website"
                        value={formData.website}
                        onChange={handleChange}
                        placeholder="https://votejohndoe.com"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                {/* Social Media */}
                <div className="p-8 border-b border-gray-200">
                  <h2 className="text-xl font-bold text-gray-900 mb-6">Social Media</h2>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Facebook
                      </label>
                      <input
                        type="url"
                        name="facebook_url"
                        value={formData.facebook_url}
                        onChange={handleChange}
                        placeholder="https://facebook.com/..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Twitter / X
                      </label>
                      <input
                        type="url"
                        name="twitter_url"
                        value={formData.twitter_url}
                        onChange={handleChange}
                        placeholder="https://twitter.com/..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Instagram
                      </label>
                      <input
                        type="url"
                        name="instagram_url"
                        value={formData.instagram_url}
                        onChange={handleChange}
                        placeholder="https://instagram.com/..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        LinkedIn
                      </label>
                      <input
                        type="url"
                        name="linkedin_url"
                        value={formData.linkedin_url}
                        onChange={handleChange}
                        placeholder="https://linkedin.com/in/..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      />
                    </div>
                  </div>
                </div>

                {/* Campaign Details */}
                <div className="p-8 border-b border-gray-200">
                  <h2 className="text-xl font-bold text-gray-900 mb-6">Campaign Details</h2>
                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Campaign Platform
                      </label>
                      <textarea
                        name="campaign_platform"
                        value={formData.campaign_platform}
                        onChange={handleChange}
                        rows={6}
                        placeholder="Describe your key campaign priorities and policy positions..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Education
                      </label>
                      <textarea
                        name="education"
                        value={formData.education}
                        onChange={handleChange}
                        rows={3}
                        placeholder="List your educational background..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Professional Experience
                      </label>
                      <textarea
                        name="experience"
                        value={formData.experience}
                        onChange={handleChange}
                        rows={4}
                        placeholder="Describe your professional and community experience..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Endorsements
                      </label>
                      <textarea
                        name="endorsements"
                        value={formData.endorsements}
                        onChange={handleChange}
                        rows={3}
                        placeholder="List organizations and individuals who have endorsed your campaign..."
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      />
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="p-8 bg-gray-50 flex gap-3">
                  <button
                    type="submit"
                    disabled={isSaving}
                    className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    <CheckCircleIcon className="h-5 w-5" />
                    {isSaving ? 'Saving...' : 'Save Changes'}
                  </button>
                  <Link
                    to={`/candidate/${candidateId}`}
                    className="flex items-center gap-2 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                  >
                    <XCircleIcon className="h-5 w-5" />
                    Cancel
                  </Link>
                </div>
              </form>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
}
