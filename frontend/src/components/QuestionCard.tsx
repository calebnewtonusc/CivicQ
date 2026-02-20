import React from 'react';
import { Link } from 'react-router-dom';
import { Question } from '../types';
import VoteButton from './VoteButton';

interface QuestionCardProps {
  question: Question;
  showContest?: boolean;
}

const statusConfig = {
  approved: {
    label: 'Approved',
    className: 'badge-green',
    icon: (
      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
      </svg>
    ),
  },
  pending: {
    label: 'Pending',
    className: 'badge-yellow',
    icon: (
      <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
      </svg>
    ),
  },
} as const;

const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  showContest: _showContest = false,
}) => {
  const netVotes = question.upvotes - question.downvotes;
  const answerCount = question.video_answers?.length ?? 0;
  const status = statusConfig[question.status as keyof typeof statusConfig];

  return (
    <article className="group bg-white rounded-2xl border border-gray-100 shadow-card hover:shadow-card-md hover:-translate-y-0.5 transition-all duration-200 overflow-hidden">
      <div className="flex items-stretch">
        {/* Left vote column */}
        <div className="flex flex-col items-center justify-start gap-1 px-4 py-5 bg-gray-50 border-r border-gray-100">
          <VoteButton questionId={question.id} />
          <span
            className={`text-sm font-bold tabular-nums mt-1 ${
              netVotes > 0
                ? 'text-primary-600'
                : netVotes < 0
                ? 'text-red-500'
                : 'text-gray-400'
            }`}
            aria-label={`${netVotes} net votes`}
          >
            {netVotes}
          </span>
        </div>

        {/* Main content */}
        <div className="flex-1 p-5 min-w-0">
          {/* Question text — clickable link */}
          <Link
            to={`/question/${question.id}`}
            className="block text-base font-semibold text-gray-900 leading-snug
                       hover:text-primary-700 transition-colors duration-150
                       focus-visible:outline-none focus-visible:text-primary-700"
          >
            {question.question_text}
          </Link>

          {/* Context */}
          {question.context && (
            <p className="mt-1.5 text-sm text-gray-500 italic line-clamp-2">
              {question.context}
            </p>
          )}

          {/* Tags */}
          {question.issue_tags && question.issue_tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-1.5">
              {question.issue_tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium
                             bg-primary-50 text-primary-700 border border-primary-100
                             hover:bg-primary-100 transition-colors"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}

          {/* Footer row */}
          <div className="mt-4 flex items-center gap-4 text-xs text-gray-500">
            {/* Answers count */}
            {answerCount > 0 && (
              <span className="flex items-center gap-1 font-medium text-success-700">
                <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 6a2 2 0 012-2h6a2 2 0 012 2v8a2 2 0 01-2 2H4a2 2 0 01-2-2V6zm12.553 1.106A1 1 0 0014 8v4a1 1 0 00.553.894l2 1A1 1 0 0018 13V7a1 1 0 00-1.447-.894l-2 1z" />
                </svg>
                {answerCount} {answerCount === 1 ? 'answer' : 'answers'}
              </span>
            )}

            {/* Status badge */}
            {status && (
              <span className={status.className + ' flex items-center gap-1'}>
                {status.icon}
                {status.label}
              </span>
            )}

            {/* View link */}
            <Link
              to={`/question/${question.id}`}
              className="ml-auto flex items-center gap-1 font-medium text-gray-400
                         hover:text-primary-600 transition-colors group-hover:text-primary-500"
              aria-label="View question details"
            >
              View
              <svg
                className="w-3.5 h-3.5 transition-transform group-hover:translate-x-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </Link>
          </div>
        </div>
      </div>
    </article>
  );
};

export default QuestionCard;
