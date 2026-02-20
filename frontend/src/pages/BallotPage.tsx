import React from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { useBallot } from '../hooks/useBallots';
import { useAuthContext } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import ContestCard from '../components/ContestCard';
import { ContestCardSkeleton, BallotHeaderSkeleton } from '../components/SkeletonLoader';
import ErrorMessage from '../components/ErrorMessage';
import { format } from 'date-fns';

const BallotPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const ballotId = searchParams.get('id');
  const { user } = useAuthContext();

  const {
    data: ballot,
    isLoading,
    error,
    refetch,
  } = useBallot(ballotId ? parseInt(ballotId) : undefined);

  if (isLoading) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8 max-w-5xl">
          <BallotHeaderSkeleton />
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 my-8">
            {(['sk-stat-0', 'sk-stat-1', 'sk-stat-2'] as const).map((id, i) => (
              <div key={id} className="card p-6 animate-fade-in" style={{ animationDelay: `${i * 0.07}s` }}>
                <div className="skeleton h-4 w-20 rounded mb-3" />
                <div className="skeleton h-8 w-12 rounded" />
              </div>
            ))}
          </div>
          <div className="space-y-5">
            {['sk-contest-0', 'sk-contest-1', 'sk-contest-2'].map((id) => (
              <ContestCardSkeleton key={id} />
            ))}
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-16 flex items-center justify-center">
          <div className="max-w-md w-full">
            <ErrorMessage
              title="Unable to Load Ballot"
              message="Failed to load ballot. Please check your connection and try again."
              onRetry={() => refetch()}
              variant="card"
            />
          </div>
        </div>
      </Layout>
    );
  }

  if (!ballot) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-16 flex items-center justify-center">
          <div className="max-w-md w-full card p-12 text-center animate-scale-in">
            <div className="w-16 h-16 bg-warning-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-warning-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-2">No Ballot Found</h3>
            <p className="text-gray-500 text-sm mb-6">
              Please select a ballot from the home page to get started.
            </p>
            <Link to="/" className="btn-primary inline-flex px-6 py-3">
              Go to Home Page
            </Link>
          </div>
        </div>
      </Layout>
    );
  }

  // Sort contests by display order with null checks
  const sortedContests = Array.isArray(ballot.contests)
    ? [...ballot.contests].sort((a, b) => (a.display_order || 0) - (b.display_order || 0))
    : [];

  // Separate races and measures with defensive filtering
  const races = sortedContests.filter((c) => c && c.type === 'race');
  const measures = sortedContests.filter((c) => c && c.type === 'measure');

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8 animate-fadeIn">
        {/* Ballot Header - Enhanced with gradient and better visual hierarchy */}
        <div className="relative bg-gradient-to-br from-white to-blue-50/50 rounded-2xl shadow-xl p-8 mb-8 border border-gray-100 overflow-hidden">
          {/* Background decoration */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-100/30 to-indigo-100/30 rounded-full blur-3xl -z-0"></div>

          <div className="relative z-10 flex items-start justify-between">
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <div>
                  <div className="text-sm font-medium text-blue-600 uppercase tracking-wide">Your Ballot</div>
                  <h1 className="text-4xl font-extrabold text-gray-900">{ballot.city_name}</h1>
                </div>
              </div>

              <div className="flex items-center gap-4 mt-4">
                <div className="flex items-center gap-2 text-gray-700">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span className="text-lg font-medium">
                    {format(new Date(ballot.election_date), 'MMMM d, yyyy')}
                  </span>
                </div>

                {ballot.is_published && (
                  <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-green-100 text-green-800 text-sm font-semibold rounded-full border border-green-200">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Published
                  </span>
                )}
              </div>
            </div>

            <div className="text-right ml-6">
              <div className="inline-flex flex-col items-end gap-2">
                <span className="px-3 py-1 bg-gray-100 text-gray-700 text-sm font-medium rounded-lg">
                  Version {ballot.version}
                </span>
                {user?.city_name && (
                  <span className="text-sm text-gray-600">
                    <span className="font-medium">Your City:</span> {user.city_name}
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Summary Stats - Enhanced with animations */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard
            label="Total Contests"
            value={sortedContests.length}
            icon={
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
            }
            gradient="from-blue-500 to-blue-600"
          />
          <StatCard
            label="Races"
            value={races.length}
            icon={
              <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
            }
            gradient="from-purple-500 to-purple-600"
          />
          <StatCard
            label="Measures"
            value={measures.length}
            icon={
              <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            }
            gradient="from-green-500 to-green-600"
          />
        </div>

        {/* Races Section - Enhanced with section headers */}
        {races.length > 0 && (
          <section className="mb-12 animate-slideUp">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center shadow-md">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-900">Races ({races.length})</h2>
            </div>
            <div className="grid gap-6">
              {races.map((contest, index) => (
                <div
                  key={contest.id}
                  className="animate-fadeIn"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <ContestCard contest={contest} ballotId={ballot.id} />
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Measures Section - Enhanced with section headers */}
        {measures.length > 0 && (
          <section className="mb-12 animate-slideUp" style={{ animationDelay: '0.2s' }}>
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center shadow-md">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h2 className="text-3xl font-bold text-gray-900">Ballot Measures ({measures.length})</h2>
            </div>
            <div className="grid gap-6">
              {measures.map((contest, index) => (
                <div
                  key={contest.id}
                  className="animate-fadeIn"
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  <ContestCard contest={contest} ballotId={ballot.id} />
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Empty State - Enhanced with better visual design */}
        {sortedContests.length === 0 && (
          <div className="bg-gradient-to-br from-gray-50 to-blue-50/30 rounded-2xl p-16 text-center border-2 border-dashed border-gray-300 animate-fadeIn">
            <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg
                className="h-10 w-10 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">No Contests Available</h3>
            <p className="text-lg text-gray-600 mb-6">
              This ballot doesn't have any contests yet. Check back later.
            </p>
            <Link
              to="/"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-all shadow-md hover:shadow-lg"
            >
              Back to Home
            </Link>
          </div>
        )}
      </div>
    </Layout>
  );
};

// Helper Component
const StatCard: React.FC<{
  label: string;
  value: number;
  icon: React.ReactNode;
  gradient: string;
}> = ({ label, value, icon, gradient }) => (
  <div className="group card hover:shadow-card-md hover:-translate-y-0.5 p-6 transition-all duration-200 cursor-default">
    <div className="flex items-center justify-between">
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-500 mb-1">{label}</p>
        <p className={`text-4xl font-extrabold bg-gradient-to-r ${gradient} bg-clip-text text-transparent`}>
          {value}
        </p>
      </div>
      <div className={`w-13 h-13 bg-gradient-to-br ${gradient} rounded-xl flex items-center justify-center shadow-md group-hover:scale-110 transition-transform duration-200 p-3`}>
        {icon}
      </div>
    </div>
  </div>
);

export default BallotPage;
