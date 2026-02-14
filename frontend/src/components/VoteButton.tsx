import React from 'react';
import { useVote } from '../hooks/useVoting';
import { useAuthContext } from '../contexts/AuthContext';

interface VoteButtonProps {
  questionId: number;
}

const VoteButton: React.FC<VoteButtonProps> = ({ questionId }) => {
  const { isAuthenticated } = useAuthContext();
  const { currentVote, upvote, downvote, isVoting } = useVote(questionId);

  const hasUpvoted = currentVote?.value === 1;
  const hasDownvoted = currentVote?.value === -1;

  const handleUpvote = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isAuthenticated) {
      alert('Please log in to vote');
      return;
    }
    upvote(questionId);
  };

  const handleDownvote = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!isAuthenticated) {
      alert('Please log in to vote');
      return;
    }
    downvote(questionId);
  };

  return (
    <div className="flex flex-col items-center space-y-1">
      <button
        onClick={handleUpvote}
        disabled={isVoting}
        className={`p-1.5 rounded hover:bg-gray-100 transition-colors ${
          hasUpvoted ? 'text-civic-green' : 'text-gray-400'
        } ${isVoting ? 'opacity-50 cursor-not-allowed' : ''}`}
        title="Upvote"
      >
        <svg
          className="w-6 h-6"
          fill={hasUpvoted ? 'currentColor' : 'none'}
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 15l7-7 7 7"
          />
        </svg>
      </button>

      <button
        onClick={handleDownvote}
        disabled={isVoting}
        className={`p-1.5 rounded hover:bg-gray-100 transition-colors ${
          hasDownvoted ? 'text-red-500' : 'text-gray-400'
        } ${isVoting ? 'opacity-50 cursor-not-allowed' : ''}`}
        title="Downvote"
      >
        <svg
          className="w-6 h-6"
          fill={hasDownvoted ? 'currentColor' : 'none'}
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 9l-7 7-7-7"
          />
        </svg>
      </button>
    </div>
  );
};

export default VoteButton;
