import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import LoadingSpinner from '../components/LoadingSpinner';
import api from '../api/axios';
import {
  Cog6ToothIcon,
  BellIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  DocumentTextIcon,
  CheckCircleIcon,
  XCircleIcon,
  EnvelopeIcon,
  GlobeAltIcon
} from '@heroicons/react/24/outline';

export default function CitySettingsPage() {
  const { cityId } = useParams<{ cityId: string }>();
  const [activeTab, setActiveTab] = useState<'general' | 'staff' | 'moderation' | 'notifications'>('general');
  const [isSaving, setIsSaving] = useState(false);

  const { data: city, isLoading } = useQuery({
    queryKey: ['city', cityId],
    queryFn: async () => {
      const response = await api.get(`/cities/${cityId}`);
      return response.data;
    }
  });

  const [generalSettings, setGeneralSettings] = useState({
    name: city?.name || '',
    state: city?.state || '',
    description: city?.description || '',
    website: city?.website || '',
    contact_email: city?.contact_email || '',
    timezone: city?.timezone || 'America/New_York'
  });

  const [moderationSettings, setModerationSettings] = useState({
    auto_approve_questions: false,
    require_candidate_verification: true,
    allow_anonymous_questions: false,
    profanity_filter_enabled: true
  });

  const [notificationSettings, setNotificationSettings] = useState({
    email_new_questions: true,
    email_new_candidates: true,
    email_flagged_content: true,
    email_daily_digest: false,
    email_weekly_report: true
  });

  const handleSaveGeneral = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await api.put(`/cities/${cityId}/settings`, generalSettings);
      // Show success message
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveModeration = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await api.put(`/cities/${cityId}/settings/moderation`, moderationSettings);
      // Show success message
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveNotifications = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    try {
      await api.put(`/cities/${cityId}/settings/notifications`, notificationSettings);
      // Show success message
    } catch (error) {
      console.error('Failed to save settings:', error);
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
        <title>City Settings - {city?.name} - CivicQ</title>
        <meta name="description" content={`Manage settings for ${city?.name}`} />
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        <Navbar />

        <main className="pt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Header */}
            <div className="mb-8">
              <nav className="text-sm text-gray-600 mb-4">
                <Link to={`/city/${cityId}/dashboard`} className="hover:text-blue-600">
                  Dashboard
                </Link>
                <span className="mx-2">→</span>
                <span className="text-gray-900">Settings</span>
              </nav>
              <h1 className="text-3xl md:text-4xl font-bold text-gray-900 flex items-center gap-3">
                <Cog6ToothIcon className="h-10 w-10 text-blue-600" />
                City Settings
              </h1>
              <p className="text-gray-600 mt-2">{city?.name}, {city?.state}</p>
            </div>

            <div className="grid lg:grid-cols-4 gap-8">
              {/* Sidebar Navigation */}
              <div className="lg:col-span-1">
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden sticky top-24">
                  <nav className="p-4">
                    <button
                      onClick={() => setActiveTab('general')}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium mb-2 transition-colors ${
                        activeTab === 'general'
                          ? 'bg-blue-50 text-blue-700'
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <Cog6ToothIcon className="h-5 w-5" />
                      General
                    </button>
                    <button
                      onClick={() => setActiveTab('staff')}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium mb-2 transition-colors ${
                        activeTab === 'staff'
                          ? 'bg-blue-50 text-blue-700'
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <UserGroupIcon className="h-5 w-5" />
                      Staff Management
                    </button>
                    <button
                      onClick={() => setActiveTab('moderation')}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium mb-2 transition-colors ${
                        activeTab === 'moderation'
                          ? 'bg-blue-50 text-blue-700'
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <ShieldCheckIcon className="h-5 w-5" />
                      Moderation
                    </button>
                    <button
                      onClick={() => setActiveTab('notifications')}
                      className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${
                        activeTab === 'notifications'
                          ? 'bg-blue-50 text-blue-700'
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <BellIcon className="h-5 w-5" />
                      Notifications
                    </button>
                  </nav>
                </div>
              </div>

              {/* Main Content */}
              <div className="lg:col-span-3">
                {activeTab === 'general' && (
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">General Settings</h2>
                    <form onSubmit={handleSaveGeneral} className="space-y-6">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          City Name
                        </label>
                        <input
                          type="text"
                          value={generalSettings.name}
                          onChange={(e) => setGeneralSettings({ ...generalSettings, name: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          State
                        </label>
                        <input
                          type="text"
                          value={generalSettings.state}
                          onChange={(e) => setGeneralSettings({ ...generalSettings, state: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Description
                        </label>
                        <textarea
                          value={generalSettings.description}
                          onChange={(e) => setGeneralSettings({ ...generalSettings, description: e.target.value })}
                          rows={4}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                        />
                      </div>

                      <div className="grid md:grid-cols-2 gap-6">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            <GlobeAltIcon className="h-4 w-4 inline mr-1" />
                            Website
                          </label>
                          <input
                            type="url"
                            value={generalSettings.website}
                            onChange={(e) => setGeneralSettings({ ...generalSettings, website: e.target.value })}
                            placeholder="https://city.gov"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>

                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            <EnvelopeIcon className="h-4 w-4 inline mr-1" />
                            Contact Email
                          </label>
                          <input
                            type="email"
                            value={generalSettings.contact_email}
                            onChange={(e) => setGeneralSettings({ ...generalSettings, contact_email: e.target.value })}
                            placeholder="elections@city.gov"
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          />
                        </div>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Timezone
                        </label>
                        <select
                          value={generalSettings.timezone}
                          onChange={(e) => setGeneralSettings({ ...generalSettings, timezone: e.target.value })}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        >
                          <option value="America/New_York">Eastern Time</option>
                          <option value="America/Chicago">Central Time</option>
                          <option value="America/Denver">Mountain Time</option>
                          <option value="America/Los_Angeles">Pacific Time</option>
                          <option value="America/Anchorage">Alaska Time</option>
                          <option value="Pacific/Honolulu">Hawaii Time</option>
                        </select>
                      </div>

                      <div className="flex gap-3">
                        <button
                          type="submit"
                          disabled={isSaving}
                          className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
                        >
                          {isSaving ? 'Saving...' : 'Save Changes'}
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {activeTab === 'staff' && (
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">Staff Management</h2>
                    <p className="text-gray-600 mb-6">Manage city staff members and their permissions</p>

                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                      <UserGroupIcon className="h-12 w-12 text-blue-600 mx-auto mb-3" />
                      <h3 className="text-lg font-semibold text-gray-900 mb-2">
                        Staff Management Coming Soon
                      </h3>
                      <p className="text-gray-600">
                        Invite and manage staff members with different permission levels
                      </p>
                    </div>
                  </div>
                )}

                {activeTab === 'moderation' && (
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">Moderation Settings</h2>
                    <form onSubmit={handleSaveModeration} className="space-y-6">
                      <div className="space-y-4">
                        <label className="flex items-start gap-3">
                          <input
                            type="checkbox"
                            checked={moderationSettings.auto_approve_questions}
                            onChange={(e) => setModerationSettings({ ...moderationSettings, auto_approve_questions: e.target.checked })}
                            className="mt-1 h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <div>
                            <div className="font-medium text-gray-900">Auto-approve Questions</div>
                            <div className="text-sm text-gray-600">
                              Automatically approve questions without manual review (not recommended)
                            </div>
                          </div>
                        </label>

                        <label className="flex items-start gap-3">
                          <input
                            type="checkbox"
                            checked={moderationSettings.require_candidate_verification}
                            onChange={(e) => setModerationSettings({ ...moderationSettings, require_candidate_verification: e.target.checked })}
                            className="mt-1 h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <div>
                            <div className="font-medium text-gray-900">Require Candidate Verification</div>
                            <div className="text-sm text-gray-600">
                              Candidates must be verified before they can answer questions
                            </div>
                          </div>
                        </label>

                        <label className="flex items-start gap-3">
                          <input
                            type="checkbox"
                            checked={moderationSettings.allow_anonymous_questions}
                            onChange={(e) => setModerationSettings({ ...moderationSettings, allow_anonymous_questions: e.target.checked })}
                            className="mt-1 h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <div>
                            <div className="font-medium text-gray-900">Allow Anonymous Questions</div>
                            <div className="text-sm text-gray-600">
                              Let voters submit questions without creating an account
                            </div>
                          </div>
                        </label>

                        <label className="flex items-start gap-3">
                          <input
                            type="checkbox"
                            checked={moderationSettings.profanity_filter_enabled}
                            onChange={(e) => setModerationSettings({ ...moderationSettings, profanity_filter_enabled: e.target.checked })}
                            className="mt-1 h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <div>
                            <div className="font-medium text-gray-900">Enable Profanity Filter</div>
                            <div className="text-sm text-gray-600">
                              Automatically flag questions containing inappropriate language
                            </div>
                          </div>
                        </label>
                      </div>

                      <div className="flex gap-3 pt-4">
                        <button
                          type="submit"
                          disabled={isSaving}
                          className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
                        >
                          {isSaving ? 'Saving...' : 'Save Settings'}
                        </button>
                      </div>
                    </form>
                  </div>
                )}

                {activeTab === 'notifications' && (
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">Notification Settings</h2>
                    <form onSubmit={handleSaveNotifications} className="space-y-6">
                      <div className="space-y-4">
                        <label className="flex items-start gap-3">
                          <input
                            type="checkbox"
                            checked={notificationSettings.email_new_questions}
                            onChange={(e) => setNotificationSettings({ ...notificationSettings, email_new_questions: e.target.checked })}
                            className="mt-1 h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <div>
                            <div className="font-medium text-gray-900">New Questions</div>
                            <div className="text-sm text-gray-600">
                              Get notified when voters submit new questions
                            </div>
                          </div>
                        </label>

                        <label className="flex items-start gap-3">
                          <input
                            type="checkbox"
                            checked={notificationSettings.email_new_candidates}
                            onChange={(e) => setNotificationSettings({ ...notificationSettings, email_new_candidates: e.target.checked })}
                            className="mt-1 h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <div>
                            <div className="font-medium text-gray-900">New Candidates</div>
                            <div className="text-sm text-gray-600">
                              Get notified when candidates register on the platform
                            </div>
                          </div>
                        </label>

                        <label className="flex items-start gap-3">
                          <input
                            type="checkbox"
                            checked={notificationSettings.email_flagged_content}
                            onChange={(e) => setNotificationSettings({ ...notificationSettings, email_flagged_content: e.target.checked })}
                            className="mt-1 h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <div>
                            <div className="font-medium text-gray-900">Flagged Content</div>
                            <div className="text-sm text-gray-600">
                              Get notified when content is flagged for review
                            </div>
                          </div>
                        </label>

                        <label className="flex items-start gap-3">
                          <input
                            type="checkbox"
                            checked={notificationSettings.email_daily_digest}
                            onChange={(e) => setNotificationSettings({ ...notificationSettings, email_daily_digest: e.target.checked })}
                            className="mt-1 h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <div>
                            <div className="font-medium text-gray-900">Daily Digest</div>
                            <div className="text-sm text-gray-600">
                              Receive a daily summary of platform activity
                            </div>
                          </div>
                        </label>

                        <label className="flex items-start gap-3">
                          <input
                            type="checkbox"
                            checked={notificationSettings.email_weekly_report}
                            onChange={(e) => setNotificationSettings({ ...notificationSettings, email_weekly_report: e.target.checked })}
                            className="mt-1 h-5 w-5 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                          />
                          <div>
                            <div className="font-medium text-gray-900">Weekly Report</div>
                            <div className="text-sm text-gray-600">
                              Receive a weekly analytics report
                            </div>
                          </div>
                        </label>
                      </div>

                      <div className="flex gap-3 pt-4">
                        <button
                          type="submit"
                          disabled={isSaving}
                          className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 transition-colors"
                        >
                          {isSaving ? 'Saving...' : 'Save Preferences'}
                        </button>
                      </div>
                    </form>
                  </div>
                )}
              </div>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
}
