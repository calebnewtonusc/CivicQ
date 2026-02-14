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
  XCircleIcon,
  MinusCircleIcon,
  DocumentTextIcon,
  CalendarIcon,
  ScaleIcon
} from '@heroicons/react/24/outline';

type VoteRecord = {
  id: number;
  bill_title: string;
  bill_number: string;
  description: string;
  date: string;
  vote: 'yes' | 'no' | 'abstain' | 'absent';
  category: string;
  result: 'passed' | 'failed';
  source_url: string;
};

export default function CandidateRecordPage() {
  const { candidateId } = useParams<{ candidateId: string }>();
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterVote, setFilterVote] = useState<string>('all');

  const { data: candidate, isLoading: candidateLoading } = useQuery({
    queryKey: ['candidate', candidateId],
    queryFn: async () => {
      const response = await api.get(`/candidates/${candidateId}`);
      return response.data;
    }
  });

  const { data: votingRecord, isLoading: recordLoading } = useQuery({
    queryKey: ['candidate-voting-record', candidateId],
    queryFn: async () => {
      const response = await api.get(`/candidates/${candidateId}/voting-record`);
      return response.data;
    }
  });

  const isLoading = candidateLoading || recordLoading;

  const getVoteIcon = (vote: string) => {
    switch (vote) {
      case 'yes':
        return <CheckCircleIcon className="h-6 w-6 text-green-600" />;
      case 'no':
        return <XCircleIcon className="h-6 w-6 text-red-600" />;
      case 'abstain':
        return <MinusCircleIcon className="h-6 w-6 text-yellow-600" />;
      case 'absent':
        return <MinusCircleIcon className="h-6 w-6 text-gray-400" />;
      default:
        return null;
    }
  };

  const getVoteBadge = (vote: string) => {
    switch (vote) {
      case 'yes':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-800 text-sm font-medium rounded-full">
            <CheckCircleIcon className="h-4 w-4" />
            Yes
          </span>
        );
      case 'no':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-red-100 text-red-800 text-sm font-medium rounded-full">
            <XCircleIcon className="h-4 w-4" />
            No
          </span>
        );
      case 'abstain':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-yellow-100 text-yellow-800 text-sm font-medium rounded-full">
            <MinusCircleIcon className="h-4 w-4" />
            Abstain
          </span>
        );
      case 'absent':
        return (
          <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-600 text-sm font-medium rounded-full">
            <MinusCircleIcon className="h-4 w-4" />
            Absent
          </span>
        );
      default:
        return null;
    }
  };

  const filteredRecords = votingRecord ? votingRecord.filter((record: VoteRecord) => {
    if (filterCategory !== 'all' && record.category !== filterCategory) return false;
    if (filterVote !== 'all' && record.vote !== filterVote) return false;
    return true;
  }) : [];

  const categories = votingRecord ? [...new Set(votingRecord.map((r: VoteRecord) => r.category))] : [];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  // Check if candidate has no voting record (not an incumbent)
  const hasNoRecord = !votingRecord || votingRecord.length === 0;

  return (
    <>
      <Helmet>
        <title>Voting Record - {candidate?.full_name} - CivicQ</title>
        <meta
          name="description"
          content={`View the complete voting record of ${candidate?.full_name}`}
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
                <span className="text-gray-900">Voting Record</span>
              </nav>

              <div className="flex items-start justify-between mb-6">
                <div>
                  <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2 flex items-center gap-3">
                    <ScaleIcon className="h-10 w-10 text-blue-600" />
                    Voting Record
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

              {!hasNoRecord && (
                <>
                  {/* Stats */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                    <div className="bg-white rounded-lg border border-gray-200 p-4">
                      <div className="text-2xl font-bold text-blue-600">{votingRecord.length}</div>
                      <div className="text-sm text-gray-600">Total Votes</div>
                    </div>
                    <div className="bg-white rounded-lg border border-gray-200 p-4">
                      <div className="text-2xl font-bold text-green-600">
                        {votingRecord.filter((r: VoteRecord) => r.vote === 'yes').length}
                      </div>
                      <div className="text-sm text-gray-600">Yes Votes</div>
                    </div>
                    <div className="bg-white rounded-lg border border-gray-200 p-4">
                      <div className="text-2xl font-bold text-red-600">
                        {votingRecord.filter((r: VoteRecord) => r.vote === 'no').length}
                      </div>
                      <div className="text-sm text-gray-600">No Votes</div>
                    </div>
                    <div className="bg-white rounded-lg border border-gray-200 p-4">
                      <div className="text-2xl font-bold text-gray-600">
                        {votingRecord.filter((r: VoteRecord) => r.vote === 'abstain' || r.vote === 'absent').length}
                      </div>
                      <div className="text-sm text-gray-600">Abstain/Absent</div>
                    </div>
                  </div>

                  {/* Filters */}
                  <div className="bg-white rounded-lg border border-gray-200 p-4 flex flex-wrap gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Category
                      </label>
                      <select
                        value={filterCategory}
                        onChange={(e) => setFilterCategory(e.target.value)}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                      >
                        <option value="all">All Categories</option>
                        {categories.map((category) => (
                          <option key={category} value={category}>
                            {category}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Vote
                      </label>
                      <select
                        value={filterVote}
                        onChange={(e) => setFilterVote(e.target.value)}
                        className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
                      >
                        <option value="all">All Votes</option>
                        <option value="yes">Yes</option>
                        <option value="no">No</option>
                        <option value="abstain">Abstain</option>
                        <option value="absent">Absent</option>
                      </select>
                    </div>

                    {(filterCategory !== 'all' || filterVote !== 'all') && (
                      <div className="flex items-end">
                        <button
                          onClick={() => {
                            setFilterCategory('all');
                            setFilterVote('all');
                          }}
                          className="px-4 py-2 text-blue-600 hover:text-blue-700 font-medium"
                        >
                          Clear Filters
                        </button>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>

            {/* Voting Record or Empty State */}
            {hasNoRecord ? (
              <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
                <DocumentTextIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  No Voting Record Available
                </h3>
                <p className="text-gray-600 mb-6 max-w-xl mx-auto">
                  {candidate?.full_name} {candidate?.is_incumbent
                    ? 'does not have a publicly available voting record yet.'
                    : 'is not currently an elected official and therefore has no voting record on file. Check their campaign platform and answers to voter questions to understand their positions.'}
                </p>
                <Link
                  to={`/candidate/${candidateId}/questions`}
                  className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                >
                  View Questions & Answers
                </Link>
              </div>
            ) : filteredRecords.length > 0 ? (
              <div className="space-y-4">
                {filteredRecords.map((record: VoteRecord) => (
                  <div
                    key={record.id}
                    className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-grow pr-4">
                        <div className="flex items-start gap-3 mb-2">
                          {getVoteIcon(record.vote)}
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-1">
                              {record.bill_title}
                            </h3>
                            <p className="text-sm text-gray-600 font-mono">{record.bill_number}</p>
                          </div>
                        </div>
                      </div>
                      {getVoteBadge(record.vote)}
                    </div>

                    <p className="text-gray-700 mb-4">{record.description}</p>

                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-4">
                      <span className="flex items-center gap-1">
                        <CalendarIcon className="h-4 w-4" />
                        {new Date(record.date).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric'
                        })}
                      </span>
                      <span>•</span>
                      <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs font-medium">
                        {record.category}
                      </span>
                      <span>•</span>
                      <span>
                        Bill {record.result === 'passed' ? (
                          <span className="text-green-600 font-medium">Passed</span>
                        ) : (
                          <span className="text-red-600 font-medium">Failed</span>
                        )}
                      </span>
                    </div>

                    {record.source_url && (
                      <a
                        href={record.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 text-sm font-medium"
                      >
                        View Official Record →
                      </a>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-white border border-gray-200 rounded-lg p-12 text-center">
                <DocumentTextIcon className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  No votes match your filters
                </h3>
                <p className="text-gray-600 mb-6">
                  Try adjusting your filter settings
                </p>
                <button
                  onClick={() => {
                    setFilterCategory('all');
                    setFilterVote('all');
                  }}
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  Clear All Filters
                </button>
              </div>
            )}
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
}
