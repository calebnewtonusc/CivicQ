import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { QuestionCardSkeleton } from '../components/SkeletonLoader';
import ErrorMessage from '../components/ErrorMessage';
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
  author: { id: number; username: string };
  created_at: string;
  status: 'pending' | 'approved' | 'rejected';
  answer_count: number;
  views: number;
};

type SortOption = 'recent' | 'popular' | 'unanswered';
type StatusFilter = 'all' | 'approved' | 'pending' | 'rejected';

/* ── FiltersPanel ── */
interface FiltersPanelProps {
  statusFilter: StatusFilter;
  onStatusChange: (v: StatusFilter) => void;
  onClearAll: () => void;
}

const FiltersPanel: React.FC<FiltersPanelProps> = ({ statusFilter, onStatusChange, onClearAll }) => (
  <div className="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
    <div className="grid md:grid-cols-3 gap-4">
      <div>
        <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-2">Status</label>
        <select
          id="status-filter"
          value={statusFilter}
          onChange={(e) => onStatusChange(e.target.value as StatusFilter)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
        >
          <option value="all">All Questions</option>
          <option value="approved">Approved Only</option>
          <option value="pending">Pending Review</option>
          <option value="rejected">Rejected</option>
        </select>
      </div>
      <div>
        <label htmlFor="location-filter" className="block text-sm font-medium text-gray-700 mb-2">Location</label>
        <select id="location-filter" disabled className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-500 cursor-not-allowed">
          <option>All Cities</option>
        </select>
      </div>
      <div>
        <label htmlFor="office-type-filter" className="block text-sm font-medium text-gray-700 mb-2">Office Type</label>
        <select id="office-type-filter" disabled className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-500 cursor-not-allowed">
          <option>All Offices</option>
        </select>
      </div>
    </div>
    <div className="mt-4 flex justify-end">
      <button onClick={onClearAll} className="text-sm text-blue-600 hover:text-blue-700 font-medium">
        Clear All Filters
      </button>
    </div>
  </div>
);

/* ── QuestionListItem ── */
interface QuestionListItemProps {
  question: Question;
  index: number;
}

const QuestionListItem: React.FC<QuestionListItemProps> = ({ question, index }) => (
  <div
    key={question.id}
    className="bg-white rounded-2xl border border-gray-100 shadow-card hover:shadow-card-md hover:-translate-y-0.5 transition-all duration-200 overflow-hidden animate-fade-in"
    style={{ animationDelay: `${index * 0.04}s` }}
  >
    <div className="p-6">
      <div className="flex items-start justify-between mb-3 gap-3">
        <Link to={`/question/${question.id}`} className="text-base font-semibold text-gray-900 hover:text-primary-700 transition-colors leading-snug">
          {question.content}
        </Link>
        {question.status === 'pending' && <span className="badge-yellow flex-shrink-0">Pending</span>}
        {question.status === 'rejected' && <span className="badge-red flex-shrink-0">Rejected</span>}
      </div>
      <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500 mb-4">
        <span className="flex items-center gap-1">
          <svg className="h-3.5 w-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {question.city_name}
        </span>
        <span className="text-gray-200">|</span>
        <span>{question.contest_name}</span>
        <span className="text-gray-200">|</span>
        <span className={question.answer_count > 0 ? 'text-success-600 font-medium' : ''}>
          {question.answer_count} answer{question.answer_count !== 1 ? 's' : ''}
        </span>
        <span className="text-gray-200">|</span>
        <span>{new Date(question.created_at).toLocaleDateString()}</span>
      </div>
      <div className="flex items-center justify-between">
        <span className="text-xs text-gray-400">
          Asked by <span className="font-medium text-gray-600">{question.author.username}</span>
        </span>
        <Link to={`/question/${question.id}`} className="text-xs font-semibold text-primary-600 hover:text-primary-700 transition-colors flex items-center gap-1">
          View Answers
          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Link>
      </div>
    </div>
  </div>
);

/* ── QuestionsPage ── */
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

  const handleSearch = (e: React.FormEvent) => { e.preventDefault(); };

  const sortOptions = [
    { value: 'recent', label: 'Most Recent', icon: ClockIcon },
    { value: 'popular', label: 'Most Popular', icon: FireIcon },
    { value: 'unanswered', label: 'Unanswered', icon: CheckCircleIcon }
  ];

  return (
    <>
      <Helmet>
        <title>Browse Questions - CivicQ</title>
        <meta name="description" content="Browse and search questions submitted by voters to candidates. See which issues matter most to your community." />
        <meta property="og:title" content="Browse All Questions - CivicQ" />
        <meta property="og:description" content="Explore questions voters are asking candidates. Filter by topic, location, and popularity." />
        <meta property="og:type" content="website" />
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        <Navbar />

        <main className="pt-16">
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 text-white py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
              <h1 className="text-4xl md:text-5xl font-bold mb-4">Explore Voter Questions</h1>
              <p className="text-xl text-blue-100 max-w-2xl mx-auto">See what issues matter most to voters across the country</p>
            </div>
          </div>

          <div className="bg-white border-b border-gray-200 sticky top-16 z-10 shadow-sm">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
              <div className="flex flex-col md:flex-row gap-4">
                <form onSubmit={handleSearch} className="flex-grow">
                  <div className="relative">
                    <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" aria-hidden="true" />
                    <input
                      type="text"
                      placeholder="Search questions by keyword, topic, or candidate..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="form-input pl-10"
                    />
                    {searchQuery && (
                      <button type="button" onClick={() => setSearchQuery('')} className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600">
                        <XMarkIcon className="h-5 w-5" />
                      </button>
                    )}
                  </div>
                </form>
                <div className="flex gap-2">
                  <select value={sortBy} onChange={(e) => setSortBy(e.target.value as SortOption)} className="form-input py-2 pr-8">
                    {sortOptions.map((option) => (
                      <option key={option.value} value={option.value}>{option.label}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => setShowFilters(!showFilters)}
                    className={`btn px-4 py-2 border transition-colors text-sm ${showFilters ? 'bg-primary-50 border-primary-300 text-primary-700' : 'border-gray-200 text-gray-600 hover:bg-gray-50'}`}
                  >
                    <FunnelIcon className="h-5 w-5" />
                    <span className="hidden sm:inline">Filters</span>
                  </button>
                </div>
              </div>

              {showFilters && (
                <FiltersPanel
                  statusFilter={statusFilter}
                  onStatusChange={setStatusFilter}
                  onClearAll={() => { setSearchQuery(''); setSortBy('recent'); setStatusFilter('approved'); }}
                />
              )}
            </div>
          </div>

          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            {isLoading ? (
              <div className="space-y-4">
                {['sk-0', 'sk-1', 'sk-2', 'sk-3'].map((id) => <QuestionCardSkeleton key={id} />)}
              </div>
            ) : error ? (
              <ErrorMessage title="Failed to Load Questions" message="Something went wrong loading questions. Please try again." variant="card" />
            ) : questions && questions.length > 0 ? (
              <div>
                <div className="mb-5 flex items-center justify-between">
                  <p className="text-sm text-gray-500">
                    Showing <span className="font-semibold text-gray-700">{questions.length}</span>{' '}
                    question{questions.length !== 1 ? 's' : ''}
                  </p>
                </div>
                <div className="grid gap-4">
                  {questions.map((question: Question, i: number) => (
                    <QuestionListItem key={question.id} question={question} index={i} />
                  ))}
                </div>
              </div>
            ) : (
              <div className="card p-16 text-center animate-scale-in">
                <div className="w-20 h-20 bg-gray-50 rounded-2xl flex items-center justify-center mx-auto mb-5">
                  <MagnifyingGlassIcon className="h-10 w-10 text-gray-300" />
                </div>
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  {searchQuery ? 'No questions match your search' : 'No questions yet'}
                </h3>
                <p className="text-gray-500 text-sm mb-7 max-w-xs mx-auto">
                  {searchQuery ? 'Try adjusting your search terms or clearing filters.' : 'Be the first to ask a question to candidates in your area!'}
                </p>
                <div className="flex flex-col sm:flex-row gap-3 justify-center">
                  {searchQuery && (
                    <button onClick={() => setSearchQuery('')} className="btn-ghost border border-gray-200 px-5 py-2.5 text-sm">
                      Clear Search
                    </button>
                  )}
                  <Link to="/ballot" className="btn-primary px-5 py-2.5 text-sm">Find Your Ballot</Link>
                </div>
              </div>
            )}
          </div>

          <div className="bg-gradient-to-r from-primary-600 to-indigo-600 py-14 mt-10">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
              <h2 className="text-3xl font-bold text-white mb-3">Have a Question for Your Candidates?</h2>
              <p className="text-lg text-primary-100 mb-8 max-w-xl mx-auto">
                Submit your question and get direct video answers from candidates running in your area.
              </p>
              <Link to="/ballot" className="btn bg-white text-primary-700 shadow-lg hover:bg-primary-50 hover:shadow-xl active:scale-[0.98] px-8 py-3 text-base rounded-xl font-bold transition-all">
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
