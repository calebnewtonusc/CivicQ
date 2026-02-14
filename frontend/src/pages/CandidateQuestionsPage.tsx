import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import LoadingSpinner from '../components/LoadingSpinner';
import api from '../api/axios';
import {
  CheckCircleIcon,
  ClockIcon,
  XCircleIcon,
  VideoCameraIcon,
  QuestionMarkCircleIcon
} from '@heroicons/react/24/outline';

type Question = {
  id: number;
  content: string;
  created_at: string;
  answer: {
    id: number;
    video_url: string;
    created_at: string;
  } | null;
  status: 'pending' | 'answered' | 'unanswered';
  views: number;
};

export default function CandidateQuestionsPage() {
  const { candidateId } = useParams<{ candidateId: string }>();
  const [filter, setFilter] = useState<'all' | 'answered' | 'unanswered'>('all');

  const { data: candidate, isLoading: candidateLoading } = useQuery({
    queryKey: ['candidate', candidateId],
    queryFn: async () => {
      const response = await api.get(`/candidates/${candidateId}`);
      return response.data;
    }
  });

  const { data: questions, isLoading: questionsLoading } = useQuery({
    queryKey: ['candidate-questions', candidateId, filter],
    queryFn: async () => {
      const params = filter !== 'all' ? `?status=${filter}` : '';
      const response = await api.get(`/candidates/${candidateId}/questions${params}`);
      return response.data;
    }
  });

  const isLoading = candidateLoading || questionsLoading;

  const getStatusBadge = (question: Question) => {
    if (question.answer) {
      return (
        <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
          <CheckCircleIcon className="h-4 w-4" />
          Answered
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
        <ClockIcon className="h-4 w-4" />
        Unanswered
      </span>
    );
  };

  const filteredQuestions = questions || [];
  const answeredCount = filteredQuestions.filter((q: Question) => q.answer).length;
  const unansweredCount = filteredQuestions.filter((q: Question) => !q.answer).length;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <>
      <Helmet>
        <title>Questions - {candidate?.full_name} - CivicQ</title>
        <meta
          name="description"
          content={`View all questions and video answers from ${candidate?.full_name}`}
        />
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        <Navbar />

        <main className="pt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Header */}
            <div className="mb-8">
              <nav className="text-sm text-gray-600 mb-4">
                <Link to={`/candidate/${candidateId}`} className="hover:text-blue-600">
                  {candidate?.full_name}
                </Link>
                <span className="mx-2">→</span>
                <span className="text-gray-900">Questions & Answers</span>
              </nav>

              <div className="flex items-start justify-between mb-6">
                <div>
                  <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                    Questions & Answers
                  </h1>
                  <p className="text-gray-600">
                    {candidate?.full_name} • {candidate?.party} • {candidate?.contest_name}
                  </p>
                </div>
                <Link
                  to={`/candidate/${candidateId}`}
                  className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                >
                  Back to Profile
                </Link>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="text-2xl font-bold text-blue-600">{filteredQuestions.length}</div>
                  <div className="text-sm text-gray-600">Total Questions</div>
                </div>
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="text-2xl font-bold text-green-600">{answeredCount}</div>
                  <div className="text-sm text-gray-600">Answered</div>
                </div>
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="text-2xl font-bold text-yellow-600">{unansweredCount}</div>
                  <div className="text-sm text-gray-600">Unanswered</div>
                </div>
                <div className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="text-2xl font-bold text-purple-600">
                    {answeredCount > 0 ? Math.round((answeredCount / filteredQuestions.length) * 100) : 0}%
                  </div>
                  <div className="text-sm text-gray-600">Response Rate</div>
                </div>
              </div>

              {/* Filter Tabs */}
              <div className="border-b border-gray-200 mt-6">
                <div className="flex space-x-8 overflow-x-auto">
                  <button
                    onClick={() => setFilter('all')}
                    className={`py-4 px-2 font-medium text-sm border-b-2 transition-colors whitespace-nowrap ${
                      filter === 'all'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    All Questions
                    <span className="ml-2 px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">
                      {filteredQuestions.length}
                    </span>
                  </button>
                  <button
                    onClick={() => setFilter('answered')}
                    className={`py-4 px-2 font-medium text-sm border-b-2 transition-colors whitespace-nowrap ${
                      filter === 'answered'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Answered
                    <span className="ml-2 px-2 py-0.5 bg-green-100 text-green-600 text-xs rounded-full">
                      {answeredCount}
                    </span>
                  </button>
                  <button
                    onClick={() => setFilter('unanswered')}
                    className={`py-4 px-2 font-medium text-sm border-b-2 transition-colors whitespace-nowrap ${
                      filter === 'unanswered'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Unanswered
                    <span className="ml-2 px-2 py-0.5 bg-yellow-100 text-yellow-600 text-xs rounded-full">
                      {unansweredCount}
                    </span>
                  </button>
                </div>
              </div>
            </div>

            {/* Questions List */}
            {filteredQuestions.length > 0 ? (
              <div className="space-y-6">
                {filteredQuestions.map((question: Question) => (
                  <div
                    key={question.id}
                    className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden hover:shadow-md transition-shadow"
                  >
                    <div className="p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-grow pr-4">
                          <Link
                            to={`/question/${question.id}`}
                            className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition-colors"
                          >
                            {question.content}
                          </Link>
                        </div>
                        {getStatusBadge(question)}
                      </div>

                      <div className="flex items-center gap-4 text-sm text-gray-600 mb-4">
                        <span className="text-gray-500">
                          Asked {new Date(question.created_at).toLocaleDateString()}
                        </span>
                        {question.answer && (
                          <>
                            <span>•</span>
                            <span className="text-green-600">
                              Answered {new Date(question.answer.created_at).toLocaleDateString()}
                            </span>
                          </>
                        )}
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                            />
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
                            />
                          </svg>
                          {question.views} views
                        </span>
                      </div>

                      <div className="flex items-center justify-between">
                        {question.answer ? (
                          <Link
                            to={`/question/${question.id}`}
                            className="flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium text-sm"
                          >
                            <VideoCameraIcon className="h-5 w-5" />
                            Watch Video Answer →
                          </Link>
                        ) : (
                          <div className="text-sm text-gray-500 italic">
                            Waiting for candidate to respond
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
                <QuestionMarkCircleIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {filter === 'all'
                    ? 'No questions yet'
                    : filter === 'answered'
                    ? 'No answered questions yet'
                    : 'No unanswered questions'}
                </h3>
                <p className="text-gray-600">
                  {filter === 'all'
                    ? 'Be the first to ask this candidate a question!'
                    : filter === 'answered'
                    ? 'This candidate hasn\'t answered any questions yet'
                    : 'All questions have been answered'}
                </p>
              </div>
            )}
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
}
