import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useContest, useContestCandidates } from '../hooks/useBallots';
import { useContestQuestions, useCreateQuestion } from '../hooks/useQuestions';
import { useAuthContext } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import CandidateCard from '../components/CandidateCard';
import QuestionCard from '../components/QuestionCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import SmartQuestionComposer from '../components/SmartQuestionComposer';

const ContestPage: React.FC = () => {
  const { contestId } = useParams<{ contestId: string }>();
  const { isAuthenticated } = useAuthContext();
  const [showQuestionForm, setShowQuestionForm] = useState(false);

  const contestIdNum = contestId ? parseInt(contestId) : undefined;

  const { data: contest, isLoading: contestLoading, error: contestError } = useContest(contestIdNum);
  const { data: candidates, isLoading: candidatesLoading } = useContestCandidates(contestIdNum);
  const {
    data: questionsData,
    isLoading: questionsLoading,
    refetch: refetchQuestions,
  } = useContestQuestions(contestIdNum, { status: 'approved', page_size: 50 });

  const createQuestionMutation = useCreateQuestion();

  const handleSubmitQuestion = async (questionText: string) => {
    if (!contestIdNum || !questionText.trim()) return;

    try {
      await createQuestionMutation.mutateAsync({
        contest_id: contestIdNum,
        question_text: questionText,
        issue_tags: [],
        context: undefined,
      });

      setShowQuestionForm(false);
      refetchQuestions();
    } catch (error) {
      console.error('Failed to submit question:', error);
    }
  };

  const handleCancelQuestion = () => {
    setShowQuestionForm(false);
  };

  if (contestLoading) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8 min-h-screen flex items-center justify-center">
          <div className="text-center animate-fadeIn">
            <div className="w-20 h-20 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
            <LoadingSpinner size="lg" message="Loading contest..." />
          </div>
        </div>
      </Layout>
    );
  }

  if (contestError || !contest) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8 min-h-screen flex items-center justify-center">
          <div className="max-w-md w-full animate-scaleIn">
            <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-8 text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Unable to Load Contest</h3>
              <ErrorMessage message="Failed to load contest. Please try again." />
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  const questions = questionsData?.items || [];
  const activeCandidates = candidates?.filter((c) => c.status === 'active') || [];

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8 animate-fadeIn">
        {/* Contest Header - Reddit-style post header */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden mb-6">
          {/* Top Bar with type badge */}
          <div className="bg-gradient-to-r from-gray-50 to-blue-50/50 px-8 py-4 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <span
                className={`inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-bold shadow-sm ${
                  contest.type === 'race'
                    ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white'
                    : 'bg-gradient-to-r from-purple-500 to-purple-600 text-white'
                }`}
              >
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                {contest.type === 'race' ? 'Election Race' : 'Ballot Measure'}
              </span>
              {contest.jurisdiction && (
                <span className="text-sm text-gray-600 flex items-center gap-1">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  {contest.jurisdiction}
                </span>
              )}
            </div>
          </div>

          {/* Main Content */}
          <div className="p-8">
            <h1 className="text-4xl font-extrabold text-gray-900 mb-4 leading-tight">
              {contest.title}
            </h1>

            {contest.office && (
              <div className="flex items-center gap-2 mb-4">
                <div className="px-3 py-1 bg-blue-100 text-blue-800 rounded-lg text-sm font-semibold">
                  Office: {contest.office}
                </div>
              </div>
            )}

            {contest.description && (
              <div className="mt-6 p-6 bg-gray-50 rounded-xl border border-gray-200">
                <p className="text-gray-700 leading-relaxed text-lg">{contest.description}</p>
              </div>
            )}

            {contest.seat_count && contest.seat_count > 1 && (
              <div className="mt-6 bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 rounded-lg p-5">
                <div className="flex items-start gap-3">
                  <svg className="w-6 h-6 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div>
                    <p className="text-blue-900 font-semibold text-lg">Multi-Seat Race</p>
                    <p className="text-blue-800 mt-1">
                      You may vote for up to {contest.seat_count} candidates in this race.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content - 2 columns */}
          <div className="lg:col-span-2 space-y-8">
            {/* Candidates Section - Reddit-style cards */}
            <section>
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <h2 className="text-3xl font-bold text-gray-900">
                  Candidates <span className="text-gray-500">({activeCandidates.length})</span>
                </h2>
              </div>

              {candidatesLoading && (
                <div className="flex justify-center py-8">
                  <LoadingSpinner message="Loading candidates..." />
                </div>
              )}

              {activeCandidates.length > 0 ? (
                <div className="grid gap-5">
                  {activeCandidates.map((candidate, index) => (
                    <div
                      key={candidate.id}
                      className="animate-fadeIn"
                      style={{ animationDelay: `${index * 0.05}s` }}
                    >
                      <CandidateCard candidate={candidate} />
                    </div>
                  ))}
                </div>
              ) : (
                !candidatesLoading && (
                  <div className="bg-gradient-to-br from-gray-50 to-blue-50/30 rounded-2xl p-12 text-center border-2 border-dashed border-gray-300">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 mb-2">No Active Candidates Yet</h3>
                    <p className="text-gray-600">Candidates will appear here once they register for this race.</p>
                  </div>
                )
              )}
            </section>

            {/* Questions Section - Reddit-style */}
            <section>
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h2 className="text-3xl font-bold text-gray-900">
                    Questions <span className="text-gray-500">({questions.length})</span>
                  </h2>
                </div>
                {isAuthenticated && (
                  <button
                    onClick={() => setShowQuestionForm(!showQuestionForm)}
                    className="group px-5 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 transition-all font-semibold flex items-center gap-2 shadow-lg hover:shadow-xl hover:scale-105"
                  >
                    {!showQuestionForm && (
                      <svg className="w-5 h-5 group-hover:rotate-90 transition-transform" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
                      </svg>
                    )}
                    {showQuestionForm ? 'Cancel' : 'Ask Question with AI'}
                  </button>
                )}
              </div>

              {/* Question Form - AI-Powered Smart Composer */}
              {showQuestionForm && contestIdNum && (
                <div className="mb-6">
                  <SmartQuestionComposer
                    contestId={contestIdNum}
                    onSubmit={handleSubmitQuestion}
                    onCancel={handleCancelQuestion}
                  />
                </div>
              )}

              {questionsLoading && <LoadingSpinner message="Loading questions..." />}

              {questions.length > 0 ? (
                <div className="space-y-5">
                  {questions.map((question, index) => (
                    <div
                      key={question.id}
                      className="animate-fadeIn"
                      style={{ animationDelay: `${index * 0.05}s` }}
                    >
                      <QuestionCard question={question} />
                    </div>
                  ))}
                </div>
              ) : (
                !questionsLoading && (
                  <div className="bg-gradient-to-br from-gray-50 to-blue-50/30 rounded-2xl p-12 text-center border-2 border-dashed border-gray-300">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <h3 className="text-xl font-bold text-gray-900 mb-2">No Questions Yet</h3>
                    <p className="text-gray-600 mb-4">Be the first to ask a question for this race!</p>
                    {!isAuthenticated ? (
                      <Link
                        to="/login"
                        className="inline-block px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition-all shadow-md hover:shadow-lg"
                      >
                        Log in to Submit a Question
                      </Link>
                    ) : (
                      <button
                        onClick={() => setShowQuestionForm(true)}
                        className="inline-block px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all shadow-md hover:shadow-lg"
                      >
                        Ask the First Question
                      </button>
                    )}
                  </div>
                )
              )}
            </section>
          </div>

          {/* Sidebar - 1 column - Enhanced sticky sidebar */}
          <div className="space-y-6 lg:sticky lg:top-24 self-start">
            {/* Quick Stats - Reddit-style */}
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-gray-50 to-blue-50 px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-bold text-gray-900">Contest Stats</h3>
              </div>
              <div className="p-6 space-y-4">
                <StatRow
                  label="Candidates"
                  value={activeCandidates.length}
                  icon={
                    <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                  }
                />
                <StatRow
                  label="Questions"
                  value={questions.length}
                  icon={
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  }
                />
                <StatRow
                  label="Total Answers"
                  value={
                    activeCandidates.reduce(
                      (sum, c) => sum + (c.video_answers?.length || 0),
                      0
                    )
                  }
                  icon={
                    <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  }
                />
              </div>
            </div>

            {/* Actions - Enhanced CTA */}
            <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-6 shadow-lg text-white">
              <h3 className="text-lg font-bold mb-4">Take Action</h3>
              <div className="space-y-4">
                {isAuthenticated ? (
                  <>
                    <button
                      onClick={() => setShowQuestionForm(true)}
                      className="w-full px-4 py-3 bg-white text-blue-600 rounded-xl hover:bg-blue-50 transition-all flex items-center justify-center gap-2 shadow-md hover:shadow-lg font-semibold"
                    >
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
                      </svg>
                      Ask Question with AI
                    </button>
                    <p className="text-sm text-blue-100">
                      Get AI-powered help crafting great questions that matter to voters
                    </p>
                  </>
                ) : (
                  <>
                    <Link
                      to="/login"
                      className="block w-full px-4 py-3 bg-white text-blue-600 rounded-xl hover:bg-blue-50 transition-all text-center font-semibold shadow-md hover:shadow-lg"
                    >
                      Login to Participate
                    </Link>
                    <p className="text-sm text-blue-100">
                      Log in to ask questions and vote on important issues
                    </p>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

// Helper Component - Enhanced with icons
const StatRow: React.FC<{ label: string; value: number; icon?: React.ReactNode }> = ({
  label,
  value,
  icon,
}) => (
  <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
    <div className="flex items-center gap-2">
      {icon}
      <span className="text-gray-700 font-medium">{label}</span>
    </div>
    <span className="text-2xl font-bold text-gray-900">{value}</span>
  </div>
);

export default ContestPage;
