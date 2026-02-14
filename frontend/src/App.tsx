import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider } from './contexts/AuthContext';

// Pages
import SimpleHomePage from './pages/SimpleHomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import BallotPage from './pages/BallotPage';
import ContestPage from './pages/ContestPage';
import QuestionPage from './pages/QuestionPage';
import CandidatePage from './pages/CandidatePage';
import NotFoundPage from './pages/NotFoundPage';

// Candidate Portal Pages
import CandidateDashboardPage from './pages/CandidateDashboardPage';
import CandidateProfileEditPage from './pages/CandidateProfileEditPage';
import CandidateAnswerPage from './pages/CandidateAnswerPage';
import CandidateOnboardingPage from './pages/CandidateOnboardingPage';

// City Onboarding Pages
import CityRegistrationPage from './pages/CityRegistrationPage';
import CitySetupWizardPage from './pages/CitySetupWizardPage';
import CityDashboardPage from './pages/CityDashboardPage';
import CityBallotImportPage from './pages/CityBallotImportPage';
import CityPendingVerificationPage from './pages/CityPendingVerificationPage';

// Admin Panel Pages
import AdminLayout from './components/admin/AdminLayout';
import AdminRoute from './components/admin/AdminRoute';
import {
  AdminDashboard,
  QuestionModeration,
  UserManagement,
  ContentModeration,
  Analytics,
  CityConfiguration,
  AuditLog,
} from './pages/admin';
import { AdminPermission } from './types';

// Legal Pages
import TermsOfServicePage from './pages/TermsOfServicePage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import AccessibilityStatementPage from './pages/AccessibilityStatementPage';
import CookiePolicyPage from './pages/CookiePolicyPage';
import DataProcessingAgreementPage from './pages/DataProcessingAgreementPage';

// Create React Query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <BrowserRouter>
            <div className="min-h-screen bg-gray-50">
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
            </div>
          </BrowserRouter>
        </AuthProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
}

export default App;
