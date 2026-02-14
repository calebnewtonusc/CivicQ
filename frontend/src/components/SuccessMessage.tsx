import React from 'react';

interface SuccessMessageProps {
  message: string;
  onDismiss?: () => void;
}

const SuccessMessage: React.FC<SuccessMessageProps> = ({ message, onDismiss }) => {
  return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-6">
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg
            className="h-6 w-6 text-green-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-medium text-green-800">Success</h3>
          <p className="mt-1 text-sm text-green-700">{message}</p>
          {onDismiss && (
            <button
              onClick={onDismiss}
              className="mt-3 text-sm font-medium text-green-800 hover:text-green-900 underline"
            >
              Dismiss
            </button>
          )}
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 ml-4 text-green-400 hover:text-green-600"
          >
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
};

export default SuccessMessage;
