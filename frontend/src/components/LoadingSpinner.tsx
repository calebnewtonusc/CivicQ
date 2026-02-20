import React from 'react';

interface LoadingSpinnerProps {
  size?: 'xs' | 'sm' | 'md' | 'lg';
  message?: string;
  className?: string;
  /** When true renders inline with no padding — useful inside buttons */
  inline?: boolean;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  message,
  className = '',
  inline = false,
}) => {
  const sizeMap = {
    xs: 'h-4 w-4 border-[1.5px]',
    sm: 'h-5 w-5 border-2',
    md: 'h-10 w-10 border-[3px]',
    lg: 'h-16 w-16 border-4',
  };

  const spinner = (
    <div
      className={`animate-spin rounded-full border-primary-200 border-t-primary-600 ${sizeMap[size]}`}
      role="status"
      aria-label={message || 'Loading…'}
    />
  );

  if (inline) return spinner;

  return (
    <div className={`flex flex-col items-center justify-center gap-3 py-10 ${className}`}>
      {spinner}
      {message && (
        <p className="text-sm font-medium text-gray-500 animate-pulse">{message}</p>
      )}
    </div>
  );
};

export default LoadingSpinner;
