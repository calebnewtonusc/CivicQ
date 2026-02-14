import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import { useQuery } from '@tantml:invoke>react-query';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import QuestionCard from '../components/QuestionCard';
import LoadingSpinner from '../components/LoadingSpinner';
import api from '../api/axios';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  ClockIcon,
  FireIcon,
  CheckCircleIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';

type Question = {
  id: number;
  content: string;
  city_id: number;
  city_name: string;
  contest_id: number;
  contest_name: string;
  author: {
    id: number;
    username: string;
  };
  created_at: string;
  status: 'pending' | 'approved' | 'rejected';
  answer_count: number;
  views: number;
};

type SortOption = 'recent' | 'popular' | 'unanswered';
type StatusFilter = 'all' | 'approved' | 'pending' | 'rejected';

export default function QuestionsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<SortOption>('recent');
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('approved');
  const [showFilters, setShowFilters] = useState(false);

  const { data: questions, isLoading, error } = useQuery({
    queryKey: ['questions', { search: searchQuery, sort: sortBy, status: statusFilter }],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchQuery) params.append('search', searchQuery);
      params.append('sort', sortBy);
      if (statusFilter !== 'all') params.append('status', statusFilter);

      const response = await api.get(`/questions?${params.toString()}`);
      return response.data;
    }
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
  };

  const sortOptions = [
    { value: 'recent', label: 'Most Recent', icon: ClockIcon },
    { value: 'popular', label: 'Most Popular', icon: FireIcon },
    { value: 'unanswered', label: 'Unanswered', icon: CheckCircleIcon }
  ];

  return (
    <>
      <Helmet>
        <title>Browse Questions - CivicQ</title>
        <meta
          name="description"
          content="Browse and search questions submitted by voters to candidates. See which issues matter most to your community."
        />
        <meta property="og:title" content="Browse All Questions - CivicQ" />
        <meta
          property="og:description"
          content="Explore questions voters are asking candidates. Filter by topic, location, and popularity."
        />
        <meta property="og:type" content="website" />
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        <Navbar />

        <main className="pt-16">
          {/* Hero Section */}
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 text-white py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center">
                <h1 className="text-4xl md:text-5xl font-bold mb-4">
                  Explore Voter Questions
                </h1>
                <p className="text-xl text-blue-100 max-w-2xl mx-auto">
                  See what issues matter most to voters across the country
                </p>
              </div>
            </div>
          </div>

          {/* Search and Filter Bar */}
          <div className="bg-white border-b border-gray-200 sticky top-16 z-10 shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="flex flex-col md:flex-row gap-4">
                {/* Search */}
                <form onSubmit={handleSearch} className="flex-grow">
                  <div className="relative">
                    <MagnifyingGlassIcon
                      className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400"
                      aria-hidden="true"
                    />
                    <input
                      type="text"
                      placeholder="Search questions by keyword, topic, or candidate..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                    {searchQuery && (
                      <button
                        type="button"
                        onClick={() => setSearchQuery('')}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                      >
                        <XMarkIcon className="h-5 w-5" />
                      </button>
                    )}
                  </div>
                </form>

                {/* Sort */}
                <div className="flex gap-2">
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as SortOption)}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                  >
                    {sortOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>

                  <button
                    onClick={() => setShowFilters(!showFilters)}
                    className={`px-4 py-2 border rounded-lg flex items-center gap-2 transition-colors ${
                      showFilters
                        ? 'bg-blue-50 border-blue-300 text-blue-700'
                        : 'border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    <FunnelIcon className="h-5 w-5" />
                    <span className="hidden sm:inline">Filters</span>
                  </button>
                </div>
              </div>

              {/* Filters Panel */}
              {showFilters && (
                <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div className="grid md:grid-cols-3 gap-4">
                    {/* Status Filter */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Status
                      </label>
                      <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                      >
                        <option value="all">All Questions</option>
                        <option value="approved">Approved Only</option>
                        <option value="pending">Pending Review</option>
                        <option value="rejected">Rejected</option>
                      </select>
                    </div>

                    {/* City Filter (placeholder for future) */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Location
                      </label>
                      <select
                        disabled
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-500 cursor-not-allowed"
                      >
                        <option>All Cities</option>
                      </select>
                    </div>

                    {/* Contest Type Filter (placeholder for future) */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Office Type
                      </label>
                      <select
                        disabled
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-500 cursor-not-allowed"
                      >
                        <option>All Offices</option>
                      </select>
                    </div>
                  </div>

                  <div className="mt-4 flex justify-end">
                    <button
                      onClick={() => {
                        setSearchQuery('');
                        setSortBy('recent');
                        setStatusFilter('approved');
                      }}
                      className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Clear All Filters
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Questions List */}
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {isLoading ? (
              <div className="flex justify-center py-12">
                <LoadingSpinner />
              </div>
            ) : error ? (
              <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
                <p className="text-red-800 font-medium mb-2">Failed to load questions</p>
                <p className="text-red-600 text-sm">Please try again later</p>
              </div>
            ) : questions && questions.length > 0 ? (
              <div>
                <div className="mb-6 flex items-center justify-between">
                  <p className="text-gray-600">
                    Showing <span className="font-semibold">{questions.length}</span> question
                    {questions.length !== 1 ? 's' : ''}
                  </p>
                </div>

                <div className="grid gap-6">
                  {questions.map((question: Question) => (
                    <div key={question.id} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                      <div className="p-6">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex-grow">
                            <Link
                              to={`/question/${question.id}`}
                              className="text-xl font-semibold text-gray-900 hover:text-blue-600 transition-colors"
                            >
                              {question.content}
                            </Link>
                          </div>
                          {question.status === 'pending' && (
                            <span className="ml-3 px-3 py-1 bg-yellow-100 text-yellow-800 text-xs font-medium rounded-full whitespace-nowrap">
                              Pending Review
                            </span>
                          )}
                          {question.status === 'rejected' && (
                            <span className="ml-3 px-3 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full whitespace-nowrap">
                              Rejected
                            </span>
                          )}
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
                          <span>
                            {question.answer_count} answer{question.answer_count !== 1 ? 's' : ''}
                          </span>
                          <span>•</span>
                          <span className="text-gray-500">
                            {new Date(question.created_at).toLocaleDateString()}
                          </span>
                        </div>

                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2 text-sm text-gray-600">
                            <span>Asked by</span>
                            <span className="font-medium text-gray-900">
                              {question.author.username}
                            </span>
                          </div>

                          <Link
                            to={`/question/${question.id}`}
                            className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                          >
                            View Answers →
                          </Link>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
                <MagnifyingGlassIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No questions found</h3>
                <p className="text-gray-600 mb-6">
                  {searchQuery
                    ? 'Try adjusting your search or filters'
                    : 'Be the first to ask a question to candidates!'}
                </p>
                <Link
                  to="/ballot"
                  className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Find Your Ballot
                </Link>
              </div>
            )}
          </div>

          {/* CTA Section */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 py-12 mt-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
              <h2 className="text-3xl font-bold text-white mb-4">
                Have a Question for Your Candidates?
              </h2>
              <p className="text-xl text-blue-100 mb-6 max-w-2xl mx-auto">
                Submit your question and get direct video answers from candidates running in your area
              </p>
              <Link
                to="/ballot"
                className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50 transition-colors"
              >
                Submit a Question
              </Link>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
}
