import React, { useState, useEffect } from 'react';
import { getDemoMode } from '../services/demoMode';

const DemoModeBanner: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [isDismissed, setIsDismissed] = useState(false);

  useEffect(() => {
    // Check if in demo mode
    const checkDemoMode = () => {
      const inDemoMode = getDemoMode();
      setIsVisible(inDemoMode && !isDismissed);
    };

    // Check immediately
    checkDemoMode();

    // Set up interval to check periodically
    const interval = setInterval(checkDemoMode, 1000);

    return () => clearInterval(interval);
  }, [isDismissed]);

  const handleDismiss = () => {
    setIsDismissed(true);
    setIsVisible(false);
  };

  if (!isVisible) return null;

  return (
    <div className="bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg">
      <div className="container mx-auto px-4 py-3">
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 flex-1">
            <div className="flex-shrink-0">
              <div className="w-10 h-10 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
            </div>

            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <h3 className="text-lg font-bold">Demo Mode Active</h3>
                <span className="px-2 py-0.5 bg-white/30 backdrop-blur-sm rounded-full text-xs font-semibold uppercase tracking-wide">
                  Preview Only
                </span>
              </div>
              <p className="text-sm text-white/90">
                You're viewing demo data. The backend is not connected. Features like voting,
                asking questions, and authentication are simulated for demonstration purposes.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDismiss}
              className="flex-shrink-0 px-4 py-2 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-lg transition-all text-sm font-semibold"
              aria-label="Dismiss banner"
            >
              Got it
            </button>
            <button
              onClick={handleDismiss}
              className="flex-shrink-0 w-8 h-8 bg-white/20 hover:bg-white/30 backdrop-blur-sm rounded-lg transition-all flex items-center justify-center"
              aria-label="Close banner"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DemoModeBanner;
