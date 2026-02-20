import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthContext } from '../contexts/AuthContext';

/* ── DropdownLink ── */
const DropdownLink: React.FC<{
  to: string;
  onClick: () => void;
  icon: React.ReactNode;
  children: React.ReactNode;
}> = ({ to, onClick, icon, children }) => (
  <Link
    to={to}
    onClick={onClick}
    role="menuitem"
    className="flex items-center gap-2.5 px-3 py-2 text-sm font-medium text-gray-700 rounded-xl
               hover:bg-gray-100 hover:text-gray-900 transition-all duration-150
               focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
  >
    <span className="flex-shrink-0 text-gray-400">{icon}</span>
    {children}
  </Link>
);

/* ── UserProfileDropdown ── */
interface UserProfileDropdownProps {
  user: { full_name?: string; email?: string; city_name?: string; role?: string } | null;
  initials: string;
  onLogout: () => void;
}

const UserProfileDropdown: React.FC<UserProfileDropdownProps> = ({ user, initials, onLogout }) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen((v) => !v)}
        aria-expanded={isOpen}
        aria-haspopup="true"
        className="flex items-center gap-2.5 pl-2 pr-3 py-1.5 rounded-xl border border-gray-200
                   hover:border-gray-300 hover:bg-gray-50 transition-all duration-150
                   focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
      >
        <div className="w-7 h-7 bg-gradient-to-br from-primary-500 to-indigo-600 rounded-full
                        flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
          {initials}
        </div>
        <span className="text-sm font-medium text-gray-700 max-w-[120px] truncate">
          {user?.full_name || user?.email}
        </span>
        <svg
          className={`w-3.5 h-3.5 text-gray-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div
          className="absolute right-0 mt-2 w-60 bg-white rounded-2xl shadow-card-xl border border-gray-100
                     py-1.5 z-20 animate-slide-down"
          role="menu"
        >
          <div className="px-4 py-3 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-indigo-600 rounded-full
                              flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
                {initials}
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {user?.full_name || 'User'}
                </p>
                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                {user?.city_name && (
                  <p className="text-xs text-gray-400 mt-0.5">{user.city_name}</p>
                )}
              </div>
            </div>
          </div>

          <div className="py-1.5 px-1.5">
            {user?.role === 'candidate' && (
              <DropdownLink
                to="/candidate/dashboard"
                onClick={() => setIsOpen(false)}
                icon={
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                }
              >
                Candidate Dashboard
              </DropdownLink>
            )}

            <DropdownLink
              to="/profile"
              onClick={() => setIsOpen(false)}
              icon={
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              }
            >
              Profile Settings
            </DropdownLink>

            <DropdownLink
              to="/my-questions"
              onClick={() => setIsOpen(false)}
              icon={
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              }
            >
              My Questions
            </DropdownLink>
          </div>

          <div className="border-t border-gray-100 py-1.5 px-1.5">
            <button
              onClick={onLogout}
              role="menuitem"
              className="w-full flex items-center gap-2.5 px-3 py-2 text-sm font-medium text-red-600
                         rounded-xl hover:bg-red-50 transition-all duration-150
                         focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-400"
            >
              <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

/* ── MobileMenu ── */
interface MobileMenuProps {
  isAuthenticated: boolean;
  user: { full_name?: string; email?: string; role?: string } | null;
  initials: string;
  mobileNavLinkClass: (path: string) => string;
  onLogout: () => void;
}

const MobileMenu: React.FC<MobileMenuProps> = ({
  isAuthenticated,
  user,
  initials,
  mobileNavLinkClass,
  onLogout,
}) => (
  <div className="md:hidden border-t border-gray-100 bg-white animate-slide-down">
    <div className="px-3 pt-3 pb-2 space-y-1">
      <Link to="/" className={mobileNavLinkClass('/')}>Home</Link>
      <Link to="/ballot" className={mobileNavLinkClass('/ballot')}>My Ballot</Link>
      {isAuthenticated && (
        <>
          <Link to="/questions" className={mobileNavLinkClass('/questions')}>Questions</Link>
          {user?.role === 'candidate' && (
            <Link to="/candidate/dashboard" className={mobileNavLinkClass('/candidate/dashboard')}>Dashboard</Link>
          )}
        </>
      )}
    </div>

    <div className="border-t border-gray-100 pt-3 pb-4">
      {isAuthenticated ? (
        <>
          <div className="px-4 pb-3 flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-indigo-600 rounded-full
                            flex items-center justify-center text-white text-sm font-bold flex-shrink-0">
              {initials}
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-gray-900 truncate">{user?.full_name || 'User'}</p>
              <p className="text-xs text-gray-500 truncate">{user?.email}</p>
            </div>
          </div>
          <div className="px-3 space-y-1">
            <Link to="/profile" className={mobileNavLinkClass('/profile')}>Profile Settings</Link>
            <Link to="/my-questions" className={mobileNavLinkClass('/my-questions')}>My Questions</Link>
            <button
              onClick={onLogout}
              className="w-full flex items-center px-4 py-2.5 rounded-xl text-sm font-medium text-red-600 hover:bg-red-50 transition-all"
            >
              Sign Out
            </button>
          </div>
        </>
      ) : (
        <div className="px-3 space-y-2">
          <Link
            to="/login"
            className="block w-full text-center px-4 py-2.5 rounded-xl text-sm font-medium text-gray-700 border border-gray-300 hover:bg-gray-50 transition-all"
          >
            Sign In
          </Link>
          <Link
            to="/register"
            className="btn-primary w-full justify-center"
          >
            Get Started
          </Link>
        </div>
      )}
    </div>
  </div>
);

/* ── Navbar ── */
const Navbar: React.FC = () => {
  const { user, isAuthenticated, logout } = useAuthContext();
  const navigate = useNavigate();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Close mobile menu on route change
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const isActive = (path: string) => location.pathname === path;

  const navLinkClass = (path: string) =>
    [
      'relative px-3.5 py-2 rounded-lg text-sm font-medium transition-all duration-150',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500',
      isActive(path)
        ? 'bg-primary-50 text-primary-700'
        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100',
    ].join(' ');

  const mobileNavLinkClass = (path: string) =>
    [
      'flex items-center px-4 py-2.5 rounded-xl text-sm font-medium transition-all duration-150',
      'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500',
      isActive(path)
        ? 'bg-primary-50 text-primary-700'
        : 'text-gray-700 hover:bg-gray-100',
    ].join(' ');

  const initials =
    user?.full_name?.[0]?.toUpperCase() ||
    user?.email?.[0]?.toUpperCase() ||
    'U';

  return (
    <nav
      className="bg-white/95 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50"
      style={{ boxShadow: '0 1px 0 0 rgb(0 0 0 / 0.06)' }}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo + Desktop Nav */}
          <div className="flex items-center gap-8">
            <Link
              to="/"
              className="flex items-center gap-2 flex-shrink-0 group focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 rounded-lg"
            >
              <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent group-hover:from-primary-700 group-hover:to-indigo-700 transition-all">
                CivicQ
              </span>
            </Link>

            <div className="hidden md:flex items-center gap-1">
              <Link to="/" className={navLinkClass('/')}>
                Home
                {isActive('/') && (
                  <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 bg-primary-600 rounded-full" />
                )}
              </Link>
              <Link to="/ballot" className={navLinkClass('/ballot')}>
                My Ballot
                {isActive('/ballot') && (
                  <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 bg-primary-600 rounded-full" />
                )}
              </Link>
              {isAuthenticated && (
                <>
                  <Link to="/questions" className={navLinkClass('/questions')}>
                    Questions
                    {isActive('/questions') && (
                      <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 bg-primary-600 rounded-full" />
                    )}
                  </Link>
                  {user?.role === 'candidate' && (
                    <Link to="/candidate/dashboard" className={navLinkClass('/candidate/dashboard')}>
                      Dashboard
                      {isActive('/candidate/dashboard') && (
                        <span className="absolute bottom-0 left-1/2 -translate-x-1/2 w-4 h-0.5 bg-primary-600 rounded-full" />
                      )}
                    </Link>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Desktop right side */}
          <div className="hidden md:flex items-center gap-3">
            {isAuthenticated ? (
              <UserProfileDropdown user={user} initials={initials} onLogout={handleLogout} />
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-xl text-sm font-medium text-gray-700 hover:bg-gray-100 transition-all duration-150
                             focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
                >
                  Sign In
                </Link>
                <Link to="/register" className="btn-primary text-sm px-4 py-2">
                  Get Started
                </Link>
              </div>
            )}
          </div>

          {/* Mobile hamburger */}
          <div className="flex items-center md:hidden">
            <button
              onClick={() => setIsMobileMenuOpen((v) => !v)}
              aria-expanded={isMobileMenuOpen}
              aria-label="Toggle menu"
              className="p-2 rounded-xl text-gray-600 hover:bg-gray-100 transition-all duration-150
                         focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
            >
              {isMobileMenuOpen ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>

      {isMobileMenuOpen && (
        <MobileMenu
          isAuthenticated={isAuthenticated}
          user={user}
          initials={initials}
          mobileNavLinkClass={mobileNavLinkClass}
          onLogout={handleLogout}
        />
      )}
    </nav>
  );
};

export default Navbar;
