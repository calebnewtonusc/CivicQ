import React from 'react';
import { Link } from 'react-router-dom';
import { Question } from '../types';
import VoteButton from './VoteButton';

interface QuestionCardProps {
  question: Question;
  showContest?: boolean;
}

const QuestionCard: React.FC<QuestionCardProps> = ({ question, showContest: _showContest = false }) => {
  const netVotes = question.upvotes - question.downvotes;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start space-x-4">
        {/* Vote Section */}
        <VoteButton questionId={question.id} />

        {/* Question Content */}
        <div className="flex-1">
          <Link
            to={`/question/${question.id}`}
            className="text-lg font-semibold text-gray-900 hover:text-civic-blue"
          >
            {question.question_text}
          </Link>

          {/* Context */}
          {question.context && (
            <p className="mt-2 text-sm text-gray-600 italic">{question.context}</p>
          )}

          {/* Tags */}
          {question.issue_tags && question.issue_tags.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {question.issue_tags.map((tag) => (
                <span
                  key={tag}
                  className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          {/* Metadata */}
          <div className="mt-4 flex items-center space-x-4 text-sm text-gray-500">
            <span>{netVotes} votes</span>
            {question.video_answers && question.video_answers.length > 0 && (
              <span>{question.video_answers.length} answers</span>
            )}
            <span
              className={`px-2 py-1 rounded text-xs font-medium ${
                question.status === 'approved'
                  ? 'bg-green-100 text-green-800'
                  : 'bg-yellow-100 text-yellow-800'
              }`}
            >
              {question.status}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QuestionCard;
