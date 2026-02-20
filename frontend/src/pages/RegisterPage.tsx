import React, { useReducer, useCallback, Dispatch } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthContext } from '../contexts/AuthContext';
import LoadingSpinner from '../components/LoadingSpinner';

interface FormData {
  email: string;
  password: string;
  confirmPassword: string;
  fullName: string;
  cityId: string;
}

interface FieldErrors {
  email?: string;
  password?: string;
  confirmPassword?: string;
  fullName?: string;
}

/* ── Helpers ── */
const calcPasswordStrength = (pw: string): number => {
  let s = 0;
  if (pw.length >= 8) s += 25;
  if (pw.length >= 12) s += 25;
  if (/[a-z]/.test(pw) && /[A-Z]/.test(pw)) s += 25;
  if (/\d/.test(pw)) s += 15;
  if (/[^a-zA-Z0-9]/.test(pw)) s += 10;
  return Math.min(s, 100);
};

const strengthLabel = (s: number) => {
  if (s < 40) return { label: 'Weak', color: 'bg-danger-500', text: 'text-danger-600' };
  if (s < 70) return { label: 'Fair', color: 'bg-warning-500', text: 'text-warning-600' };
  return { label: 'Strong', color: 'bg-success-500', text: 'text-success-600' };
};

const EyeIcon: React.FC<{ off?: boolean }> = ({ off }) =>
  off ? (
    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
    </svg>
  ) : (
    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
    </svg>
  );

const InlineError: React.FC<{ id: string; message?: string }> = ({ id, message }) =>
  message ? (
    <p id={id} className="mt-1.5 text-xs font-medium text-danger-600 flex items-center gap-1 animate-fade-in">
      <svg className="w-3.5 h-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
      </svg>
      {message}
    </p>
  ) : null;

/* ── useReducer state for RegisterPage ── */
interface RegisterState {
  formData: FormData;
  showPassword: boolean;
  showConfirmPassword: boolean;
  globalError: string;
  fieldErrors: FieldErrors;
  touched: Record<string, boolean>;
  isSubmitting: boolean;
  passwordStrength: number;
}

type RegisterAction =
  | { type: 'SET_FORM_FIELD'; payload: { field: keyof FormData; value: string } }
  | { type: 'TOGGLE_SHOW_PASSWORD' }
  | { type: 'TOGGLE_SHOW_CONFIRM_PASSWORD' }
  | { type: 'SET_GLOBAL_ERROR'; payload: string }
  | { type: 'SET_FIELD_ERRORS'; payload: FieldErrors }
  | { type: 'PATCH_FIELD_ERROR'; payload: { field: keyof FieldErrors; error: string } }
  | { type: 'SET_TOUCHED'; payload: Record<string, boolean> }
  | { type: 'PATCH_TOUCHED'; payload: { field: string; value: boolean } }
  | { type: 'SET_SUBMITTING'; payload: boolean }
  | { type: 'SET_PASSWORD_STRENGTH'; payload: number };

const initialRegisterState: RegisterState = {
  formData: { email: '', password: '', confirmPassword: '', fullName: '', cityId: '' },
  showPassword: false,
  showConfirmPassword: false,
  globalError: '',
  fieldErrors: {},
  touched: {},
  isSubmitting: false,
  passwordStrength: 0,
};

function registerReducer(state: RegisterState, action: RegisterAction): RegisterState {
  switch (action.type) {
    case 'SET_FORM_FIELD':
      return { ...state, formData: { ...state.formData, [action.payload.field]: action.payload.value } };
    case 'TOGGLE_SHOW_PASSWORD':
      return { ...state, showPassword: !state.showPassword };
    case 'TOGGLE_SHOW_CONFIRM_PASSWORD':
      return { ...state, showConfirmPassword: !state.showConfirmPassword };
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
    case 'SET_PASSWORD_STRENGTH':
      return { ...state, passwordStrength: action.payload };
    default:
      return state;
  }
}

/* ── FieldIcon ── */
interface FieldIconProps {
  field: keyof FieldErrors;
  icon: React.ReactNode;
  touched: Record<string, boolean>;
  fieldErrors: FieldErrors;
}

