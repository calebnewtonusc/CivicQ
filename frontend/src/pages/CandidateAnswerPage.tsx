import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Layout } from '../components';
import { useAuthContext } from '../contexts/AuthContext';
import { VideoAnswerRecorder } from '../components/VideoAnswerRecorder';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

interface Question {
  id: number;
  question_text: string;
  issue_tags: string[];
  upvotes: number;
  downvotes: number;
  rank_score: number;
  created_at: string;
  context?: string;
}

export default function CandidateAnswerPage() {
  const { questionId } = useParams<{ questionId: string }>();
  const { user, isAuthenticated, isLoading: authLoading } = useAuthContext();
  const navigate = useNavigate();

  const [question, setQuestion] = useState<Question | null>(null);
  const [candidateId] = useState(1); // Replace with actual candidate ID
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login');
      return;
    }

    if (user && user.role !== 'candidate') {
      setError('You must be a candidate to access this page');
      setLoading(false);
      return;
    }

    if (questionId) {
      loadQuestion(parseInt(questionId));
    }
  }, [questionId, user, isAuthenticated, authLoading, navigate]);

  const loadQuestion = async (qId: number) => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/questions/${qId}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load question');
      }

      const data = await response.json();
      setQuestion(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load question:', err);
      setError('Failed to load question. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSuccess = () => {
    navigate('/candidate/dashboard');
  };

  const handleCancel = () => {
    navigate('/candidate/dashboard');
  };

  if (authLoading || loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center min-h-[60vh]">
          <LoadingSpinner size="lg" />
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <ErrorMessage message={error} />
          <button
            onClick={() => navigate('/candidate/dashboard')}
            className="mt-4 text-blue-600 hover:text-blue-500"
          >
            Return to Dashboard
          </button>
        </div>
      </Layout>
    );
  }

  if (!question) {
    return null;
  }

  return (
    <Layout>
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => navigate('/candidate/dashboard')}
            className="text-blue-600 hover:text-blue-500 mb-4 flex items-center"
          >
            <svg className="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold text-gray-900">Record Your Answer</h1>
          <p className="mt-2 text-gray-600">
            Take your time to provide a thoughtful, authentic response to this voter question.
          </p>
        </div>

        {/* Question Context */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h2 className="text-xl font-semibold text-gray-900 mb-3">
                Question from Voters
              </h2>
              <p className="text-lg text-gray-800 mb-4">
                {question.question_text}
              </p>

              {question.context && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-700 mb-1">Additional Context:</p>
                  <p className="text-sm text-gray-600">{question.context}</p>
                </div>
              )}

              {Array.isArray(question.issue_tags) && question.issue_tags.length > 0 && (
                <div className="mt-4 flex flex-wrap gap-2">
                  <span className="text-sm font-medium text-gray-700">Topics:</span>
                  {question.issue_tags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              <div className="mt-4 flex items-center text-sm text-gray-500 space-x-4">
                <span className="flex items-center">
                  <svg className="h-5 w-5 mr-1 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 10.5a1.5 1.5 0 113 0v6a1.5 1.5 0 01-3 0v-6zM6 10.333v5.43a2 2 0 001.106 1.79l.05.025A4 4 0 008.943 18h5.416a2 2 0 001.962-1.608l1.2-6A2 2 0 0015.56 8H12V4a2 2 0 00-2-2 1 1 0 00-1 1v.667a4 4 0 01-.8 2.4L6.8 7.933a4 4 0 00-.8 2.4z" />
                  </svg>
                  {question.upvotes} upvotes
                </span>
                <span>
                  Rank Score: {question.rank_score.toFixed(1)}
                </span>
                <span>
                  Asked {new Date(question.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>

          {/* Engagement Indicator */}
          <div className="mt-6 p-4 bg-blue-50 rounded-lg">
            <div className="flex items-start">
              <svg className="h-5 w-5 text-blue-600 mt-0.5 mr-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <p className="text-sm font-medium text-blue-900">
                  This is a high-priority question from voters in your community
                </p>
                <p className="text-sm text-blue-700 mt-1">
                  Your thoughtful response will help voters understand your position on this important issue.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Video Recorder */}
        <VideoAnswerRecorder
          questionId={question.id}
          questionText={question.question_text}
          candidateId={candidateId}
          onSuccess={handleSuccess}
          onCancel={handleCancel}
        />

        {/* Tips */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Tips for a Great Answer</h3>
          <ul className="space-y-3 text-sm text-gray-600">
            <li className="flex items-start">
              <svg className="h-5 w-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span><strong>Be direct:</strong> Answer the question clearly and concisely</span>
            </li>
            <li className="flex items-start">
              <svg className="h-5 w-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span><strong>Be specific:</strong> Provide concrete examples or plans when possible</span>
            </li>
            <li className="flex items-start">
              <svg className="h-5 w-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span><strong>Be authentic:</strong> Speak naturally and honestly in your own voice</span>
            </li>
            <li className="flex items-start">
              <svg className="h-5 w-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span><strong>Be respectful:</strong> Address opposing views constructively</span>
            </li>
            <li className="flex items-start">
              <svg className="h-5 w-5 text-green-500 mr-2 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span><strong>Check your setup:</strong> Good lighting, clear audio, and minimal background noise</span>
            </li>
          </ul>
        </div>
      </div>
    </Layout>
  );
}
