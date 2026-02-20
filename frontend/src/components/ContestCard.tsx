import React from 'react';
import { Link } from 'react-router-dom';
import { Contest } from '../types';

interface ContestCardProps {
  contest: Contest;
  ballotId?: number;
}

const ContestCard: React.FC<ContestCardProps> = ({ contest, ballotId: _ballotId }) => {
  const candidateCount = contest.candidates?.length ?? 0;
  const questionCount  = contest.questions?.length ?? 0;
  const isRace = contest.type === 'race';

  return (
    <Link
      to={`/contest/${contest.id}`}
      className="group block bg-white rounded-2xl border border-gray-100 shadow-card
                 hover:shadow-card-md hover:-translate-y-0.5 hover:border-primary-200
                 transition-all duration-200 overflow-hidden
                 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
    >
      <div className="flex items-stretch">
        {/* Color accent bar */}
        <div
          className={`w-1 flex-shrink-0 rounded-l-2xl ${
            isRace ? 'bg-gradient-to-b from-primary-500 to-indigo-500' : 'bg-gradient-to-b from-purple-500 to-pink-500'
          }`}
        />

        <div className="flex-1 p-6">
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1 min-w-0">
              {/* Type badge */}
              <span
                className={`badge mb-2 ${
                  isRace ? 'badge-blue' : 'bg-purple-100 text-purple-800 border border-purple-200 badge'
                }`}
              >
                {isRace ? (
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                  </svg>
                ) : (
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z" />
                    <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd" />
                  </svg>
                )}
                {isRace ? 'Race' : 'Measure'}
              </span>

              {/* Title */}
              <h3 className="text-lg font-bold text-gray-900 leading-snug group-hover:text-primary-700 transition-colors">
                {contest.title}
              </h3>

              {/* Office / Jurisdiction */}
              {(contest.office || contest.jurisdiction) && (
                <div className="mt-1.5 flex flex-wrap gap-x-4 gap-y-0.5">
                  {contest.office && (
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Office:</span> {contest.office}
                    </p>
                  )}
                  {contest.jurisdiction && (
                    <p className="text-sm text-gray-600">
                      <span className="font-medium">Jurisdiction:</span> {contest.jurisdiction}
                    </p>
                  )}
                </div>
              )}

              {/* Description */}
              {contest.description && (
                <p className="mt-2 text-sm text-gray-500 line-clamp-2 leading-relaxed">
                  {contest.description}
                </p>
              )}

              {/* Stats row */}
              <div className="mt-4 flex flex-wrap items-center gap-4 text-sm text-gray-500">
                {isRace && (
                  <span className="flex items-center gap-1.5">
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span className="font-medium text-gray-700">{candidateCount}</span>
                    {' '}candidate{candidateCount !== 1 ? 's' : ''}
                  </span>
                )}

                <span className="flex items-center gap-1.5">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="font-medium text-gray-700">{questionCount}</span>
                  {' '}question{questionCount !== 1 ? 's' : ''}
                </span>

                {contest.seat_count && contest.seat_count > 1 && (
                  <span className="badge-gray">
                    {contest.seat_count} seats
                  </span>
                )}
              </div>

              {/* AI badge */}
              <div className="mt-3 inline-flex items-center gap-1.5 px-2.5 py-1 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-full text-xs text-blue-700 font-medium">
                <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
                </svg>
                AI-Powered Question Help
              </div>
            </div>

            {/* Arrow */}
            <div className="flex-shrink-0 self-center">
              <div className="w-8 h-8 rounded-full bg-gray-50 border border-gray-200 flex items-center justify-center
                              group-hover:bg-primary-50 group-hover:border-primary-200 transition-all duration-200">
                <svg
                  className="w-4 h-4 text-gray-400 group-hover:text-primary-600 transition-all duration-200 group-hover:translate-x-0.5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Link>
  );
};

export default ContestCard;
