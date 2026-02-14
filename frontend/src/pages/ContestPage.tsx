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
        <div className="container mx-auto px-4 py-8">
          <LoadingSpinner size="lg" message="Loading contest..." />
        </div>
      </Layout>
    );
  }

  if (contestError || !contest) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <ErrorMessage message="Failed to load contest. Please try again." />
        </div>
      </Layout>
    );
  }

  const questions = questionsData?.items || [];
  const activeCandidates = candidates?.filter((c) => c.status === 'active') || [];

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Contest Header */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <span
                className={`inline-block px-3 py-1 rounded-full text-xs font-medium mb-3 ${
                  contest.type === 'race'
                    ? 'bg-blue-100 text-blue-800'
                    : 'bg-purple-100 text-purple-800'
                }`}
              >
                {contest.type === 'race' ? 'Race' : 'Measure'}
              </span>
              <h1 className="text-4xl font-bold text-gray-900">{contest.title}</h1>
              {contest.office && (
                <p className="text-xl text-gray-600 mt-2">Office: {contest.office}</p>
              )}
              {contest.jurisdiction && (
                <p className="text-gray-600 mt-1">Jurisdiction: {contest.jurisdiction}</p>
              )}
            </div>
          </div>

          {contest.description && (
            <p className="text-gray-700 mt-4 leading-relaxed">{contest.description}</p>
          )}

          {contest.seat_count && contest.seat_count > 1 && (
            <div className="mt-4 bg-blue-50 border border-blue-200 rounded-md p-4">
              <p className="text-blue-900 font-medium">
                Note: This is a multi-seat race. You may vote for up to {contest.seat_count}{' '}
                candidates.
              </p>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content - 2 columns */}
          <div className="lg:col-span-2 space-y-8">
            {/* Candidates Section */}
            <section>
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Candidates ({activeCandidates.length})
              </h2>

              {candidatesLoading && <LoadingSpinner message="Loading candidates..." />}

              {activeCandidates.length > 0 ? (
                <div className="grid gap-4">
                  {activeCandidates.map((candidate) => (
                    <CandidateCard key={candidate.id} candidate={candidate} />
                  ))}
                </div>
              ) : (
                <div className="bg-gray-50 rounded-lg p-6 text-center text-gray-600">
                  No active candidates yet.
                </div>
              )}
            </section>

            {/* Questions Section */}
            <section>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">
                  Questions ({questions.length})
                </h2>
                {isAuthenticated && (
                  <button
                    onClick={() => setShowQuestionForm(!showQuestionForm)}
                    className="px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all font-medium flex items-center gap-2 shadow-sm"
                  >
                    {!showQuestionForm && (
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
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
                <div className="space-y-4">
                  {questions.map((question) => (
                    <QuestionCard key={question.id} question={question} />
                  ))}
                </div>
              ) : (
                <div className="bg-gray-50 rounded-lg p-8 text-center text-gray-600">
                  <p>No questions yet. Be the first to ask!</p>
                  {!isAuthenticated && (
                    <Link to="/login" className="text-civic-blue hover:underline mt-2 inline-block">
                      Log in to submit a question
                    </Link>
                  )}
                </div>
              )}
            </section>
          </div>

          {/* Sidebar - 1 column */}
          <div className="space-y-6">
            {/* Quick Stats */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Contest Stats</h3>
              <div className="space-y-3">
                <StatRow label="Candidates" value={activeCandidates.length} />
                <StatRow label="Questions" value={questions.length} />
                <StatRow
                  label="Total Answers"
                  value={
                    activeCandidates.reduce(
                      (sum, c) => sum + (c.video_answers?.length || 0),
                      0
                    )
                  }
                />
              </div>
            </div>

            {/* Actions */}
            <div className="bg-blue-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Take Action</h3>
              <div className="space-y-3">
                {isAuthenticated ? (
                  <>
                    <button
                      onClick={() => setShowQuestionForm(true)}
                      className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all flex items-center justify-center gap-2 shadow-sm"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
                      </svg>
                      Ask a Question with AI
                    </button>
                    <p className="text-sm text-gray-600">
                      Get AI-powered help crafting great questions that matter to voters
                    </p>
                  </>
                ) : (
                  <>
                    <Link
                      to="/login"
                      className="block w-full px-4 py-2 bg-civic-blue text-white rounded-lg hover:bg-blue-700 transition-colors text-center"
                    >
                      Login to Participate
                    </Link>
                    <p className="text-sm text-gray-600">
                      Log in to ask questions and vote
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

// Helper Component
const StatRow: React.FC<{ label: string; value: number }> = ({ label, value }) => (
  <div className="flex justify-between items-center">
    <span className="text-gray-600">{label}</span>
    <span className="text-lg font-semibold text-gray-900">{value}</span>
  </div>
);

export default ContestPage;
