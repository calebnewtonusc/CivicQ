import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import LoadingSpinner from '../components/LoadingSpinner';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/axios';
import {
  QuestionMarkCircleIcon,
  CheckCircleIcon,
  ClockIcon,
  XCircleIcon,
  PlusIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';

type Question = {
  id: number;
  content: string;
  city_name: string;
  contest_name: string;
  status: 'pending' | 'approved' | 'rejected';
  created_at: string;
  answer_count: number;
  views: number;
  rejection_reason?: string;
};

export default function MyQuestionsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('all');

  const { data: questions, isLoading, error } = useQuery({
    queryKey: ['my-questions', filter],
    queryFn: async () => {
      const params = filter !== 'all' ? `?status=${filter}` : '';
      const response = await api.get(`/users/me/questions${params}`);
      return response.data;
    },
    enabled: !!user
  });

  if (!user) {
    navigate('/login');
    return null;
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'approved':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-full">
            <CheckCircleIcon className="h-4 w-4" />
            Approved
          </span>
        );
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full">
            <ClockIcon className="h-4 w-4" />
            Pending Review
          </span>
        );
      case 'rejected':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
            <XCircleIcon className="h-4 w-4" />
            Rejected
          </span>
        );
      default:
        return null;
    }
  };

  const filteredQuestions = questions || [];

  return (
    <>
      <Helmet>
        <title>My Questions - CivicQ</title>
        <meta name="description" content="View and manage your submitted questions to candidates" />
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        <Navbar />

        <main className="pt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {/* Header */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
                    My Questions
                  </h1>
                  <p className="text-gray-600">
                    Track and manage all questions you've submitted to candidates
                  </p>
                </div>
                <Link
                  to="/ballot"
                  className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  <PlusIcon className="h-5 w-5" />
                  <span className="hidden sm:inline">Submit New Question</span>
                  <span className="sm:hidden">New</span>
                </Link>
              </div>

              {/* Filter Tabs */}
              <div className="border-b border-gray-200">
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
                    {questions && (
                      <span className="ml-2 px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">
                        {questions.length}
                      </span>
                    )}
                  </button>
                  <button
                    onClick={() => setFilter('approved')}
                    className={`py-4 px-2 font-medium text-sm border-b-2 transition-colors whitespace-nowrap ${
                      filter === 'approved'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Approved
                    {questions && (
                      <span className="ml-2 px-2 py-0.5 bg-green-100 text-green-600 text-xs rounded-full">
                        {questions.filter((q: Question) => q.status === 'approved').length}
                      </span>
                    )}
                  </button>
                  <button
                    onClick={() => setFilter('pending')}
                    className={`py-4 px-2 font-medium text-sm border-b-2 transition-colors whitespace-nowrap ${
                      filter === 'pending'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Pending
                    {questions && (
                      <span className="ml-2 px-2 py-0.5 bg-yellow-100 text-yellow-600 text-xs rounded-full">
                        {questions.filter((q: Question) => q.status === 'pending').length}
                      </span>
                    )}
                  </button>
                  <button
                    onClick={() => setFilter('rejected')}
                    className={`py-4 px-2 font-medium text-sm border-b-2 transition-colors whitespace-nowrap ${
                      filter === 'rejected'
                        ? 'border-blue-600 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    Rejected
                    {questions && (
                      <span className="ml-2 px-2 py-0.5 bg-red-100 text-red-600 text-xs rounded-full">
                        {questions.filter((q: Question) => q.status === 'rejected').length}
                      </span>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Questions List */}
            {isLoading ? (
              <div className="flex justify-center py-12">
                <LoadingSpinner />
              </div>
            ) : error ? (
              <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
                <p className="text-red-800 font-medium mb-2">Failed to load questions</p>
                <p className="text-red-600 text-sm">Please try again later</p>
              </div>
            ) : filteredQuestions.length > 0 ? (
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
                            to={question.status === 'approved' ? `/question/${question.id}` : '#'}
                            className={`text-xl font-semibold ${
                              question.status === 'approved'
                                ? 'text-gray-900 hover:text-blue-600'
                                : 'text-gray-700 cursor-default'
                            } transition-colors`}
                          >
                            {question.content}
                          </Link>
                        </div>
                        {getStatusBadge(question.status)}
                      </div>

                      <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-4">
                        <span className="flex items-center gap-1">
                          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                            />
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                            />
                          </svg>
                          {question.city_name}
                        </span>
                        <span>•</span>
                        <span>{question.contest_name}</span>
                        <span>•</span>
                        <span className="text-gray-500">
                          {new Date(question.created_at).toLocaleDateString()}
                        </span>
                      </div>

                      {question.status === 'rejected' && question.rejection_reason && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
                          <p className="text-sm font-medium text-red-800 mb-1">Rejection Reason:</p>
                          <p className="text-sm text-red-700">{question.rejection_reason}</p>
                        </div>
                      )}

                      {question.status === 'pending' && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                          <p className="text-sm text-yellow-800">
                            <ClockIcon className="h-4 w-4 inline mr-1" />
                            Your question is being reviewed by moderators. You'll be notified once it's approved.
                          </p>
                        </div>
                      )}

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span className="flex items-center gap-1">
                            <ChatBubbleLeftRightIcon className="h-4 w-4" />
                            {question.answer_count} answer{question.answer_count !== 1 ? 's' : ''}
                          </span>
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
                            {question.views} view{question.views !== 1 ? 's' : ''}
                          </span>
                        </div>

                        {question.status === 'approved' && (
                          <Link
                            to={`/question/${question.id}`}
                            className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                          >
                            View Answers →
                          </Link>
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
                    : filter === 'approved'
                    ? 'No approved questions'
                    : filter === 'pending'
                    ? 'No pending questions'
                    : 'No rejected questions'}
                </h3>
                <p className="text-gray-600 mb-6">
                  {filter === 'all'
                    ? 'Submit your first question to candidates in your area'
                    : `You don't have any ${filter} questions at the moment`}
                </p>
                <Link
                  to="/ballot"
                  className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <PlusIcon className="h-5 w-5" />
                  Submit a Question
                </Link>
              </div>
            )}
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
}
