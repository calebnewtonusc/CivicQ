import React, { useReducer, useCallback } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuthContext } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

/* ── Field-level inline validation state ── */
interface FieldError {
  email?: string;
  password?: string;
}

interface LoginState {
  email: string;
  password: string;
  showPassword: boolean;
  globalError: string;
  fieldErrors: FieldError;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
}

type LoginAction =
  | { type: 'SET_EMAIL'; payload: string }
  | { type: 'SET_PASSWORD'; payload: string }
  | { type: 'TOGGLE_SHOW_PASSWORD' }
  | { type: 'SET_GLOBAL_ERROR'; payload: string }
  | { type: 'SET_FIELD_ERRORS'; payload: FieldError }
  | { type: 'PATCH_FIELD_ERROR'; payload: { field: keyof FieldError; error: string } }
  | { type: 'SET_TOUCHED'; payload: Record<string, boolean> }
  | { type: 'PATCH_TOUCHED'; payload: { field: string; value: boolean } }
  | { type: 'SET_SUBMITTING'; payload: boolean };

const initialLoginState: LoginState = {
  email: '',
  password: '',
  showPassword: false,
  globalError: '',
  fieldErrors: {},
  touched: {},
  isSubmitting: false,
};

function loginReducer(state: LoginState, action: LoginAction): LoginState {
  switch (action.type) {
    case 'SET_EMAIL':
      return { ...state, email: action.payload };
    case 'SET_PASSWORD':
      return { ...state, password: action.payload };
    case 'TOGGLE_SHOW_PASSWORD':
      return { ...state, showPassword: !state.showPassword };
    case 'SET_GLOBAL_ERROR':
      return { ...state, globalError: action.payload };
    case 'SET_FIELD_ERRORS':
      return { ...state, fieldErrors: action.payload };
    case 'PATCH_FIELD_ERROR':
      return { ...state, fieldErrors: { ...state.fieldErrors, [action.payload.field]: action.payload.error } };
    case 'SET_TOUCHED':
      return { ...state, touched: action.payload };
    case 'PATCH_TOUCHED':
      return { ...state, touched: { ...state.touched, [action.payload.field]: action.payload.value } };
    case 'SET_SUBMITTING':
      return { ...state, isSubmitting: action.payload };
    default:
      return state;
  }
}

