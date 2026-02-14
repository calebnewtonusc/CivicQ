import React from 'react';
import { Link } from 'react-router-dom';
import { Contest } from '../types';

interface ContestCardProps {
  contest: Contest;
  ballotId?: number;
}

const ContestCard: React.FC<ContestCardProps> = ({ contest, ballotId: _ballotId }) => {
  const candidateCount = contest.candidates?.length || 0;
  const questionCount = contest.questions?.length || 0;

  return (
    <Link
      to={`/contest/${contest.id}`}
      className="block bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md hover:border-civic-blue transition-all"
    >
      <div className="flex items-start justify-between">
        <div className="flex-1">
          {/* Contest Type Badge */}
          <div className="mb-2">
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                contest.type === 'race'
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-purple-100 text-purple-800'
              }`}
            >
              {contest.type === 'race' ? 'Race' : 'Measure'}
            </span>
          </div>

          {/* Title */}
          <h3 className="text-xl font-semibold text-gray-900">{contest.title}</h3>

          {/* Office/Jurisdiction */}
          {contest.office && (
            <p className="mt-1 text-sm text-gray-600">
              <span className="font-medium">Office:</span> {contest.office}
            </p>
          )}
          {contest.jurisdiction && (
            <p className="mt-1 text-sm text-gray-600">
              <span className="font-medium">Jurisdiction:</span> {contest.jurisdiction}
            </p>
          )}

          {/* Description */}
          {contest.description && (
            <p className="mt-2 text-sm text-gray-700 line-clamp-2">{contest.description}</p>
          )}

          {/* Stats */}
          <div className="mt-4 flex items-center space-x-6 text-sm text-gray-600">
            {contest.type === 'race' && (
              <div className="flex items-center">
                <svg
                  className="w-5 h-5 mr-1 text-gray-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
                  />
                </svg>
                <span>
                  {candidateCount} candidate{candidateCount !== 1 ? 's' : ''}
                </span>
              </div>
            )}
            <div className="flex items-center">
              <svg
                className="w-5 h-5 mr-1 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span>
                {questionCount} question{questionCount !== 1 ? 's' : ''}
              </span>
            </div>
            {contest.seat_count && contest.seat_count > 1 && (
              <div className="flex items-center">
                <span className="font-medium">{contest.seat_count} seats</span>
              </div>
            )}
          </div>
        </div>

        {/* Arrow */}
        <div className="ml-4 flex-shrink-0">
          <svg
            className="w-6 h-6 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 5l7 7-7 7"
            />
          </svg>
        </div>
      </div>
    </Link>
  );
};

export default ContestCard;
