import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { Link, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/axios';
import {
  UserIcon,
  EnvelopeIcon,
  MapPinIcon,
  CalendarIcon,
  PencilIcon,
  CheckCircleIcon,
  XCircleIcon,
  ShieldCheckIcon,
  BellIcon,
  KeyIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    full_name: user?.full_name || '',
    location: user?.location || '',
    bio: user?.bio || ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);

    try {
      await api.put('/users/me', formData);
      setIsEditing(false);
      // TODO: Update user context with new data
    } catch (error) {
      console.error('Failed to update profile:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setFormData({
      username: user?.username || '',
      email: user?.email || '',
      full_name: user?.full_name || '',
      location: user?.location || '',
      bio: user?.bio || ''
    });
    setIsEditing(false);
  };

  if (!user) {
    navigate('/login');
    return null;
  }

  return (
    <>
      <Helmet>
        <title>My Profile - CivicQ</title>
        <meta name="description" content="View and edit your CivicQ profile" />
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        <Navbar />

        <main className="pt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="grid lg:grid-cols-3 gap-8">
              {/* Left Sidebar - Navigation */}
              <div className="lg:col-span-1">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                  <div className="p-6 border-b border-gray-200">
                    <div className="flex items-center gap-4">
                      <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                        <UserIcon className="h-8 w-8 text-blue-600" />
                      </div>
                      <div>
                        <h2 className="text-xl font-bold text-gray-900">{user.username}</h2>
                        <p className="text-sm text-gray-600">{user.email}</p>
                      </div>
                    </div>
                  </div>

                  <nav className="p-4">
                    <Link
                      to="/profile"
                      className="flex items-center gap-3 px-4 py-3 bg-blue-50 text-blue-700 rounded-lg font-medium mb-2"
                    >
                      <UserIcon className="h-5 w-5" />
                      Profile
                    </Link>
                    <Link
                      to="/my-questions"
                      className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg font-medium mb-2"
                    >
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                      </svg>
                      My Questions
                    </Link>
                    <button
                      className="w-full flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg font-medium mb-2"
                      disabled
                    >
                      <BellIcon className="h-5 w-5" />
                      Notifications
                      <span className="ml-auto text-xs text-gray-400">Soon</span>
                    </button>
                    <button
                      className="w-full flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg font-medium mb-2"
                      disabled
                    >
                      <ShieldCheckIcon className="h-5 w-5" />
                      Privacy
                      <span className="ml-auto text-xs text-gray-400">Soon</span>
                    </button>
                    <button
                      className="w-full flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg font-medium"
                      disabled
                    >
                      <KeyIcon className="h-5 w-5" />
                      Security
                      <span className="ml-auto text-xs text-gray-400">Soon</span>
                    </button>
                  </nav>

                  <div className="p-4 border-t border-gray-200">
                    <button
                      onClick={logout}
                      className="w-full px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg font-medium transition-colors"
                    >
                      Sign Out
                    </button>
                  </div>
                </div>
              </div>

              {/* Main Content */}
              <div className="lg:col-span-2">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                  <div className="p-6 border-b border-gray-200 flex items-center justify-between">
                    <h1 className="text-2xl font-bold text-gray-900">Profile Information</h1>
                    {!isEditing && (
                      <button
                        onClick={() => setIsEditing(true)}
                        className="flex items-center gap-2 px-4 py-2 text-blue-600 hover:bg-blue-50 rounded-lg font-medium transition-colors"
                      >
                        <PencilIcon className="h-5 w-5" />
                        Edit Profile
                      </button>
                    )}
                  </div>

                  <div className="p-6">
                    {isEditing ? (
                      <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                          <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
                            Username
                          </label>
                          <input
                            type="text"
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>

                        <div>
                          <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                            Email Address
                          </label>
                          <input
                            type="email"
                            id="email"
                            name="email"
                            value={formData.email}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>

                        <div>
                          <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
                            Full Name
                          </label>
                          <input
                            type="text"
                            id="full_name"
                            name="full_name"
                            value={formData.full_name}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>

                        <div>
                          <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
                            Location
                          </label>
                          <input
                            type="text"
                            id="location"
                            name="location"
                            value={formData.location}
                            onChange={handleChange}
                            placeholder="City, State"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>

                        <div>
                          <label htmlFor="bio" className="block text-sm font-medium text-gray-700 mb-2">
                            Bio
                          </label>
                          <textarea
                            id="bio"
                            name="bio"
                            value={formData.bio}
                            onChange={handleChange}
                            rows={4}
                            placeholder="Tell us a bit about yourself..."
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                          />
                        </div>

                        <div className="flex gap-3">
                          <button
                            type="submit"
                            disabled={isSaving}
                            className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          >
                            <CheckCircleIcon className="h-5 w-5" />
                            {isSaving ? 'Saving...' : 'Save Changes'}
                          </button>
                          <button
                            type="button"
                            onClick={handleCancel}
                            disabled={isSaving}
                            className="flex items-center gap-2 px-6 py-2 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                          >
                            <XCircleIcon className="h-5 w-5" />
                            Cancel
                          </button>
                        </div>
                      </form>
                    ) : (
                      <div className="space-y-6">
                        <div className="grid md:grid-cols-2 gap-6">
                          <div>
                            <label className="block text-sm font-medium text-gray-500 mb-1">Username</label>
                            <div className="flex items-center gap-2 text-gray-900">
                              <UserIcon className="h-5 w-5 text-gray-400" />
                              {user.username}
                            </div>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-500 mb-1">Email</label>
                            <div className="flex items-center gap-2 text-gray-900">
                              <EnvelopeIcon className="h-5 w-5 text-gray-400" />
                              {user.email}
                            </div>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-500 mb-1">Full Name</label>
                            <div className="text-gray-900">
                              {user.full_name || <span className="text-gray-400 italic">Not set</span>}
                            </div>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-500 mb-1">Location</label>
                            <div className="flex items-center gap-2 text-gray-900">
                              <MapPinIcon className="h-5 w-5 text-gray-400" />
                              {user.location || <span className="text-gray-400 italic">Not set</span>}
                            </div>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-500 mb-1">Member Since</label>
                            <div className="flex items-center gap-2 text-gray-900">
                              <CalendarIcon className="h-5 w-5 text-gray-400" />
                              {new Date(user.created_at).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: 'long',
                                day: 'numeric'
                              })}
                            </div>
                          </div>

                          <div>
                            <label className="block text-sm font-medium text-gray-500 mb-1">Account Status</label>
                            <div className="flex items-center gap-2">
                              <CheckCircleIcon className="h-5 w-5 text-green-600" />
                              <span className="text-green-600 font-medium">Active</span>
                            </div>
                          </div>
                        </div>

                        {user.bio && (
                          <div>
                            <label className="block text-sm font-medium text-gray-500 mb-1">Bio</label>
                            <p className="text-gray-900">{user.bio}</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                {/* Account Stats */}
                <div className="mt-6 grid md:grid-cols-3 gap-6">
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="text-3xl font-bold text-blue-600 mb-1">
                      {user.question_count || 0}
                    </div>
                    <div className="text-sm text-gray-600">Questions Asked</div>
                  </div>
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="text-3xl font-bold text-green-600 mb-1">
                      {user.answer_count || 0}
                    </div>
                    <div className="text-sm text-gray-600">Answers Received</div>
                  </div>
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <div className="text-3xl font-bold text-purple-600 mb-1">
                      {user.vote_count || 0}
                    </div>
                    <div className="text-sm text-gray-600">Ballots Viewed</div>
                  </div>
                </div>

                {/* Danger Zone */}
                <div className="mt-6 bg-white rounded-lg shadow-sm border border-red-200 overflow-hidden">
                  <div className="p-6 border-b border-red-200 bg-red-50">
                    <h2 className="text-lg font-bold text-red-900 flex items-center gap-2">
                      <TrashIcon className="h-5 w-5" />
                      Danger Zone
                    </h2>
                  </div>
                  <div className="p-6">
                    <p className="text-gray-600 mb-4">
                      Once you delete your account, there is no going back. Your questions and activity will be anonymized.
                    </p>
                    <button
                      disabled
                      className="px-6 py-2 bg-red-600 text-white rounded-lg font-medium opacity-50 cursor-not-allowed"
                    >
                      Delete Account (Coming Soon)
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
}
