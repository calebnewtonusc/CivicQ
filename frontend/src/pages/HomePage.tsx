import React from 'react';
import { Link } from 'react-router-dom';
import { useBallots } from '../hooks/useBallots';
import { useAuthContext } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { ContestCardSkeleton } from '../components/SkeletonLoader';
import ErrorMessage from '../components/ErrorMessage';
import { format } from 'date-fns';
import {
  CheckBadgeIcon,
  QuestionMarkCircleIcon,
  VideoCameraIcon,
  ScaleIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
} from '@heroicons/react/24/outline';

const FEATURES = [
  {
    icon: CheckBadgeIcon,
    title: 'Your Ballot',
    description: 'View all contests and measures for your local election in one place.',
    color: 'text-primary-600',
    bg: 'bg-primary-50',
  },
  {
    icon: QuestionMarkCircleIcon,
    title: 'Ask Questions',
    description: 'Submit and vote on questions you want candidates to answer.',
    color: 'text-indigo-600',
    bg: 'bg-indigo-50',
  },
  {
    icon: VideoCameraIcon,
    title: 'Watch Answers',
    description: 'See candidates respond to your questions in structured video format.',
    color: 'text-green-600',
    bg: 'bg-green-50',
  },
  {
    icon: ScaleIcon,
    title: 'Compare Candidates',
    description: 'Side-by-side comparison of candidate positions and answers.',
    color: 'text-purple-600',
    bg: 'bg-purple-50',
  },
  {
    icon: MagnifyingGlassIcon,
    title: 'Transparent Process',
    description: 'Anti-polarization ranking ensures diverse, fair representation.',
    color: 'text-orange-600',
    bg: 'bg-orange-50',
  },
  {
    icon: CheckCircleIcon,
    title: 'Verified Identity',
    description: 'All candidates and voters go through identity verification.',
    color: 'text-teal-600',
    bg: 'bg-teal-50',
  },
];

const STEPS = [
  { number: 1, title: 'Verify Your Identity', description: 'Quick verification ensures only real voters participate.' },
  { number: 2, title: 'Submit Questions',     description: 'Ask what matters to you and vote on others\' questions.' },
  { number: 3, title: 'Candidates Respond',   description: 'Candidates record video answers to top-ranked questions.' },
  { number: 4, title: 'Make Informed Choices',description: 'Compare answers side-by-side and vote with confidence.' },
];

