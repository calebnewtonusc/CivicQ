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
        <div className="container mx-auto px-4 py-8 min-h-screen flex items-center justify-center">
          <div className="text-center animate-fadeIn">
            <div className="w-20 h-20 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
            <LoadingSpinner size="lg" message="Loading question..." />
          </div>
        </div>
      </Layout>
    );
  }

  if (questionError || !question) {
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
              <h3 className="text-xl font-bold text-gray-900 mb-2">Unable to Load Question</h3>
              <ErrorMessage message="Failed to load question. Please try again." />
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  const publishedAnswers = videoAnswers?.filter((a) => a.status === 'published') || [];
  const netVotes = question.upvotes - question.downvotes;

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8 animate-fadeIn">
        {/* Question Header - Reddit-style post */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden mb-8">
          <div className="flex">
            {/* Vote Section - Reddit-style left sidebar */}
            <div className="bg-gray-50 border-r border-gray-200 p-4 flex flex-col items-center">
              <VoteButton questionId={question.id} />
            </div>

            {/* Question Content */}
            <div className="flex-1 p-8">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  {/* Status badge */}
                  <div className="flex items-center gap-2 mb-4">
                    <span
                      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-bold ${
                        question.status === 'approved'
                          ? 'bg-green-100 text-green-800 border border-green-200'
                          : 'bg-yellow-100 text-yellow-800 border border-yellow-200'
                      }`}
                    >
                      {question.status === 'approved' && (
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      )}
                      {question.status}
                    </span>

                    {/* Vote count badge */}
                    <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-bold border border-blue-200">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                      </svg>
                      {netVotes} {netVotes === 1 ? 'vote' : 'votes'}
                    </span>

                    {currentVote && (
                      <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-bold border border-green-200">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        You Voted
                      </span>
                    )}
                  </div>

                  <h1 className="text-4xl font-extrabold text-gray-900 mb-6 leading-tight">
                    {question.question_text}
                  </h1>

                  {/* Tags */}
                  {question.issue_tags && question.issue_tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-6">
                      {question.issue_tags.map((tag) => (
                        <span
                          key={tag}
                          className="inline-flex items-center px-3 py-1.5 rounded-lg text-sm font-semibold bg-gradient-to-r from-blue-50 to-indigo-50 text-blue-700 border border-blue-200 hover:border-blue-300 transition-colors"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Context */}
                  {question.context && (
                    <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 rounded-lg p-5 mb-6">
                      <div className="flex items-start gap-3">
                        <svg className="w-5 h-5 text-blue-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <div>
                          <p className="text-sm font-bold text-blue-900 mb-1">Additional Context</p>
                          <p className="text-gray-700 leading-relaxed">{question.context}</p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Stats Bar */}
                  <div className="flex items-center gap-6 text-sm text-gray-600 border-t border-gray-200 pt-4">
                    <div className="flex items-center gap-2">
                      <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      <span className="font-semibold">{publishedAnswers.length}</span>
                      <span>Candidate {publishedAnswers.length === 1 ? 'Answer' : 'Answers'}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Video Answers Section */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Answer List - Sidebar - YouTube-style */}
          <div className="lg:col-span-1 space-y-4 lg:sticky lg:top-24 self-start">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <h2 className="text-xl font-bold text-gray-900">Candidate Answers</h2>
            </div>

            {answersLoading && (
              <div className="flex justify-center py-4">
                <LoadingSpinner message="Loading answers..." />
              </div>
            )}

            {publishedAnswers.length > 0 ? (
              <div className="space-y-3">
                {publishedAnswers.map((answer, index) => (
                  <button
                    key={answer.id}
                    onClick={() => setSelectedAnswer(answer)}
                    className={`group w-full text-left p-4 rounded-xl border-2 transition-all animate-fadeIn ${
                      selectedAnswer?.id === answer.id
                        ? 'border-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50 shadow-lg'
                        : 'border-gray-200 hover:border-blue-300 bg-white hover:shadow-md'
                    }`}
                    style={{ animationDelay: `${index * 0.05}s` }}
                  >
                    <div className="flex items-start space-x-3">
                      {answer.candidate?.photo_url ? (
                        <img
                          src={answer.candidate.photo_url}
                          alt={answer.candidate.name}
                          className="w-12 h-12 rounded-full object-cover border-2 border-gray-200 group-hover:border-blue-400 transition-colors"
                        />
                      ) : (
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center text-sm font-bold text-gray-600">
                          {answer.candidate?.name.charAt(0)}
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-gray-900 truncate group-hover:text-blue-600 transition-colors">
                          {answer.candidate?.name || 'Unknown'}
                        </p>
                        <div className="flex items-center gap-2 mt-1">
                          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <p className="text-sm text-gray-500 font-medium">
                            {Math.floor(answer.duration / 60)}:{(answer.duration % 60).toFixed(0).padStart(2, '0')}
                          </p>
                        </div>
                      </div>
                      {selectedAnswer?.id === answer.id && (
                        <svg className="w-6 h-6 text-blue-600 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              !answersLoading && (
                <div className="bg-gradient-to-br from-gray-50 to-blue-50/30 rounded-xl p-8 text-center border-2 border-dashed border-gray-300">
                  <div className="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                  <p className="text-sm font-semibold text-gray-900 mb-1">No Answers Yet</p>
                  <p className="text-xs text-gray-600">
                    Candidates will be notified of this question
                  </p>
                </div>
              )
            )}
          </div>

          {/* Video Player - Main Content - YouTube-style */}
          <div className="lg:col-span-3">
            {selectedAnswer ? (
              <div className="animate-fadeIn">
                <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden mb-6">
                  <VideoPlayer answer={selectedAnswer} />
                </div>

                <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-6 mb-6">
                  <Link
                    to={`/candidate/${selectedAnswer.candidate_id}`}
                    className="group inline-flex items-center gap-3 mb-4 hover:bg-gray-50 p-3 rounded-xl transition-colors"
                  >
                    {selectedAnswer.candidate?.photo_url ? (
                      <img
                        src={selectedAnswer.candidate.photo_url}
                        alt={selectedAnswer.candidate.name}
                        className="w-12 h-12 rounded-full object-cover border-2 border-gray-200 group-hover:border-blue-400 transition-colors"
                      />
                    ) : (
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center text-lg font-bold text-gray-600">
                        {selectedAnswer.candidate?.name.charAt(0)}
                      </div>
                    )}
                    <div>
                      <p className="text-xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
                        {selectedAnswer.candidate?.name || 'Unknown Candidate'}
                      </p>
                      <p className="text-sm text-gray-600">View full profile</p>
                    </div>
                    <svg className="w-5 h-5 ml-auto text-gray-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </Link>
                </div>

                {/* Answer Metadata - Enhanced accordion-style */}
                <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
                  <div className="bg-gradient-to-r from-gray-50 to-blue-50 px-6 py-4 border-b border-gray-200">
                    <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                      <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      Answer Details
                    </h3>
                  </div>

                  <div className="p-6 space-y-6">
                    {selectedAnswer.rationale && (
                      <div className="p-4 bg-blue-50 rounded-xl border border-blue-100">
                        <h4 className="text-sm font-bold text-blue-900 mb-2 flex items-center gap-2">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                          </svg>
                          Rationale
                        </h4>
                        <p className="text-gray-700 leading-relaxed">{selectedAnswer.rationale}</p>
                      </div>
                    )}

                    {selectedAnswer.implementation_plan && (
                      <div className="p-4 bg-green-50 rounded-xl border border-green-100">
                        <h4 className="text-sm font-bold text-green-900 mb-2 flex items-center gap-2">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                          </svg>
                          Implementation Plan
                        </h4>
                        <p className="text-gray-700 leading-relaxed">{selectedAnswer.implementation_plan}</p>
                      </div>
                    )}

                    {selectedAnswer.tradeoff_acknowledged && (
                      <div className="p-4 bg-yellow-50 rounded-xl border border-yellow-100">
                        <h4 className="text-sm font-bold text-yellow-900 mb-2 flex items-center gap-2">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M3 6a3 3 0 013-3h10a1 1 0 01.8 1.6L14.25 8l2.55 3.4A1 1 0 0116 13H6a1 1 0 00-1 1v3a1 1 0 11-2 0V6z" clipRule="evenodd" />
                          </svg>
                          Tradeoffs Acknowledged
                        </h4>
                        <p className="text-gray-700 leading-relaxed">{selectedAnswer.tradeoff_acknowledged}</p>
                      </div>
                    )}

                    {selectedAnswer.measurement_criteria && (
                      <div className="p-4 bg-purple-50 rounded-xl border border-purple-100">
                        <h4 className="text-sm font-bold text-purple-900 mb-2 flex items-center gap-2">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                          </svg>
                          Success Metrics
                        </h4>
                        <p className="text-gray-700 leading-relaxed">{selectedAnswer.measurement_criteria}</p>
                      </div>
                    )}

                    {selectedAnswer.values_statement && (
                      <div className="p-4 bg-indigo-50 rounded-xl border border-indigo-100">
                        <h4 className="text-sm font-bold text-indigo-900 mb-2 flex items-center gap-2">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                          </svg>
                          Values Statement
                        </h4>
                        <p className="text-gray-700 leading-relaxed">{selectedAnswer.values_statement}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-gradient-to-br from-gray-50 to-blue-50/30 rounded-2xl p-16 text-center border-2 border-dashed border-gray-300">
                <div className="w-24 h-24 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center mx-auto mb-6">
                  <svg
                    className="h-12 w-12 text-gray-400"
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
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-3">
                  Select a Candidate Answer
                </h3>
                <p className="text-lg text-gray-600 max-w-md mx-auto">
                  Choose from the list on the left to watch a candidate's video response
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Call to Action - Enhanced */}
        {!isAuthenticated && (
          <div className="mt-8 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-8 shadow-xl text-white">
            <div className="text-center">
              <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h4.764a2 2 0 011.789 2.894l-3.5 7A2 2 0 0115.263 21h-4.017c-.163 0-.326-.02-.485-.06L7 20m7-10V5a2 2 0 00-2-2h-.095c-.5 0-.905.405-.905.905 0 .714-.211 1.412-.608 2.006L7 11v9m7-10h-2M7 20H5a2 2 0 01-2-2v-6a2 2 0 012-2h2.5" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold mb-3">
                Want to Vote on This Question?
              </h3>
              <p className="text-blue-100 mb-6 max-w-xl mx-auto text-lg">
                Log in to upvote or downvote questions and help surface the most important issues to voters
              </p>
              <Link
                to="/login"
                className="inline-block px-8 py-4 bg-white text-blue-600 rounded-xl hover:bg-blue-50 transition-all font-bold shadow-lg hover:shadow-xl hover:scale-105 transform"
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
