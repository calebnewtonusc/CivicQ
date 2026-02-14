import React, { useEffect, useState } from 'react';
import { ArrowDownTrayIcon } from '@heroicons/react/24/outline';
import { analyticsAPI } from '../../services/adminApi';
import { AnalyticsData } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

const Analytics: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      const analyticsData = await analyticsAPI.getAnalytics();
      setData(analyticsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async (format: 'csv' | 'json') => {
    try {
      const blob = await analyticsAPI.exportAnalytics(format);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-${new Date().toISOString()}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      alert(`Failed to export: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner />
      </div>
    );
  }

  if (error) {
    return <ErrorMessage message={error} />;
  }

  if (!data) {
    return <ErrorMessage message="No analytics data available" />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
          <p className="mt-1 text-sm text-gray-500">
            Platform engagement metrics and insights
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={() => handleExport('csv')}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            Export CSV
          </button>
          <button
            onClick={() => handleExport('json')}
            className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
          >
            <ArrowDownTrayIcon className="h-4 w-4 mr-2" />
            Export JSON
          </button>
        </div>
      </div>

      {/* Answer Coverage */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Answer Coverage</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div>
            <p className="text-sm text-gray-500">Total Questions</p>
            <p className="text-2xl font-semibold text-gray-900">
              {data.answer_coverage.total_questions}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Answered</p>
            <p className="text-2xl font-semibold text-green-600">
              {data.answer_coverage.answered_questions}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-500">Coverage</p>
            <p className="text-2xl font-semibold text-indigo-600">
              {data.answer_coverage.coverage_percentage.toFixed(1)}%
            </p>
          </div>
        </div>
        <div className="mt-4">
          <div className="relative pt-1">
            <div className="overflow-hidden h-2 text-xs flex rounded bg-gray-200">
              <div
                style={{ width: `${data.answer_coverage.coverage_percentage}%` }}
                className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Top Topics */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Trending Topics</h2>
        <div className="space-y-2">
          {data.top_topics.slice(0, 10).map((topic, idx) => (
            <div key={idx} className="flex items-center justify-between">
              <span className="text-sm text-gray-700">{topic.tag}</span>
              <span className="text-sm font-medium text-gray-900">{topic.count} questions</span>
            </div>
          ))}
        </div>
      </div>

      {/* User Demographics */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Users by City</h2>
          <div className="space-y-2">
            {data.user_demographics.by_city.map((city, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-sm text-gray-700">{city.city}</span>
                <span className="text-sm font-medium text-gray-900">{city.count} users</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Verification Status</h2>
          <div className="space-y-2">
            {data.user_demographics.by_verification_status.map((status, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <span className="text-sm text-gray-700 capitalize">{status.status}</span>
                <span className="text-sm font-medium text-gray-900">{status.count} users</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
