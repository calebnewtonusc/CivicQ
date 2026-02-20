import React from 'react';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  className?: string;
  title?: string;
  variant?: 'inline' | 'card' | 'banner';
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  onRetry,
  className = '',
  title = 'Something went wrong',
  variant = 'inline',
}) => {
  if (variant === 'banner') {
    return (
      <div
        role="alert"
        className={`flex items-center gap-3 px-4 py-3 bg-danger-50 border border-danger-200 rounded-xl text-danger-700 text-sm ${className}`}
      >
        <svg
          className="w-5 h-5 flex-shrink-0 text-danger-500"
          fill="currentColor"
          viewBox="0 0 20 20"
          aria-hidden="true"
        >
          <path
            fillRule="evenodd"
            d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
            clipRule="evenodd"
          />
        </svg>
        <p className="flex-1 font-medium">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="ml-auto flex-shrink-0 text-xs font-semibold text-danger-700 hover:text-danger-900 underline underline-offset-2 transition-colors focus-visible:outline-none"
          >
            Dismiss
          </button>
        )}
      </div>
    );
  }

  if (variant === 'card') {
    return (
      <div
        role="alert"
        className={`bg-danger-50 border-2 border-danger-200 rounded-2xl p-8 text-center animate-scale-in ${className}`}
      >
        <div className="w-16 h-16 bg-danger-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg
            className="w-8 h-8 text-danger-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>
        <h3 className="text-xl font-bold text-gray-900 mb-2">{title}</h3>
        <p className="text-danger-700 text-sm mb-6 max-w-sm mx-auto">{message}</p>
        {onRetry && (
          <button
            onClick={onRetry}
            className="btn-primary"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Try Again
          </button>
        )}
      </div>
    );
  }

  // Default: inline
  return (
    <div
      role="alert"
      className={`bg-danger-50 border border-danger-200 rounded-xl p-4 animate-fade-in ${className}`}
    >
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <svg
            className="w-5 h-5 text-danger-500"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-danger-800">{title}</h3>
          <p className="mt-0.5 text-sm text-danger-700">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="mt-2 text-xs font-semibold text-danger-800 hover:text-danger-900 underline underline-offset-2 transition-colors focus-visible:outline-none"
            >
              Try again
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export { ErrorMessage };
export default ErrorMessage;
