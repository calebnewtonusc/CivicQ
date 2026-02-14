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

const ContestPage: React.FC = () => {
  const { contestId } = useParams<{ contestId: string }>();
  const { user, isAuthenticated } = useAuthContext();
  const [showQuestionForm, setShowQuestionForm] = useState(false);
  const [questionText, setQuestionText] = useState('');
  const [questionContext, setQuestionContext] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  const contestIdNum = contestId ? parseInt(contestId) : undefined;

  const { data: contest, isLoading: contestLoading, error: contestError } = useContest(contestIdNum);
  const { data: candidates, isLoading: candidatesLoading } = useContestCandidates(contestIdNum);
  const {
    data: questionsData,
    isLoading: questionsLoading,
    refetch: refetchQuestions,
  } = useContestQuestions(contestIdNum, { status: 'approved', page_size: 50 });

  const createQuestionMutation = useCreateQuestion();

  const handleSubmitQuestion = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!contestIdNum || !questionText.trim()) return;

    try {
      await createQuestionMutation.mutateAsync({
        contest_id: contestIdNum,
        question_text: questionText,
        issue_tags: selectedTags,
        context: questionContext || undefined,
      });

      setQuestionText('');
      setQuestionContext('');
      setSelectedTags([]);
      setShowQuestionForm(false);
      refetchQuestions();
    } catch (error) {
      console.error('Failed to submit question:', error);
    }
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
                    className="px-4 py-2 bg-civic-blue text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
                  >
                    {showQuestionForm ? 'Cancel' : 'Ask Question'}
                  </button>
                )}
              </div>

              {/* Question Form */}
              {showQuestionForm && (
                <form
                  onSubmit={handleSubmitQuestion}
                  className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6"
                >
                  <h3 className="text-lg font-semibold mb-4">Submit a Question</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Your Question
                      </label>
                      <textarea
                        value={questionText}
                        onChange={(e) => setQuestionText(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-civic-blue focus:border-transparent"
                        rows={3}
                        placeholder="What would you like to know from the candidates?"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Context (Optional)
                      </label>
                      <textarea
                        value={questionContext}
                        onChange={(e) => setQuestionContext(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-civic-blue focus:border-transparent"
                        rows={2}
                        placeholder="Why does this question matter to you?"
                      />
                    </div>
                    <div className="flex justify-end space-x-3">
                      <button
                        type="button"
                        onClick={() => setShowQuestionForm(false)}
                        className="px-4 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                      >
                        Cancel
                      </button>
                      <button
                        type="submit"
                        disabled={createQuestionMutation.isPending}
                        className="px-6 py-2 bg-civic-blue text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
                      >
                        {createQuestionMutation.isPending ? 'Submitting...' : 'Submit Question'}
                      </button>
                    </div>
                  </div>
                </form>
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
                      className="w-full px-4 py-2 bg-civic-blue text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Ask a Question
                    </button>
                    <p className="text-sm text-gray-600">
                      Vote on questions to help surface the most important issues
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
