import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';

// Pages
import HomePage from './pages/HomePage';
import BallotPage from './pages/BallotPage';
import ContestPage from './pages/ContestPage';
import QuestionPage from './pages/QuestionPage';
import CandidatePage from './pages/CandidatePage';

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
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <div className="min-h-screen bg-gray-50">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/ballot" element={<BallotPage />} />
              <Route path="/contest/:contestId" element={<ContestPage />} />
              <Route path="/question/:questionId" element={<QuestionPage />} />
              <Route path="/candidate/:candidateId" element={<CandidatePage />} />
            </Routes>
          </div>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
