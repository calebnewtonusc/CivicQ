import React, { useCallback } from 'react';
import { useVote } from '../hooks/useVoting';
import { useAuthContext } from '../contexts/AuthContext';
import { Link } from 'react-router-dom';

interface VoteButtonProps {
  questionId: number;
  /** Orientation: column (default Reddit-style) or row */
  orientation?: 'col' | 'row';
}

const VoteButton: React.FC<VoteButtonProps> = ({
  questionId,
  orientation = 'col',
}) => {
  const { isAuthenticated } = useAuthContext();
  const { currentVote, upvote, downvote, isVoting } = useVote(questionId);

  const hasUpvoted   = currentVote?.value === 1;
  const hasDownvoted = currentVote?.value === -1;

  const handleUpvote = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
      if (!isAuthenticated) return;
      upvote(questionId);
    },
    [isAuthenticated, questionId, upvote],
  );

  const handleDownvote = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
      if (!isAuthenticated) return;
      downvote(questionId);
    },
    [isAuthenticated, questionId, downvote],
  );

  const flexDir = orientation === 'row' ? 'flex-row' : 'flex-col';

  /* Unauthenticated users see dimmed buttons that link to /login */
  if (!isAuthenticated) {
    return (
      <div className={`flex ${flexDir} items-center gap-1.5`}>
        <Link
          to="/login"
          onClick={(e) => e.stopPropagation()}
          className="group p-2 rounded-lg text-gray-300 hover:text-primary-500 hover:bg-primary-50
                     transition-all duration-150 focus-visible:ring-2 focus-visible:ring-primary-500"
          title="Log in to upvote"
          aria-label="Log in to upvote"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
          </svg>
        </Link>
        <Link
          to="/login"
          onClick={(e) => e.stopPropagation()}
          className="group p-2 rounded-lg text-gray-300 hover:text-red-400 hover:bg-red-50
                     transition-all duration-150 focus-visible:ring-2 focus-visible:ring-red-400"
          title="Log in to downvote"
          aria-label="Log in to downvote"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </Link>
      </div>
    );
  }

  return (
    <div className={`flex ${flexDir} items-center gap-1.5`}>
      {/* Upvote */}
      <button
        onClick={handleUpvote}
        disabled={isVoting}
        aria-pressed={hasUpvoted}
        aria-label={hasUpvoted ? 'Remove upvote' : 'Upvote this question'}
        className={`
          group relative p-2 rounded-lg transition-all duration-150
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500
          disabled:cursor-not-allowed disabled:opacity-40
          ${hasUpvoted
            ? 'text-primary-600 bg-primary-50 shadow-glow-blue'
            : 'text-gray-400 hover:text-primary-500 hover:bg-primary-50'
          }
        `}
      >
        <svg
          className={`w-5 h-5 transition-transform duration-200 ${hasUpvoted ? 'scale-110' : 'group-hover:scale-110'}`}
          fill={hasUpvoted ? 'currentColor' : 'none'}
          stroke="currentColor"
          strokeWidth={2}
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" />
        </svg>

        {/* Ripple on active */}
        {hasUpvoted && (
          <span
            className="absolute inset-0 rounded-lg bg-primary-400 opacity-0 animate-ping"
            style={{ animationDuration: '0.6s', animationIterationCount: 1 }}
            aria-hidden="true"
          />
        )}
      </button>

      {/* Downvote */}
      <button
        onClick={handleDownvote}
        disabled={isVoting}
        aria-pressed={hasDownvoted}
        aria-label={hasDownvoted ? 'Remove downvote' : 'Downvote this question'}
        className={`
          group relative p-2 rounded-lg transition-all duration-150
          focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-400
          disabled:cursor-not-allowed disabled:opacity-40
          ${hasDownvoted
            ? 'text-red-500 bg-red-50 shadow-[0_0_0_3px_rgba(239,68,68,0.15)]'
            : 'text-gray-400 hover:text-red-400 hover:bg-red-50'
          }
        `}
      >
        <svg
          className={`w-5 h-5 transition-transform duration-200 ${hasDownvoted ? 'scale-110' : 'group-hover:scale-110'}`}
          fill={hasDownvoted ? 'currentColor' : 'none'}
          stroke="currentColor"
          strokeWidth={2}
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      </button>
    </div>
  );
};

export default VoteButton;
