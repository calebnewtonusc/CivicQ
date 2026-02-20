import React from 'react';

interface SuccessMessageProps {
  message: string;
  title?: string;
  onDismiss?: () => void;
  className?: string;
}

const SuccessMessage: React.FC<SuccessMessageProps> = ({
  message,
  title = 'Success',
  onDismiss,
  className = '',
}) => {
  return (
    <div
      role="status"
      className={`bg-success-50 border border-success-200 rounded-xl p-4 animate-fade-in ${className}`}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <svg
            className="w-5 h-5 text-success-500"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-success-800">{title}</h3>
          <p className="mt-0.5 text-sm text-success-700">{message}</p>
        </div>
        {onDismiss && (
          <button
            onClick={onDismiss}
            aria-label="Dismiss"
            className="flex-shrink-0 text-success-400 hover:text-success-600 transition-colors focus-visible:outline-none"
          >
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
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

export { SuccessMessage };
export default SuccessMessage;
