import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { useBallot } from '../hooks/useBallots';
import { useAuthContext } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import ContestCard from '../components/ContestCard';
import LoadingSpinner from '../components/LoadingSpinner';
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
        <div className="container mx-auto px-4 py-8">
          <LoadingSpinner size="lg" message="Loading your ballot..." />
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <ErrorMessage
            message="Failed to load ballot. Please try again."
            onRetry={() => refetch()}
          />
        </div>
      </Layout>
    );
  }

  if (!ballot) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
            <p className="text-yellow-800">No ballot found. Please select a ballot from the home page.</p>
          </div>
        </div>
      </Layout>
    );
  }

  // Sort contests by display order
  const sortedContests = ballot.contests
    ? [...ballot.contests].sort((a, b) => a.display_order - b.display_order)
    : [];

  // Separate races and measures
  const races = sortedContests.filter((c) => c.type === 'race');
  const measures = sortedContests.filter((c) => c.type === 'measure');

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Ballot Header */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">{ballot.city_name}</h1>
              <p className="text-xl text-gray-600">
                Election Date: {format(new Date(ballot.election_date), 'MMMM d, yyyy')}
              </p>
              {ballot.is_published && (
                <span className="inline-block mt-3 px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">
                  Published
                </span>
              )}
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Ballot Version {ballot.version}</p>
              {user?.city_name && (
                <p className="text-sm text-gray-600 mt-1">Your City: {user.city_name}</p>
              )}
            </div>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <StatCard
            label="Total Contests"
            value={sortedContests.length}
            icon="📋"
          />
          <StatCard
            label="Races"
            value={races.length}
            icon="🗳️"
          />
          <StatCard
            label="Measures"
            value={measures.length}
            icon="📊"
          />
        </div>

        {/* Races Section */}
        {races.length > 0 && (
          <section className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Races</h2>
            <div className="grid gap-6">
              {races.map((contest) => (
                <ContestCard key={contest.id} contest={contest} ballotId={ballot.id} />
              ))}
            </div>
          </section>
        )}

        {/* Measures Section */}
        {measures.length > 0 && (
          <section className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Ballot Measures</h2>
            <div className="grid gap-6">
              {measures.map((contest) => (
                <ContestCard key={contest.id} contest={contest} ballotId={ballot.id} />
              ))}
            </div>
          </section>
        )}

        {/* Empty State */}
        {sortedContests.length === 0 && (
          <div className="bg-gray-50 rounded-lg p-12 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
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
            <h3 className="mt-4 text-lg font-medium text-gray-900">No contests available</h3>
            <p className="mt-2 text-gray-600">
              This ballot doesn't have any contests yet. Check back later.
            </p>
          </div>
        )}
      </div>
    </Layout>
  );
};

// Helper Component
const StatCard: React.FC<{ label: string; value: number; icon: string }> = ({
  label,
  value,
  icon,
}) => (
  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <div className="flex items-center justify-between">
      <div>
        <p className="text-sm text-gray-600 mb-1">{label}</p>
        <p className="text-3xl font-bold text-gray-900">{value}</p>
      </div>
      <div className="text-4xl">{icon}</div>
    </div>
  </div>
);

export default BallotPage;
