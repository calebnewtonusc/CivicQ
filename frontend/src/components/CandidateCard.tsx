import React from 'react';
import { Link } from 'react-router-dom';
import { Candidate } from '../types';

interface CandidateCardProps {
  candidate: Candidate;
  showAnswerCount?: boolean;
}

const CandidateCard: React.FC<CandidateCardProps> = ({
  candidate,
  showAnswerCount = true,
}) => {
  const answerCount = candidate.video_answers?.length || 0;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start space-x-4">
        {/* Photo */}
        <div className="flex-shrink-0">
          {candidate.photo_url ? (
            <img
              src={candidate.photo_url}
              alt={candidate.name}
              className="h-20 w-20 rounded-full object-cover border-2 border-gray-200"
            />
          ) : (
            <div className="h-20 w-20 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-2xl font-bold">
              {candidate.name.charAt(0)}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1">
          <Link
            to={`/candidate/${candidate.id}`}
            className="text-xl font-semibold text-gray-900 hover:text-civic-blue"
          >
            {candidate.name}
          </Link>

          {/* Status Badge */}
          <div className="mt-1">
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                candidate.status === 'active'
                  ? 'bg-green-100 text-green-800'
                  : candidate.status === 'verified'
                  ? 'bg-blue-100 text-blue-800'
                  : 'bg-gray-100 text-gray-800'
              }`}
            >
              {candidate.status}
              {candidate.identity_verified && ' (Verified)'}
            </span>
          </div>

          {/* Website */}
          {candidate.website && (
            <a
              href={candidate.website}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-2 inline-flex items-center text-sm text-civic-blue hover:underline"
              onClick={(e) => e.stopPropagation()}
            >
              <svg
                className="w-4 h-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
              Campaign Website
            </a>
          )}

          {/* Answer Count */}
          {showAnswerCount && (
            <div className="mt-3 text-sm text-gray-600">
              <span className="font-medium">{answerCount}</span> video answer
              {answerCount !== 1 ? 's' : ''} submitted
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CandidateCard;
