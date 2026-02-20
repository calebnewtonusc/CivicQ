import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

const NotFoundPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-indigo-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center animate-fade-in">
        {/* Illustration */}
        <div className="mb-10">
          <div className="relative inline-flex items-center justify-center w-56 h-56 mx-auto">
            <span className="absolute text-[8rem] font-black text-primary-100 select-none leading-none">
              404
            </span>
            <div className="relative z-10 w-28 h-28 bg-gradient-to-br from-primary-500 to-indigo-600 rounded-3xl flex items-center justify-center shadow-card-xl rotate-6">
              <svg className="w-14 h-14 text-white -rotate-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
        </div>

        {/* Content */}
        <h1 className="text-4xl font-extrabold text-gray-900 mb-3">Page Not Found</h1>
        <p className="text-lg text-gray-500 mb-2">
          Oops — this page has gone missing from the ballot.
        </p>
        <p className="text-sm text-gray-400 mb-10">
          The page you're looking for doesn't exist or may have been moved.
        </p>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center mb-12">
          <button
            onClick={() => navigate(-1)}
            className="btn-ghost border border-gray-200 px-6 py-3 text-sm font-semibold"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Go Back
          </button>
          <Link to="/" className="btn-primary px-6 py-3 text-sm font-bold">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Back to Home
          </Link>
        </div>

        {/* Quick Links */}
        <div className="card p-6 text-left">
          <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">
            Looking for something?
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {[
              { to: '/ballot', icon: '🗳️', label: 'View Ballot', sub: 'See your local elections' },
              { to: '/about', icon: '💡', label: 'About CivicQ', sub: 'Learn how it works' },
              { to: '/contact', icon: '✉️', label: 'Contact Us', sub: 'Get in touch' },
              { to: '/login', icon: '🔑', label: 'Sign In', sub: 'Access your account' },
            ].map(({ to, label, sub }) => (
              <Link
                key={to}
                to={to}
                className="group flex items-center gap-3 p-3 rounded-xl hover:bg-primary-50 transition-all duration-150
                           focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
              >
                <div className="w-10 h-10 bg-primary-50 rounded-xl flex items-center justify-center
                                group-hover:bg-primary-100 transition-colors flex-shrink-0">
                  <svg className="w-5 h-5 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900 group-hover:text-primary-700 transition-colors">
                    {label}
                  </p>
                  <p className="text-xs text-gray-400">{sub}</p>
                </div>
              </Link>
            ))}
          </div>
        </div>

        <p className="mt-8 text-xs text-gray-400">
          If you think this is an error, please{' '}
          <Link to="/contact" className="text-primary-600 hover:text-primary-700 font-medium underline-offset-2 underline transition-colors">
            contact us
          </Link>
          .
        </p>
      </div>
    </div>
  );
};

export default NotFoundPage;