const FieldIcon: React.FC<FieldIconProps> = ({ field, icon, touched, fieldErrors }) => (
  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
    <span className={`h-4 w-4 transition-colors ${touched[field] && fieldErrors[field] ? 'text-danger-400' : 'text-gray-400'}`}>
      {icon}
    </span>
  </div>
);

/* ── RegisterForm ── */
interface RegisterFormProps {
  state: RegisterState;
  dispatch: Dispatch<RegisterAction>;
  onSubmit: (e: React.FormEvent) => void;
  inputClass: (field: keyof FieldErrors) => string;
}

const RegisterForm: React.FC<RegisterFormProps> = ({ state, dispatch, onSubmit, inputClass }) => {
  const { formData, showPassword, showConfirmPassword, globalError, fieldErrors, touched, isSubmitting, passwordStrength } = state;
  const strength = strengthLabel(passwordStrength);

  return (
    <div className="card shadow-card-xl overflow-hidden">
      {/* Card hero */}
      <div className="bg-gradient-to-r from-primary-600 to-indigo-600 px-8 py-7 text-center">
        <div className="w-14 h-14 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-4">
          <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z" />
          </svg>
        </div>
        <h1 className="text-2xl font-bold text-white">Create Account</h1>
        <p className="text-primary-100 text-sm mt-1">Join CivicQ and make your voice heard</p>
      </div>

      <div className="px-8 py-8">
        {/* Global error */}
        {globalError && (
          <div role="alert" className="flex items-start gap-3 mb-6 p-4 bg-danger-50 border border-danger-200 rounded-xl animate-fade-in">
            <svg className="w-5 h-5 text-danger-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div className="flex-1">
              <p className="text-sm font-semibold text-danger-800">Registration failed</p>
              <p className="text-sm text-danger-700 mt-0.5">{globalError}</p>
            </div>
            <button onClick={() => dispatch({ type: 'SET_GLOBAL_ERROR', payload: '' })} className="text-danger-400 hover:text-danger-600 transition-colors" aria-label="Dismiss">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        <form onSubmit={onSubmit} className="space-y-5" noValidate>
          {/* Full Name */}
          <div>
            <label htmlFor="fullName" className="block text-sm font-semibold text-gray-700 mb-1.5">Full Name</label>
            <div className="relative">
              <FieldIcon field="fullName" touched={touched} fieldErrors={fieldErrors} icon={
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              } />
              <input
                id="fullName"
                type="text"
                value={formData.fullName}
                onChange={(e) => dispatch({ type: 'SET_FORM_FIELD', payload: { field: 'fullName', value: e.target.value } })}
                onBlur={() => dispatch({ type: 'PATCH_TOUCHED', payload: { field: 'fullName', value: true } })}
                placeholder="Jane Doe"
                className={inputClass('fullName')}
                disabled={isSubmitting}
                autoComplete="name"
              />
            </div>
            <InlineError id="fullName-error" message={touched.fullName ? fieldErrors.fullName : undefined} />
          </div>

          {/* Email */}
          <div>
            <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-1.5">Email Address</label>
            <div className="relative">
              <FieldIcon field="email" touched={touched} fieldErrors={fieldErrors} icon={
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
              } />
              <input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => dispatch({ type: 'SET_FORM_FIELD', payload: { field: 'email', value: e.target.value } })}
                onBlur={() => dispatch({ type: 'PATCH_TOUCHED', payload: { field: 'email', value: true } })}
                placeholder="you@example.com"
                className={inputClass('email')}
                disabled={isSubmitting}
                autoComplete="email"
              />
            </div>
            <InlineError id="email-error" message={touched.email ? fieldErrors.email : undefined} />
          </div>

          {/* City (optional) */}
          <div>
            <label htmlFor="cityId" className="block text-sm font-semibold text-gray-700 mb-1.5">
              City <span className="text-gray-400 font-normal">(optional)</span>
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-gray-400">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <input
                id="cityId"
                type="text"
                value={formData.cityId}
                onChange={(e) => dispatch({ type: 'SET_FORM_FIELD', payload: { field: 'cityId', value: e.target.value } })}
                placeholder="e.g., los-angeles-ca"
                className="form-input pl-10"
                disabled={isSubmitting}
              />
            </div>
            <p className="mt-1 text-xs text-gray-400">Enter your city ID to see relevant elections</p>
          </div>

          {/* Password */}
          <div>
            <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-1.5">Password</label>
            <div className="relative">
              <FieldIcon field="password" touched={touched} fieldErrors={fieldErrors} icon={
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              } />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => dispatch({ type: 'SET_FORM_FIELD', payload: { field: 'password', value: e.target.value } })}
                onBlur={() => dispatch({ type: 'PATCH_TOUCHED', payload: { field: 'password', value: true } })}
                placeholder="Min. 8 characters"
                className={`${inputClass('password')} pr-11`}
                disabled={isSubmitting}
                autoComplete="new-password"
              />
              <button type="button" onClick={() => dispatch({ type: 'TOGGLE_SHOW_PASSWORD' })} disabled={isSubmitting}
                className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600 transition-colors focus-visible:outline-none" aria-label={showPassword ? 'Hide password' : 'Show password'}>
                <EyeIcon off={showPassword} />
              </button>
            </div>
            {formData.password && (
              <div className="mt-2 space-y-1 animate-fade-in">
                <div className="flex items-center gap-2">
                  <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${strength.color}`}
                      style={{ width: `${passwordStrength}%` }}
                    />
                  </div>
                  <span className={`text-xs font-semibold ${strength.text}`}>{strength.label}</span>
                </div>
              </div>
            )}
            <InlineError id="password-error" message={touched.password ? fieldErrors.password : undefined} />
          </div>

          {/* Confirm Password */}
          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-semibold text-gray-700 mb-1.5">Confirm Password</label>
            <div className="relative">
              <FieldIcon field="confirmPassword" touched={touched} fieldErrors={fieldErrors} icon={
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              } />
              <input
                id="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={(e) => dispatch({ type: 'SET_FORM_FIELD', payload: { field: 'confirmPassword', value: e.target.value } })}
                onBlur={() => dispatch({ type: 'PATCH_TOUCHED', payload: { field: 'confirmPassword', value: true } })}
                placeholder="Re-enter password"
                className={`${inputClass('confirmPassword')} pr-11`}
                disabled={isSubmitting}
                autoComplete="new-password"
              />
              <button type="button" onClick={() => dispatch({ type: 'TOGGLE_SHOW_CONFIRM_PASSWORD' })} disabled={isSubmitting}
                className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-gray-400 hover:text-gray-600 transition-colors focus-visible:outline-none" aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}>
                <EyeIcon off={showConfirmPassword} />
              </button>
            </div>
            {formData.confirmPassword && !fieldErrors.confirmPassword && (
              <p className="mt-1.5 text-xs font-medium text-success-600 flex items-center gap-1 animate-fade-in">
                <svg className="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                Passwords match
              </p>
            )}
            <InlineError id="confirmPassword-error" message={touched.confirmPassword ? fieldErrors.confirmPassword : undefined} />
          </div>

          {/* Terms */}
          <div className="flex items-start gap-3 pt-1">
            <input
              id="terms"
              type="checkbox"
              required
              className="mt-0.5 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500 transition-colors"
              disabled={isSubmitting}
            />
            <label htmlFor="terms" className="text-sm text-gray-600 leading-relaxed">
              I agree to the{' '}
              <Link to="/terms" className="text-primary-600 hover:text-primary-700 font-medium transition-colors">Terms of Service</Link>
              {' '}and{' '}
              <Link to="/privacy" className="text-primary-600 hover:text-primary-700 font-medium transition-colors">Privacy Policy</Link>
            </label>
          </div>

          {/* Submit */}
          <button type="submit" disabled={isSubmitting} className="btn-primary w-full py-3 text-base mt-1">
            {isSubmitting ? (
              <>
                <LoadingSpinner size="xs" inline />
                Creating Account…
              </>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        {/* Divider */}
        <div className="my-6 flex items-center gap-3">
          <div className="flex-1 h-px bg-gray-200" />
          <span className="text-xs font-medium text-gray-400">Already have an account?</span>
          <div className="flex-1 h-px bg-gray-200" />
        </div>

        <Link to="/login" className="btn-secondary w-full justify-center py-3 text-sm">
          Sign In Instead
        </Link>
      </div>
    </div>
  );
};

/* ── RegisterPage ── */
const RegisterPage: React.FC = () => {
  const [state, dispatch] = useReducer(registerReducer, initialRegisterState);
  const { formData, fieldErrors, touched, isSubmitting } = state;

  const { isAuthenticated } = useAuthContext();
  const navigate = useNavigate();

  React.useEffect(() => {
    if (isAuthenticated) navigate('/ballot', { replace: true });
  }, [isAuthenticated, navigate]);

  /* ── Validators ── */
  const validators: Record<keyof FieldErrors, (data: FormData) => string> = {
    fullName: (d) => {
      if (!d.fullName.trim()) return 'Full name is required';
      if (d.fullName.trim().length < 2) return 'Full name must be at least 2 characters';
      return '';
    },
    email: (d) => {
      if (!d.email.trim()) return 'Email is required';
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email)) return 'Enter a valid email address';
      return '';
    },
    password: (d) => {
      if (!d.password) return 'Password is required';
      if (d.password.length < 8) return 'Password must be at least 8 characters';
      return '';
    },
    confirmPassword: (d) => {
      if (!d.confirmPassword) return 'Please confirm your password';
      if (d.confirmPassword !== d.password) return 'Passwords do not match';
      return '';
    },
  };

  const validateField = useCallback(
    (field: keyof FieldErrors, data: FormData) => validators[field](data),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  );

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    dispatch({ type: 'SET_GLOBAL_ERROR', payload: '' });

    const errors: FieldErrors = {
      fullName:        validators.fullName(formData),
      email:           validators.email(formData),
      password:        validators.password(formData),
      confirmPassword: validators.confirmPassword(formData),
    };
    dispatch({ type: 'SET_FIELD_ERRORS', payload: errors });
    dispatch({ type: 'SET_TOUCHED', payload: { fullName: true, email: true, password: true, confirmPassword: true } });
    if (!Object.values(errors).every((err) => !err)) return;

    dispatch({ type: 'SET_SUBMITTING', payload: true });
    try {
      const { authAPI } = await import('../services/api');
      const response = await authAPI.register({
        email: formData.email.trim(),
        password: formData.password,
        full_name: formData.fullName.trim(),
        city_id: formData.cityId || undefined,
      });
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));
      navigate('/ballot');
    } catch (error: any) {
      dispatch({
        type: 'SET_GLOBAL_ERROR',
        payload: error?.response?.data?.detail ||
          'Registration failed. This email may already be registered.',
      });
    } finally {
      dispatch({ type: 'SET_SUBMITTING', payload: false });
    }
  };

  // Expose validateField so it's used (avoids lint warning)
  void validateField;

  const inputClass = (field: keyof FieldErrors) => {
    const hasError = touched[field] && fieldErrors[field];
    return ['form-input pl-10', hasError ? 'border-danger-500 focus:ring-danger-500' : ''].join(' ');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-indigo-50 flex flex-col">
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link to="/" className="inline-flex items-center gap-1 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 rounded-lg">
            <span className="text-2xl font-bold bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent">
              CivicQ
            </span>
          </Link>
        </div>
      </header>

      <main className="flex-1 flex items-center justify-center px-4 py-10 sm:py-14">
        <div className="w-full max-w-md animate-fade-in">
          <RegisterForm
            state={state}
            dispatch={dispatch}
            onSubmit={handleSubmit}
            inputClass={inputClass}
          />

          <div className="text-center mt-6">
            <Link to="/" className="inline-flex items-center gap-1.5 text-sm font-medium text-gray-500 hover:text-gray-700 transition-colors focus-visible:outline-none focus-visible:underline">
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

export default RegisterPage;
