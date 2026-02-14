import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  UserGroupIcon,
  QuestionMarkCircleIcon,
  ChatBubbleLeftRightIcon,
  FlagIcon,
  ArrowTrendingUpIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';
import StatCard from '../../components/admin/StatCard';
import { adminDashboardAPI } from '../../services/adminApi';
import { AdminStats, AuditLog } from '../../types';
import LoadingSpinner from '../../components/LoadingSpinner';
import ErrorMessage from '../../components/ErrorMessage';

const AdminDashboard: React.FC = () => {
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<AuditLog[]>([]);
  const [alerts, setAlerts] = useState<Array<{ id: number; type: string; message: string; severity: string; created_at: string }>>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, activityData, alertsData] = await Promise.all([
        adminDashboardAPI.getStats(),
        adminDashboardAPI.getRecentActivity(10),
        adminDashboardAPI.getAlerts(),
      ]);
      setStats(statsData);
      setRecentActivity(activityData);
      setAlerts(alertsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
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

  if (!stats) {
    return <ErrorMessage message="No data available" />;
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="mt-1 text-sm text-gray-500">
          Overview of platform activity and moderation queue
        </p>
      </div>

      {/* Alerts */}
      {alerts.length > 0 && (
        <div className="space-y-2">
          {alerts.map((alert) => (
            <div
              key={alert.id}
              className={`flex items-start p-4 border rounded-lg ${getSeverityColor(alert.severity)}`}
            >
              <ExclamationTriangleIcon className="h-5 w-5 mt-0.5 mr-3 flex-shrink-0" />
              <div className="flex-1">
                <p className="font-medium">{alert.type}</p>
                <p className="text-sm mt-1">{alert.message}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Users"
          value={stats.total_users.toLocaleString()}
          subtitle={`${stats.active_users_24h} active in last 24h`}
          icon={UserGroupIcon}
          color="blue"
        />
        <StatCard
          title="Questions"
          value={stats.total_questions.toLocaleString()}
          subtitle={`${stats.pending_questions} pending approval`}
          icon={QuestionMarkCircleIcon}
          color="purple"
        />
        <StatCard
          title="Video Answers"
          value={stats.total_answers.toLocaleString()}
          icon={ChatBubbleLeftRightIcon}
          color="green"
        />
        <StatCard
          title="Engagement Rate"
          value={`${stats.engagement_rate.toFixed(1)}%`}
          subtitle={`${stats.total_votes.toLocaleString()} total votes`}
          icon={ArrowTrendingUpIcon}
          color="yellow"
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Link
            to="/admin/questions"
            className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div>
              <p className="font-medium text-gray-900">Moderate Questions</p>
              <p className="text-sm text-gray-500">{stats.pending_questions} pending</p>
            </div>
            <QuestionMarkCircleIcon className="h-8 w-8 text-indigo-600" />
          </Link>
          <Link
            to="/admin/content"
            className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div>
              <p className="font-medium text-gray-900">Review Reports</p>
              <p className="text-sm text-gray-500">{stats.flagged_content} flagged items</p>
            </div>
            <FlagIcon className="h-8 w-8 text-yellow-600" />
          </Link>
          <Link
            to="/admin/users"
            className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div>
              <p className="font-medium text-gray-900">Manage Users</p>
              <p className="text-sm text-gray-500">{stats.total_users} total</p>
            </div>
            <UserGroupIcon className="h-8 w-8 text-blue-600" />
          </Link>
          <Link
            to="/admin/analytics"
            className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div>
              <p className="font-medium text-gray-900">View Analytics</p>
              <p className="text-sm text-gray-500">Insights & trends</p>
            </div>
            <ArrowTrendingUpIcon className="h-8 w-8 text-green-600" />
          </Link>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Activity</h2>
        </div>
        <div className="divide-y divide-gray-200">
          {recentActivity.length === 0 ? (
            <div className="px-6 py-8 text-center text-sm text-gray-500">
              No recent activity
            </div>
          ) : (
            recentActivity.map((log) => (
              <div key={log.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">
                      {log.event_type.replace(/_/g, ' ')}
                    </p>
                    {log.target_type && (
                      <p className="text-sm text-gray-500 mt-1">
                        Target: {log.target_type} #{log.target_id}
                      </p>
                    )}
                    {log.severity !== 'info' && (
                      <span
                        className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium mt-2 ${
                          log.severity === 'critical'
                            ? 'bg-red-100 text-red-800'
                            : 'bg-yellow-100 text-yellow-800'
                        }`}
                      >
                        {log.severity}
                      </span>
                    )}
                  </div>
                  <div className="ml-4 flex-shrink-0">
                    <p className="text-xs text-gray-500">
                      {new Date(log.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
        <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
          <Link
            to="/admin/audit"
            className="text-sm font-medium text-indigo-600 hover:text-indigo-500"
          >
            View all activity
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
