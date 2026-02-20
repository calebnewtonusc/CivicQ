import React from 'react';
import { Link } from 'react-router-dom';
import { Candidate } from '../types';

interface CandidateCardProps {
  candidate: Candidate;
  showAnswerCount?: boolean;
}

const statusConfig = {
  active:   'bg-success-100 text-success-800 border border-success-200',
  verified: 'bg-primary-100 text-primary-800 border border-primary-200',
  default:  'bg-gray-100 text-gray-700 border border-gray-200',
};

const CandidateCard: React.FC<CandidateCardProps> = ({
  candidate,
  showAnswerCount = true,
}) => {
  const answerCount = candidate.video_answers?.length || 0;
  const statusClass = statusConfig[candidate.status as keyof typeof statusConfig] ?? statusConfig.default;

  return (
    <div className="group card hover:shadow-card-md hover:-translate-y-0.5 transition-all duration-200 p-6">
      <div className="flex items-start gap-4">
        {/* Photo */}
        <div className="flex-shrink-0">
          {candidate.photo_url ? (
            <img
              src={candidate.photo_url}
              alt={candidate.name}
              className="h-16 w-16 rounded-full object-cover border-2 border-gray-100 group-hover:border-primary-200 transition-colors"
            />
          ) : (
            <div className="h-16 w-16 rounded-full bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center text-gray-600 text-xl font-bold border-2 border-gray-100 group-hover:border-primary-200 transition-colors">
              {candidate.name.charAt(0)}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <Link
            to={`/candidate/${candidate.id}`}
            className="text-lg font-bold text-gray-900 hover:text-primary-700 transition-colors leading-snug block truncate
                       focus-visible:outline-none focus-visible:text-primary-700"
          >
            {candidate.name}
          </Link>

          {/* Status Badge */}
          <div className="mt-1.5 flex items-center gap-2 flex-wrap">
            <span className={`badge text-xs ${statusClass}`}>
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
              className="mt-2 inline-flex items-center gap-1 text-sm text-primary-600 hover:text-primary-700 font-medium transition-colors focus-visible:outline-none focus-visible:underline"
              onClick={(e) => e.stopPropagation()}
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              Campaign Website
            </a>
          )}

          {/* Answer Count */}
          {showAnswerCount && (
            <div className="mt-2.5 text-xs text-gray-500 flex items-center gap-1">
              <svg className="w-3.5 h-3.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              <span className="font-semibold text-gray-700">{answerCount}</span>{' '}
              video answer{answerCount !== 1 ? 's' : ''}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CandidateCard;
