import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

interface City {
  id: number;
  name: string;
  slug: string;
  state: string;
  status: string;
  next_election_date: string | null;
}

interface DashboardStats {
  total_voters: number;
  total_questions: number;
  total_candidates: number;
  total_ballots: number;
  total_contests: number;
  questions_this_week: number;
  voters_this_week: number;
  avg_questions_per_contest: number;
  avg_votes_per_question: number;
  next_election_date: string | null;
  days_until_election: number | null;
}

const CityDashboardPage: React.FC = () => {
  const { cityId } = useParams<{ cityId: string }>();
  const navigate = useNavigate();

  const [city, setCity] = useState<City | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const getToken = () => localStorage.getItem('access_token');

  useEffect(() => {
    fetchDashboardData();
  }, [cityId]);

  const fetchDashboardData = async () => {
    try {
      const [cityRes, statsRes] = await Promise.all([
        axios.get(`${API_BASE_URL}/cities/${cityId}`, {
          headers: { Authorization: `Bearer ${getToken()}` }
        }),
        axios.get(`${API_BASE_URL}/cities/${cityId}/dashboard`, {
          headers: { Authorization: `Bearer ${getToken()}` }
        })
      ]);

      setCity(cityRes.data);
      setStats(statsRes.data);
      setLoading(false);
    } catch (err: any) {
      console.error('Error fetching dashboard data:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error || !city || !stats) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-md p-8 max-w-md">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Error</h2>
          <p className="text-gray-700">{error || 'Failed to load dashboard'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {city.name} Dashboard
              </h1>
              <p className="text-sm text-gray-600">
                City Management Portal
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                to={`/city/${city.id}/settings`}
                className="px-4 py-2 text-gray-700 hover:text-gray-900 border border-gray-300 rounded-md"
              >
                Settings
              </Link>
              <button
                onClick={() => navigate('/')}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                View Public Site
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Election Info Banner */}
        {stats.next_election_date && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-xl font-semibold text-blue-900 mb-1">
                  Next Election
                </h2>
                <p className="text-blue-700">
                  {new Date(stats.next_election_date).toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                  })}
                </p>
              </div>
              {stats.days_until_election !== null && (
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-900">
                    {stats.days_until_election}
                  </div>
                  <div className="text-sm text-blue-700">
                    days remaining
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Total Voters"
            value={stats.total_voters}
            change={stats.voters_this_week}
            changeLabel="this week"
            icon="👥"
            color="blue"
          />
          <StatCard
            title="Questions"
            value={stats.total_questions}
            change={stats.questions_this_week}
            changeLabel="this week"
            icon="❓"
            color="green"
          />
          <StatCard
            title="Candidates"
            value={stats.total_candidates}
            icon="🎯"
            color="purple"
          />
          <StatCard
            title="Contests"
            value={stats.total_contests}
            icon="🗳️"
            color="orange"
          />
        </div>

        {/* Engagement Metrics */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Engagement Metrics
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600">Avg. Questions per Contest</span>
                <span className="text-2xl font-bold text-gray-900">
                  {stats.avg_questions_per_contest.toFixed(1)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${Math.min(stats.avg_questions_per_contest * 10, 100)}%` }}
                ></div>
              </div>
            </div>
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600">Avg. Votes per Question</span>
                <span className="text-2xl font-bold text-gray-900">
                  {stats.avg_votes_per_question.toFixed(1)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-600 h-2 rounded-full"
                  style={{ width: `${Math.min(stats.avg_votes_per_question * 2, 100)}%` }}
                ></div>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <QuickActionCard
            title="Manage Ballots"
            description="Create and edit election ballots"
            icon="🗳️"
            onClick={() => navigate(`/city/${city.id}/ballots`)}
          />
          <QuickActionCard
            title="Moderate Questions"
            description="Review and moderate voter questions"
            icon="✅"
            onClick={() => navigate(`/city/${city.id}/questions`)}
          />
          <QuickActionCard
            title="Invite Staff"
            description="Add team members to help manage"
            icon="👥"
            onClick={() => navigate(`/city/${city.id}/staff`)}
          />
          <QuickActionCard
            title="Customize Branding"
            description="Update logo and colors"
            icon="🎨"
            onClick={() => navigate(`/city/${city.id}/branding`)}
          />
          <QuickActionCard
            title="View Analytics"
            description="Detailed engagement analytics"
            icon="📊"
            onClick={() => navigate(`/city/${city.id}/analytics`)}
          />
          <QuickActionCard
            title="Export Data"
            description="Download reports and data"
            icon="📥"
            onClick={() => navigate(`/city/${city.id}/export`)}
          />
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Recent Activity
          </h2>
          <div className="space-y-4">
            {stats.questions_this_week > 0 && (
              <ActivityItem
                icon="❓"
                title="New Questions"
                description={`${stats.questions_this_week} questions submitted this week`}
                time="This week"
              />
            )}
            {stats.voters_this_week > 0 && (
              <ActivityItem
                icon="👥"
                title="New Voters"
                description={`${stats.voters_this_week} voters registered this week`}
                time="This week"
              />
            )}
            {stats.questions_this_week === 0 && stats.voters_this_week === 0 && (
              <p className="text-gray-500 text-center py-8">
                No recent activity
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Stat Card Component
const StatCard: React.FC<{
  title: string;
  value: number;
  change?: number;
  changeLabel?: string;
  icon: string;
  color: 'blue' | 'green' | 'purple' | 'orange';
}> = ({ title, value, change, changeLabel, icon, color }) => {
  const colorClasses = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    purple: 'bg-purple-100 text-purple-600',
    orange: 'bg-orange-100 text-orange-600',
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-gray-600 text-sm font-medium">{title}</h3>
        <span className={`text-2xl ${colorClasses[color]} px-3 py-1 rounded-lg`}>
          {icon}
        </span>
      </div>
      <div className="text-3xl font-bold text-gray-900 mb-2">
        {value.toLocaleString()}
      </div>
      {change !== undefined && changeLabel && (
        <p className="text-sm text-gray-500">
          <span className="text-green-600 font-semibold">+{change}</span> {changeLabel}
        </p>
      )}
    </div>
  );
};

// Quick Action Card Component
const QuickActionCard: React.FC<{
  title: string;
  description: string;
  icon: string;
  onClick: () => void;
}> = ({ title, description, icon, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow text-left w-full"
    >
      <div className="text-3xl mb-3">{icon}</div>
      <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
      <p className="text-sm text-gray-600">{description}</p>
    </button>
  );
};

// Activity Item Component
const ActivityItem: React.FC<{
  icon: string;
  title: string;
  description: string;
  time: string;
}> = ({ icon, title, description, time }) => {
  return (
    <div className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
      <span className="text-2xl">{icon}</span>
      <div className="flex-1">
        <h4 className="font-semibold text-gray-900">{title}</h4>
        <p className="text-sm text-gray-600">{description}</p>
      </div>
      <span className="text-sm text-gray-500">{time}</span>
    </div>
  );
};

export default CityDashboardPage;