const HomePage: React.FC = () => {
  const { user, isAuthenticated } = useAuthContext();
  const { data: ballots, isLoading, error, refetch } = useBallots({
    city_id: user?.city_id,
    is_published: true,
  });

  return (
    <Layout>
      {/* ── Hero ─────────────────────────────────────────── */}
      <section className="relative overflow-hidden bg-gradient-to-br from-primary-600 via-primary-700 to-indigo-700 text-white">
        {/* Background decoration */}
        <div className="absolute inset-0 pointer-events-none" aria-hidden="true">
          <div className="absolute -top-32 -right-32 w-96 h-96 bg-white/5 rounded-full blur-3xl" />
          <div className="absolute -bottom-24 -left-24 w-80 h-80 bg-indigo-500/20 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 mb-6 rounded-full bg-white/10 border border-white/20 text-sm font-medium text-white/90 animate-fade-in">
            <svg className="w-4 h-4 text-green-300" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            Now live in your city
          </div>

          <h1 className="text-5xl sm:text-6xl font-extrabold tracking-tight mb-6 animate-slide-up">
            Democracy,
            <br />
            <span className="text-indigo-200">Accountability First</span>
          </h1>

          <p className="text-lg sm:text-xl text-white/80 max-w-2xl mx-auto mb-10 animate-slide-up" style={{ animationDelay: '0.07s' }}>
            CivicQ creates a standardized, verifiable public record of candidates answering the
            public's top questions — city by city, with integrity by design.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 justify-center animate-slide-up" style={{ animationDelay: '0.14s' }}>
            {isAuthenticated ? (
              <Link to="/ballot" className="btn bg-white text-primary-700 shadow-lg hover:bg-primary-50 hover:shadow-xl active:scale-[0.98] px-7 py-3 text-base rounded-xl font-bold transition-all">
                View My Ballot
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn bg-white text-primary-700 shadow-lg hover:bg-primary-50 hover:shadow-xl active:scale-[0.98] px-7 py-3 text-base rounded-xl font-bold transition-all">
                  Get Started — Free
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                </Link>
                <Link to="/login" className="btn bg-transparent text-white border-2 border-white/40 hover:bg-white/10 hover:border-white/60 active:scale-[0.98] px-7 py-3 text-base rounded-xl font-semibold transition-all">
                  Sign In
                </Link>
              </>
            )}
          </div>
        </div>
      </section>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-20">
        {/* ── Available Ballots ─────────────────────────── */}
        {isAuthenticated && (
          <section className="animate-fade-in">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-900">Available Ballots</h2>
                <p className="text-sm text-gray-500 mt-1">Elections in your area</p>
              </div>
              <Link to="/ballot" className="text-sm font-semibold text-primary-600 hover:text-primary-700 transition-colors flex items-center gap-1">
                View all
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>

            {isLoading && (
              <div className="space-y-4">
                {['sk-ballot-0', 'sk-ballot-1'].map((id) => (
                  <ContestCardSkeleton key={id} />
                ))}
              </div>
            )}

            {error && (
              <ErrorMessage
                message="Failed to load ballots. Please try again."
                onRetry={() => refetch()}
                variant="card"
              />
            )}

            {ballots && ballots.length > 0 && (
              <div className="grid gap-4">
                {ballots.map((ballot, i) => (
                  <Link
                    key={ballot.id}
                    to={`/ballot?id=${ballot.id}`}
                    className="group block card hover:shadow-card-md hover:-translate-y-0.5 transition-all duration-200
                               focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500
                               animate-fade-in"
                    style={{ animationDelay: `${i * 0.06}s` }}
                  >
                    <div className="flex items-center justify-between p-6">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-indigo-500 rounded-xl
                                        flex items-center justify-center shadow-md flex-shrink-0">
                          <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                          </svg>
                        </div>
                        <div>
                          <h3 className="text-lg font-bold text-gray-900 group-hover:text-primary-700 transition-colors">
                            {ballot.city_name}
                          </h3>
                          <p className="text-sm text-gray-500 mt-0.5">
                            Election: {format(new Date(ballot.election_date), 'MMMM d, yyyy')}
                          </p>
                          {ballot.contests && (
                            <p className="text-xs text-gray-400 mt-0.5">
                              {ballot.contests.length} contest{ballot.contests.length !== 1 ? 's' : ''}
                            </p>
                          )}
                        </div>
                      </div>
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gray-50 border border-gray-200
                                      flex items-center justify-center group-hover:bg-primary-50 group-hover:border-primary-200 transition-all">
                        <svg className="w-4 h-4 text-gray-400 group-hover:text-primary-600 group-hover:translate-x-0.5 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                        </svg>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}

            {ballots && ballots.length === 0 && !isLoading && (
              <div className="card p-12 text-center animate-scale-in">
                <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">No Ballots Available Yet</h3>
                <p className="text-gray-500 text-sm mb-6 max-w-xs mx-auto">
                  We're working on adding elections for your area. Check back soon!
                </p>
                <Link to="/how-it-works" className="btn-secondary inline-flex text-sm px-5 py-2">
                  Learn How It Works
                </Link>
              </div>
            )}
          </section>
        )}

        {/* ── Features ─────────────────────────────────── */}
        <section>
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-gray-900 mb-3">
              Everything you need to vote with confidence
            </h2>
            <p className="text-gray-500 max-w-xl mx-auto">
              CivicQ gives you the tools to research candidates, ask the hard questions,
              and make informed decisions.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {FEATURES.map((f, i) => {
              const Icon = f.icon;
              return (
                <div
                  key={f.title}
                  className="group card hover:shadow-card-md hover:-translate-y-0.5 transition-all duration-200 p-6 animate-fade-in"
                  style={{ animationDelay: `${i * 0.06}s` }}
                >
                  <div className={`w-11 h-11 ${f.bg} rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-200`}>
                    <Icon className={`w-6 h-6 ${f.color}`} />
                  </div>
                  <h3 className="text-base font-bold text-gray-900 mb-1.5">{f.title}</h3>
                  <p className="text-sm text-gray-500 leading-relaxed">{f.description}</p>
                </div>
              );
            })}
          </div>
        </section>

        {/* ── CTA Banner (unauthenticated) ──────────────── */}
        {!isAuthenticated && (
          <section className="relative overflow-hidden bg-gradient-to-br from-primary-600 to-indigo-700 rounded-3xl p-10 text-white shadow-card-xl animate-fade-in">
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl" aria-hidden="true" />
            <div className="relative text-center max-w-lg mx-auto">
              <h2 className="text-3xl font-bold mb-4">Ready to make your voice heard?</h2>
              <p className="text-white/80 mb-8 leading-relaxed">
                Join thousands of voters who use CivicQ to research candidates and vote with
                confidence. It's free, secure, and takes less than two minutes to get started.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Link
                  to="/register"
                  className="btn bg-white text-primary-700 shadow-lg hover:bg-primary-50 hover:shadow-xl active:scale-[0.98] px-7 py-3 text-base rounded-xl font-bold transition-all"
                >
                  Create Free Account
                </Link>
                <Link
                  to="/login"
                  className="btn bg-transparent text-white border-2 border-white/40 hover:bg-white/10 hover:border-white/60 active:scale-[0.98] px-7 py-3 text-base rounded-xl font-semibold transition-all"
                >
                  Sign In
                </Link>
              </div>
            </div>
          </section>
        )}

        {/* ── How It Works ─────────────────────────────── */}
        <section>
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-gray-900 mb-3">How It Works</h2>
            <p className="text-gray-500 max-w-xl mx-auto">
              Four simple steps from signup to informed voter.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {STEPS.map((step, i) => (
              <div key={step.number} className="relative text-center animate-fade-in" style={{ animationDelay: `${i * 0.08}s` }}>
                {/* Connector line */}
                {i < STEPS.length - 1 && (
                  <div className="hidden lg:block absolute top-6 left-1/2 w-full h-0.5 bg-gradient-to-r from-primary-200 to-primary-100 z-0" aria-hidden="true" />
                )}

                <div className="relative z-10">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary-600 to-indigo-600 text-white text-lg font-extrabold rounded-full flex items-center justify-center mx-auto mb-4 shadow-md">
                    {step.number}
                  </div>
                  <h3 className="font-bold text-gray-900 mb-2 text-sm">{step.title}</h3>
                  <p className="text-xs text-gray-500 leading-relaxed max-w-[150px] mx-auto">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </Layout>
  );
};

export default HomePage;