const LoginPage: React.FC = () => {
  const [state, dispatch] = useReducer(loginReducer, initialLoginState);
  const { email, password, showPassword, globalError, fieldErrors, touched, isSubmitting } = state;

  const { login, isAuthenticated } = useAuthContext();
  const navigate   = useNavigate();
  const location   = useLocation();

  React.useEffect(() => {
    if (isAuthenticated) {
      const from = (location.state as any)?.from?.pathname || '/ballot';
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, location]);

  /* ── Live validation per field ── */
  const validateEmail = useCallback((value: string) => {
    if (!value.trim()) return 'Email is required';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)) return 'Enter a valid email address';
    return '';
  }, []);

  const validatePassword = useCallback((value: string) => {
    if (!value) return 'Password is required';
    if (value.length < 6) return 'Password must be at least 6 characters';
    return '';
  }, []);

  const handleBlur = (field: keyof FieldError, value: string) => {
    dispatch({ type: 'PATCH_TOUCHED', payload: { field, value: true } });
    const err = field === 'email' ? validateEmail(value) : validatePassword(value);
    dispatch({ type: 'PATCH_FIELD_ERROR', payload: { field, error: err } });
  };

  const validateAll = (): boolean => {
    const emailErr    = validateEmail(email);
    const passwordErr = validatePassword(password);
    dispatch({ type: 'SET_FIELD_ERRORS', payload: { email: emailErr, password: passwordErr } });
    dispatch({ type: 'SET_TOUCHED', payload: { email: true, password: true } });
    return !emailErr && !passwordErr;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    dispatch({ type: 'SET_GLOBAL_ERROR', payload: '' });
    if (!validateAll()) return;

    dispatch({ type: 'SET_SUBMITTING', payload: true });
    try {
      await login(email.trim(), password);
    } catch (error: any) {
      dispatch({
        type: 'SET_GLOBAL_ERROR',
        payload: error?.response?.data?.detail ||
          'Login failed. Please check your credentials and try again.',
      });
    } finally {
      dispatch({ type: 'SET_SUBMITTING', payload: false });
    }
  };

  const inputClass = (field: keyof FieldError) => {
    const hasError = touched[field] && fieldErrors[field];
    return [
      'form-input pl-10',
      hasError ? 'border-danger-500 focus:ring-danger-500' : '',
    ].join(' ');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-indigo-50 flex flex-col">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link
            to="/"
            className="inline-flex items-center gap-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 rounded-lg"
          >
            <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent">
              CivicQ
            </span>
          </Link>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center px-4 py-12 sm:py-16">
        <div className="w-full max-w-md animate-fade-in">
          {/* Card */}
          <div className="card shadow-card-xl overflow-hidden">
            {/* Card hero */}
            <div className="bg-gradient-to-r from-primary-600 to-indigo-600 px-8 py-7 text-center">
              <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-white">Welcome Back</h1>
              <p className="text-primary-100 text-sm mt-1">Sign in to continue to CivicQ</p>
            </div>

            <div className="px-8 py-8">
              {/* Global error */}
              {globalError && (
                <div
                  role="alert"
                  className="flex items-start gap-3 mb-6 p-4 bg-danger-50 border border-danger-200 rounded-xl animate-fade-in"
                >
                  <svg className="w-5 h-5 text-danger-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-danger-800">Login failed</p>
                    <p className="text-sm text-danger-700 mt-0.5">{globalError}</p>
                  </div>
                  <button
                    onClick={() => dispatch({ type: 'SET_GLOBAL_ERROR', payload: '' })}
                    className="text-danger-400 hover:text-danger-600 transition-colors"
                    aria-label="Dismiss error"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-5" noValidate>
                {/* Email */}
                <div>
                  <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-1.5">
                    Email Address
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                      <svg className={`h-4 w-4 transition-colors ${touched.email && fieldErrors.email ? 'text-danger-400' : 'text-gray-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                      </svg>
                    </div>
                    <input
                      id="email"
                      type="email"
                      value={email}
                      onChange={(e) => {
                        dispatch({ type: 'SET_EMAIL', payload: e.target.value });
                        if (touched.email) {
                          dispatch({ type: 'PATCH_FIELD_ERROR', payload: { field: 'email', error: validateEmail(e.target.value) } });
                        }
                      }}
                      onBlur={(e) => handleBlur('email', e.target.value)}
                      placeholder="you@example.com"
                      className={inputClass('email')}
                      disabled={isSubmitting}
                      autoComplete="email"
                      aria-invalid={!!(touched.email && fieldErrors.email)}
                      aria-describedby={fieldErrors.email ? 'email-error' : undefined}
                    />
                    {touched.email && !fieldErrors.email && email && (
                      <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                        <svg className="w-4 h-4 text-success-500" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      </div>
                    )}
                  </div>
                  {touched.email && fieldErrors.email && (
                    <p id="email-error" className="mt-1.5 text-xs font-medium text-danger-600 flex items-center gap-1 animate-fade-in">
                      <svg className="w-3.5 h-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      {fieldErrors.email}
                    </p>
                  )}
                </div>

                {/* Password */}
                <div>
                  <div className="flex items-center justify-between mb-1.5">
                    <label htmlFor="password" className="block text-sm font-semibold text-gray-700">
                      Password
                    </label>
                    <Link
                      to="/forgot-password"
                      className="text-xs font-medium text-primary-600 hover:text-primary-700 transition-colors focus-visible:outline-none focus-visible:underline"
                    >
                      Forgot password?
                    </Link>
                  </div>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                      <svg className={`h-4 w-4 transition-colors ${touched.password && fieldErrors.password ? 'text-danger-400' : 'text-gray-400'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                    </div>
                    <input
                      id="password"
                      type={showPassword ? 'text' : 'password'}
                      value={password}
                      onChange={(e) => {
                        dispatch({ type: 'SET_PASSWORD', payload: e.target.value });
                        if (touched.password) {
                          dispatch({ type: 'PATCH_FIELD_ERROR', payload: { field: 'password', error: validatePassword(e.target.value) } });
                        }
                      }}
                      onBlur={(e) => handleBlur('password', e.target.value)}
                      placeholder="Enter your password"
                      className={`${inputClass('password')} pr-11`}
                      disabled={isSubmitting}
                      autoComplete="current-password"
                      aria-invalid={!!(touched.password && fieldErrors.password)}
                      aria-describedby={fieldErrors.password ? 'password-error' : undefined}
                    />
                    <button
                      type="button"
                      onClick={() => dispatch({ type: 'TOGGLE_SHOW_PASSWORD' })}
                      disabled={isSubmitting}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                      className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600 transition-colors focus-visible:outline-none"
                    >
                      {showPassword ? (
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                        </svg>
                      ) : (
                        <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      )}
                    </button>
                  </div>
                  {touched.password && fieldErrors.password && (
                    <p id="password-error" className="mt-1.5 text-xs font-medium text-danger-600 flex items-center gap-1 animate-fade-in">
                      <svg className="w-3.5 h-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      {fieldErrors.password}
                    </p>
                  )}
                </div>

                {/* Submit */}
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="btn-primary w-full py-3 text-base mt-2"
                >
                  {isSubmitting ? (
                    <>
                      <LoadingSpinner size="xs" inline />
                      Signing in…
                    </>
                  ) : (
                    'Sign In'
                  )}
                </button>
              </form>

              {/* Divider */}
              <div className="my-6 flex items-center gap-3">
                <div className="flex-1 h-px bg-gray-200" />
                <span className="text-xs font-medium text-gray-400">Don't have an account?</span>
                <div className="flex-1 h-px bg-gray-200" />
              </div>

              <Link
                to="/register"
                className="btn-secondary w-full justify-center py-3 text-sm"
              >
                Create New Account
              </Link>
            </div>
          </div>

          {/* Back to home */}
          <div className="text-center mt-6">
            <Link
              to="/"
              className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors focus-visible:outline-none focus-visible:underline"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back to Home
            </Link>
          </div>
        </div>
      </main>

      <footer className="bg-white border-t border-gray-100 py-5 text-center text-sm text-gray-400">
        Making democracy more accessible, one question at a time.
      </footer>
    </div>
  );
};

export default LoginPage;
