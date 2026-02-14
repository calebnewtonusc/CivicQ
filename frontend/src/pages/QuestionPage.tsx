import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuestion, useQuestionVideoAnswers } from '../hooks/useQuestions';
import { useVote } from '../hooks/useVoting';
import { useAuthContext } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import VideoPlayer from '../components/VideoPlayer';
import VoteButton from '../components/VoteButton';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { VideoAnswer } from '../types';

const QuestionPage: React.FC = () => {
  const { questionId } = useParams<{ questionId: string }>();
  const { isAuthenticated } = useAuthContext();
  const [selectedAnswer, setSelectedAnswer] = useState<VideoAnswer | null>(null);

  const questionIdNum = questionId ? parseInt(questionId) : undefined;

  const {
    data: question,
    isLoading: questionLoading,
    error: questionError,
  } = useQuestion(questionIdNum);

  const {
    data: videoAnswers,
    isLoading: answersLoading,
  } = useQuestionVideoAnswers(questionIdNum);

  const { currentVote } = useVote(questionIdNum);

  if (questionLoading) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <LoadingSpinner size="lg" message="Loading question..." />
        </div>
      </Layout>
    );
  }

  if (questionError || !question) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <ErrorMessage message="Failed to load question. Please try again." />
        </div>
      </Layout>
    );
  }

  const publishedAnswers = videoAnswers?.filter((a) => a.status === 'published') || [];
  const netVotes = question.upvotes - question.downvotes;

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Question Header */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-start space-x-6">
            {/* Vote Section */}
            <div className="flex-shrink-0">
              <VoteButton questionId={question.id} />
            </div>

            {/* Question Content */}
            <div className="flex-1">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <h1 className="text-3xl font-bold text-gray-900 mb-3">
                    {question.question_text}
                  </h1>

                  {/* Tags */}
                  {question.issue_tags && question.issue_tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {question.issue_tags.map((tag) => (
                        <span
                          key={tag}
                          className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                        >
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Context */}
                  {question.context && (
                    <div className="bg-gray-50 border-l-4 border-civic-blue p-4 mb-4">
                      <p className="text-sm font-medium text-gray-900 mb-1">Context</p>
                      <p className="text-gray-700 italic">{question.context}</p>
                    </div>
                  )}
                </div>

                <span
                  className={`ml-4 px-3 py-1 rounded-full text-sm font-medium ${
                    question.status === 'approved'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {question.status}
                </span>
              </div>

              {/* Stats */}
              <div className="flex items-center space-x-6 text-sm text-gray-600 border-t border-gray-200 pt-4">
                <div className="flex items-center">
                  <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                  </svg>
                  <span className="font-medium">{netVotes}</span> votes
                </div>
                <div className="flex items-center">
                  <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <span className="font-medium">{publishedAnswers.length}</span> answer
                  {publishedAnswers.length !== 1 ? 's' : ''}
                </div>
                {currentVote && (
                  <div className="flex items-center text-civic-green">
                    <svg className="w-5 h-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    You voted on this
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Video Answers Section */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Answer List - Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            <h2 className="text-xl font-bold text-gray-900">Candidate Answers</h2>

            {answersLoading && <LoadingSpinner message="Loading answers..." />}

            {publishedAnswers.length > 0 ? (
              <div className="space-y-3">
                {publishedAnswers.map((answer) => (
                  <button
                    key={answer.id}
                    onClick={() => setSelectedAnswer(answer)}
                    className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                      selectedAnswer?.id === answer.id
                        ? 'border-civic-blue bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300 bg-white'
                    }`}
                  >
                    <div className="flex items-start space-x-3">
                      {answer.candidate?.photo_url ? (
                        <img
                          src={answer.candidate.photo_url}
                          alt={answer.candidate.name}
                          className="w-10 h-10 rounded-full object-cover"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-sm font-bold">
                          {answer.candidate?.name.charAt(0)}
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">
                          {answer.candidate?.name || 'Unknown'}
                        </p>
                        <p className="text-xs text-gray-500">
                          {Math.floor(answer.duration / 60)}:{(answer.duration % 60).toFixed(0).padStart(2, '0')}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="bg-gray-50 rounded-lg p-6 text-center text-gray-600 text-sm">
                No answers yet. Candidates will be notified of this question.
              </div>
            )}
          </div>

          {/* Video Player - Main Content */}
          <div className="lg:col-span-3">
            {selectedAnswer ? (
              <div>
                <div className="mb-4">
                  <Link
                    to={`/candidate/${selectedAnswer.candidate_id}`}
                    className="inline-flex items-center text-lg font-semibold text-gray-900 hover:text-civic-blue"
                  >
                    {selectedAnswer.candidate?.name || 'Unknown Candidate'}
                    <svg className="w-5 h-5 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </Link>
                </div>
                <VideoPlayer answer={selectedAnswer} />

                {/* Answer Metadata */}
                <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Answer Details</h3>

                  {selectedAnswer.rationale && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Rationale</h4>
                      <p className="text-gray-600">{selectedAnswer.rationale}</p>
                    </div>
                  )}

                  {selectedAnswer.implementation_plan && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Implementation Plan</h4>
                      <p className="text-gray-600">{selectedAnswer.implementation_plan}</p>
                    </div>
                  )}

                  {selectedAnswer.tradeoff_acknowledged && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Tradeoffs Acknowledged</h4>
                      <p className="text-gray-600">{selectedAnswer.tradeoff_acknowledged}</p>
                    </div>
                  )}

                  {selectedAnswer.measurement_criteria && (
                    <div className="mb-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Success Metrics</h4>
                      <p className="text-gray-600">{selectedAnswer.measurement_criteria}</p>
                    </div>
                  )}

                  {selectedAnswer.values_statement && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-1">Values Statement</h4>
                      <p className="text-gray-600">{selectedAnswer.values_statement}</p>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="bg-gray-50 rounded-lg p-12 text-center">
                <svg
                  className="mx-auto h-16 w-16 text-gray-400 mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Select a candidate to watch their answer
                </h3>
                <p className="text-gray-600">
                  Choose from the list on the left to see their video response
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Call to Action */}
        {!isAuthenticated && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Want to vote on this question?
              </h3>
              <p className="text-gray-600 mb-4">
                Log in to upvote or downvote questions and help surface the most important issues
              </p>
              <Link
                to="/login"
                className="inline-block px-6 py-2 bg-civic-blue text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Login to Vote
              </Link>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default QuestionPage;
