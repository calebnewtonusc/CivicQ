import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider } from './contexts/AuthContext';
import LoadingSpinner from './components/LoadingSpinner';
import { AdminPermission } from './types';

// Eager load critical pages for instant display
import SimpleHomePage from './pages/SimpleHomePage';
import NotFoundPage from './pages/NotFoundPage';

// Lazy load all other pages for better code splitting
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const BallotPage = lazy(() => import('./pages/BallotPage'));
const ContestPage = lazy(() => import('./pages/ContestPage'));
const QuestionPage = lazy(() => import('./pages/QuestionPage'));
const CandidatePage = lazy(() => import('./pages/CandidatePage'));

// Candidate Portal Pages (lazy loaded)
const CandidateDashboardPage = lazy(() => import('./pages/CandidateDashboardPage'));
const CandidateProfileEditPage = lazy(() => import('./pages/CandidateProfileEditPage'));
const CandidateAnswerPage = lazy(() => import('./pages/CandidateAnswerPage'));
const CandidateOnboardingPage = lazy(() => import('./pages/CandidateOnboardingPage'));

// City Onboarding Pages (lazy loaded)
const CityRegistrationPage = lazy(() => import('./pages/CityRegistrationPage'));
const CitySetupWizardPage = lazy(() => import('./pages/CitySetupWizardPage'));
const CityDashboardPage = lazy(() => import('./pages/CityDashboardPage'));
const CityBallotImportPage = lazy(() => import('./pages/CityBallotImportPage'));
const CityPendingVerificationPage = lazy(() => import('./pages/CityPendingVerificationPage'));

// Admin Panel Pages (lazy loaded)
const AdminLayout = lazy(() => import('./components/admin/AdminLayout'));
const AdminRoute = lazy(() => import('./components/admin/AdminRoute'));
const AdminDashboard = lazy(() => import('./pages/admin/AdminDashboard'));
const QuestionModeration = lazy(() => import('./pages/admin/QuestionModeration'));
const UserManagement = lazy(() => import('./pages/admin/UserManagement'));
const ContentModeration = lazy(() => import('./pages/admin/ContentModeration'));
const Analytics = lazy(() => import('./pages/admin/Analytics'));
const CityConfiguration = lazy(() => import('./pages/admin/CityConfiguration'));
const AuditLog = lazy(() => import('./pages/admin/AuditLog'));

// Legal Pages (lazy loaded)
const TermsOfServicePage = lazy(() => import('./pages/TermsOfServicePage'));
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicyPage'));
const AccessibilityStatementPage = lazy(() => import('./pages/AccessibilityStatementPage'));
const CookiePolicyPage = lazy(() => import('./pages/CookiePolicyPage'));
const DataProcessingAgreementPage = lazy(() => import('./pages/DataProcessingAgreementPage'));

// Create React Query client with optimized caching
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
      gcTime: 10 * 60 * 1000, // 10 minutes
    },
  },
});

// Loading fallback component
const PageLoader = () => (
  <div className="min-h-screen bg-gray-50 flex items-center justify-center">
    <LoadingSpinner />
  </div>
);

function App() {
  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <BrowserRouter>
            <div className="min-h-screen bg-gray-50">
              <Suspense fallback={<PageLoader />}>
                <Routes>
                  <Route path="/" element={<SimpleHomePage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  <Route path="/ballot" element={<BallotPage />} />
                  <Route path="/contest/:contestId" element={<ContestPage />} />
                  <Route path="/question/:questionId" element={<QuestionPage />} />
                  <Route path="/candidate/:candidateId" element={<CandidatePage />} />

                  {/* Candidate Portal Routes */}
                  <Route path="/candidate/dashboard" element={<CandidateDashboardPage />} />
                  <Route path="/candidate/profile/edit" element={<CandidateProfileEditPage />} />
                  <Route path="/candidate/answer/:questionId" element={<CandidateAnswerPage />} />
                  <Route path="/candidate/onboarding" element={<CandidateOnboardingPage />} />

                  {/* City Onboarding Routes */}
                  <Route path="/city/register" element={<CityRegistrationPage />} />
                  <Route path="/city/:cityId/pending-verification" element={<CityPendingVerificationPage />} />
                  <Route path="/city/:cityId/setup" element={<CitySetupWizardPage />} />
                  <Route path="/city/:cityId/dashboard" element={<CityDashboardPage />} />
                  <Route path="/city/:cityId/import/manual" element={<CityBallotImportPage />} />

                  {/* Admin Panel Routes */}
                  <Route path="/admin" element={<AdminRoute><AdminLayout /></AdminRoute>}>
                    <Route index element={<AdminDashboard />} />
                    <Route
                      path="questions"
                      element={
                        <AdminRoute requiredPermission={AdminPermission.MODERATE_QUESTIONS}>
                          <QuestionModeration />
                        </AdminRoute>
                      }
                    />
                    <Route
                      path="users"
                      element={
                        <AdminRoute requiredPermission={AdminPermission.MANAGE_USERS}>
                          <UserManagement />
                        </AdminRoute>
                      }
                    />
                    <Route
                      path="content"
                      element={
                        <AdminRoute requiredPermission={AdminPermission.MODERATE_CONTENT}>
                          <ContentModeration />
                        </AdminRoute>
                      }
                    />
                    <Route
                      path="analytics"
                      element={
                        <AdminRoute requiredPermission={AdminPermission.VIEW_ANALYTICS}>
                          <Analytics />
                        </AdminRoute>
                      }
                    />
                    <Route
                      path="config"
                      element={
                        <AdminRoute requiredPermission={AdminPermission.MANAGE_CITY_CONFIG}>
                          <CityConfiguration />
                        </AdminRoute>
                      }
                    />
                    <Route
                      path="audit"
                      element={
                        <AdminRoute requiredPermission={AdminPermission.VIEW_AUDIT_LOG}>
                          <AuditLog />
                        </AdminRoute>
                      }
                    />
                  </Route>

                  {/* Legal Pages */}
                  <Route path="/terms" element={<TermsOfServicePage />} />
                  <Route path="/privacy" element={<PrivacyPolicyPage />} />
                  <Route path="/accessibility" element={<AccessibilityStatementPage />} />
                  <Route path="/cookies" element={<CookiePolicyPage />} />
                  <Route path="/dpa" element={<DataProcessingAgreementPage />} />

                  <Route path="*" element={<NotFoundPage />} />
                </Routes>
              </Suspense>
            </div>
          </BrowserRouter>
        </AuthProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

export default App;
