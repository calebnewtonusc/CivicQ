/**
 * Sentry Integration for CivicQ Frontend
 *
 * Comprehensive error tracking and performance monitoring for React application.
 * Includes error boundaries, user feedback, session replay, and performance monitoring.
 *
 * NOTE: Sentry is currently disabled. Install @sentry/react to enable error tracking.
 */

// Stub Sentry types and functions when package is not installed
type SeverityLevel = 'fatal' | 'error' | 'warning' | 'info' | 'debug';

/**
 * Initialize Sentry for error tracking and performance monitoring
 */
export function initSentry() {
  console.log('Sentry is not configured. Install @sentry/react to enable error tracking.');
}

/**
 * Set user context for error tracking
 */
export function setUserContext(_user: {
  id: string;
  email?: string;
  username?: string;
  role?: string;
  cityId?: string;
}) {
  // Stub: No-op when Sentry is not installed
}

/**
 * Clear user context (on logout)
 */
export function clearUserContext() {
  // Stub: No-op when Sentry is not installed
}

/**
 * Add custom context to error reports
 */
export function setContext(_name: string, _context: Record<string, any>) {
  // Stub: No-op when Sentry is not installed
}

/**
 * Add breadcrumb for debugging
 */
export function addBreadcrumb(
  _message: string,
  _category?: string,
  _level?: SeverityLevel,
  _data?: Record<string, any>
) {
  // Stub: No-op when Sentry is not installed
}

/**
 * Manually capture an exception
 */
export function captureException(error: Error, context?: Record<string, any>) {
  console.error('Error captured:', error, context);
}

/**
 * Capture a message
 */
export function captureMessage(
  message: string,
  level: SeverityLevel = 'info',
  context?: Record<string, any>
) {
  console.log(`[${level}] ${message}`, context);
}

/**
 * Start a performance transaction
 */
export function startTransaction(_name: string, _op: string) {
  return {
    finish: () => {},
    setStatus: () => {},
    setTag: () => {},
    setData: () => {},
  };
}

/**
 * Show user feedback dialog
 */
export function showReportDialog(_eventId?: string) {
  // Stub: No-op when Sentry is not installed
  alert('Error reporting is not configured. Please contact support.');
}
