import React from 'react';
import { Link } from 'react-router-dom';
import { useBallots } from '../hooks/useBallots';
import { useAuthContext } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { format } from 'date-fns';

const HomePage: React.FC = () => {
  const { user, isAuthenticated } = useAuthContext();
  const { data: ballots, isLoading, error, refetch } = useBallots({
    city_id: user?.city_id,
    is_published: true,
  });

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Hero Section */}
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-civic-blue mb-4">CivicQ</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Turning campaigning into a standardized, verifiable public record of candidates
            answering the public's top questions, city by city, with integrity by design.
          </p>
        </header>

        {/* Main Content */}
        <div className="max-w-6xl mx-auto">
          {/* Features Section */}
          <div className="mb-12 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <FeatureCard
              icon="🗳️"
              title="Your Ballot"
              description="View all contests and measures for your local election in one place"
            />
            <FeatureCard
              icon="❓"
              title="Ask Questions"
              description="Submit and vote on questions you want candidates to answer"
            />
            <FeatureCard
              icon="📹"
              title="Watch Answers"
              description="See candidates respond to your questions in structured video format"
            />
            <FeatureCard
              icon="⚖️"
              title="Compare Candidates"
              description="Side-by-side comparison of candidate positions and answers"
            />
            <FeatureCard
              icon="🔍"
              title="Transparent Process"
              description="Anti-polarization ranking ensures diverse representation"
            />
            <FeatureCard
              icon="✓"
              title="Verified Identity"
              description="All candidates and voters go through identity verification"
            />
          </div>

          {/* Available Ballots */}
          {isAuthenticated && (
            <div className="bg-white rounded-lg shadow-md p-8 mb-8">
              <h2 className="text-2xl font-semibold mb-6">Available Ballots</h2>

              {isLoading && <LoadingSpinner message="Loading ballots..." />}

              {error && (
                <ErrorMessage
                  message="Failed to load ballots. Please try again."
                  onRetry={() => refetch()}
                />
              )}

              {ballots && ballots.length > 0 ? (
                <div className="grid gap-4">
                  {ballots.map((ballot) => (
                    <Link
                      key={ballot.id}
                      to={`/ballot?id=${ballot.id}`}
                      className="block p-6 border border-gray-200 rounded-lg hover:border-civic-blue hover:shadow-md transition-all"
                    >
                      <h3 className="text-xl font-semibold text-gray-900">
                        {ballot.city_name}
                      </h3>
                      <p className="text-gray-600 mt-1">
                        Election Date: {format(new Date(ballot.election_date), 'MMMM d, yyyy')}
                      </p>
                      {ballot.contests && (
                        <p className="text-sm text-gray-500 mt-2">
                          {ballot.contests.length} contest{ballot.contests.length !== 1 ? 's' : ''}
                        </p>
                      )}
                    </Link>
                  ))}
                </div>
              ) : (
                ballots &&
                ballots.length === 0 && (
                  <div className="text-center py-8 text-gray-600">
                    <p>No ballots available for your area yet.</p>
                    <p className="text-sm mt-2">Check back soon!</p>
                  </div>
                )
              )}
            </div>
          )}

          {/* Call to Action */}
          {!isAuthenticated && (
            <div className="bg-civic-blue text-white rounded-lg shadow-lg p-8 text-center">
              <h2 className="text-3xl font-bold mb-4">Get Started</h2>
              <p className="text-lg mb-6">
                Join CivicQ to view your ballot, ask questions, and make informed voting
                decisions.
              </p>
              <div className="flex justify-center space-x-4">
                <Link
                  to="/login"
                  className="bg-white text-civic-blue px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-civic-green text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
                >
                  Sign Up
                </Link>
              </div>
            </div>
          )}

          {/* How It Works */}
          <div className="mt-12 bg-white rounded-lg shadow-md p-8">
            <h2 className="text-2xl font-semibold mb-6 text-center">How It Works</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <Step number={1} title="Verify Your Identity" description="Quick verification ensures only real voters participate" />
              <Step number={2} title="Submit Questions" description="Ask what matters to you and vote on others' questions" />
              <Step number={3} title="Candidates Respond" description="Candidates record video answers to top-ranked questions" />
              <Step number={4} title="Make Informed Choices" description="Compare answers side-by-side and vote with confidence" />
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

// Helper Components
const FeatureCard: React.FC<{ icon: string; title: string; description: string }> = ({
  icon,
  title,
  description,
}) => (
  <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
    <div className="text-4xl mb-3">{icon}</div>
    <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
    <p className="text-gray-600 text-sm">{description}</p>
  </div>
);

const Step: React.FC<{ number: number; title: string; description: string }> = ({
  number,
  title,
  description,
}) => (
  <div className="text-center">
    <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-civic-blue text-white text-xl font-bold mb-3">
      {number}
    </div>
    <h3 className="font-semibold text-gray-900 mb-2">{title}</h3>
    <p className="text-sm text-gray-600">{description}</p>
  </div>
);

export default HomePage;
