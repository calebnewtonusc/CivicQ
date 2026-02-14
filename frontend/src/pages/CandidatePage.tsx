import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useCandidate, useCandidateVideoAnswers } from '../hooks/useCandidates';
import { useAuthContext } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import VideoPlayer from '../components/VideoPlayer';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { VideoAnswer } from '../types';

const CandidatePage: React.FC = () => {
  const { candidateId } = useParams<{ candidateId: string }>();
  const { user } = useAuthContext();
  const [selectedAnswer, setSelectedAnswer] = useState<VideoAnswer | null>(null);

  const candidateIdNum = candidateId ? parseInt(candidateId) : undefined;

  const {
    data: candidate,
    isLoading: candidateLoading,
    error: candidateError,
  } = useCandidate(candidateIdNum);

  const {
    data: videoAnswers,
    isLoading: answersLoading,
  } = useCandidateVideoAnswers(candidateIdNum);

  if (candidateLoading) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <LoadingSpinner size="lg" message="Loading candidate profile..." />
        </div>
      </Layout>
    );
  }

  if (candidateError || !candidate) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <ErrorMessage message="Failed to load candidate profile. Please try again." />
        </div>
      </Layout>
    );
  }

  const isCandidateUser = user?.id === candidate.user_id;
  const publishedAnswers = videoAnswers?.filter((a) => a.status === 'published') || [];
  const draftAnswers = videoAnswers?.filter((a) => a.status === 'draft') || [];

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Candidate Header */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-start space-x-6">
            {/* Photo */}
            <div className="flex-shrink-0">
              {candidate.photo_url ? (
                <img
                  src={candidate.photo_url}
                  alt={candidate.name}
                  className="w-32 h-32 rounded-full object-cover border-4 border-gray-200"
                />
              ) : (
                <div className="w-32 h-32 rounded-full bg-gray-200 flex items-center justify-center text-gray-500 text-5xl font-bold border-4 border-gray-300">
                  {candidate.name.charAt(0)}
                </div>
              )}
            </div>

            {/* Info */}
            <div className="flex-1">
              <div className="flex items-start justify-between">
                <div>
                  <h1 className="text-4xl font-bold text-gray-900 mb-2">{candidate.name}</h1>

                  {/* Status Badges */}
                  <div className="flex items-center space-x-2 mb-4">
                    <span
                      className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                        candidate.status === 'active'
                          ? 'bg-green-100 text-green-800'
                          : candidate.status === 'verified'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {candidate.status}
                    </span>
                    {candidate.identity_verified && (
                      <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-civic-blue text-white">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        Verified Identity
                      </span>
                    )}
                  </div>

                  {/* Profile Fields */}
                  {candidate.profile_fields && (
                    <div className="space-y-2 text-gray-700">
                      {Object.entries(candidate.profile_fields).map(([key, value]) => (
                        <div key={key}>
                          <span className="font-medium capitalize">{key.replace(/_/g, ' ')}:</span>{' '}
                          {String(value)}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Website */}
                  {candidate.website && (
                    <a
                      href={candidate.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-3 inline-flex items-center text-civic-blue hover:underline"
                    >
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                      </svg>
                      Campaign Website
                    </a>
                  )}
                </div>

                {isCandidateUser && (
                  <div className="ml-4">
                    <Link
                      to={`/candidate/${candidate.id}/edit`}
                      className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                    >
                      Edit Profile
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Candidate Portal (for logged-in candidate) */}
        {isCandidateUser && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Candidate Portal</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <PortalStat label="Published Answers" value={publishedAnswers.length} />
              <PortalStat label="Draft Answers" value={draftAnswers.length} />
              <PortalStat label="Profile Status" value={candidate.status} />
            </div>
            <div className="flex space-x-3">
              <Link
                to={`/candidate/${candidate.id}/questions`}
                className="px-4 py-2 bg-civic-blue text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                View Questions to Answer
              </Link>
              <Link
                to={`/candidate/${candidate.id}/record`}
                className="px-4 py-2 bg-civic-green text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Record New Answer
              </Link>
            </div>
          </div>
        )}

        {/* Video Answers */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Answer List */}
          <div className="lg:col-span-1 space-y-4">
            <h2 className="text-xl font-bold text-gray-900">
              Video Answers ({publishedAnswers.length})
            </h2>

            {answersLoading && <LoadingSpinner message="Loading answers..." />}

            {publishedAnswers.length > 0 ? (
              <div className="space-y-3">
                {publishedAnswers.map((answer) => (
                  <button
                    key={answer.id}
                    onClick={() => setSelectedAnswer(answer)}
                    className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                      selectedAnswer?.id === answer.id
                        ? 'border-civic-blue bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300 bg-white'
                    }`}
                  >
                    <p className="font-medium text-gray-900 line-clamp-2 mb-1">
                      {answer.question?.question_text || 'Unknown Question'}
                    </p>
                    <p className="text-xs text-gray-500">
                      {Math.floor(answer.duration / 60)}:{(answer.duration % 60).toFixed(0).padStart(2, '0')}
                    </p>
                  </button>
                ))}
              </div>
            ) : (
              <div className="bg-gray-50 rounded-lg p-6 text-center text-gray-600 text-sm">
                {isCandidateUser
                  ? 'You haven\'t recorded any answers yet. Start by recording your first answer!'
                  : 'This candidate hasn\'t recorded any answers yet.'}
              </div>
            )}

            {/* Draft Answers (only for candidate) */}
            {isCandidateUser && draftAnswers.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-3">
                  Drafts ({draftAnswers.length})
                </h3>
                <div className="space-y-2">
                  {draftAnswers.map((answer) => (
                    <div
                      key={answer.id}
                      className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-sm"
                    >
                      <p className="font-medium text-gray-900 line-clamp-2">
                        {answer.question?.question_text || 'Unknown Question'}
                      </p>
                      <p className="text-xs text-yellow-800 mt-1">Draft - Not Published</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Video Player */}
          <div className="lg:col-span-3">
            {selectedAnswer ? (
              <div>
                <div className="mb-4">
                  <Link
                    to={`/question/${selectedAnswer.question_id}`}
                    className="inline-flex items-center text-lg font-semibold text-gray-900 hover:text-civic-blue"
                  >
                    View Question Details
                    <svg className="w-5 h-5 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </Link>
                  <h2 className="text-2xl font-bold text-gray-900 mt-2">
                    {selectedAnswer.question?.question_text}
                  </h2>
                </div>
                <VideoPlayer answer={selectedAnswer} />
              </div>
            ) : (
              <div className="bg-gray-50 rounded-lg p-12 text-center">
                <svg
                  className="mx-auto h-16 w-16 text-gray-400 mb-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
                  />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Select an answer to watch
                </h3>
                <p className="text-gray-600">
                  Choose from the list on the left to see the video response
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Additional Info */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Contact (if available) */}
          {(candidate.email || candidate.phone) && !isCandidateUser && (
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h3>
              {candidate.email && (
                <a
                  href={`mailto:${candidate.email}`}
                  className="block text-civic-blue hover:underline mb-2"
                >
                  {candidate.email}
                </a>
              )}
              {candidate.phone && (
                <a
                  href={`tel:${candidate.phone}`}
                  className="block text-civic-blue hover:underline"
                >
                  {candidate.phone}
                </a>
              )}
            </div>
          )}

          {/* Stats */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Activity</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Published Answers</span>
                <span className="font-semibold text-gray-900">{publishedAnswers.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Total Video Time</span>
                <span className="font-semibold text-gray-900">
                  {Math.floor(
                    publishedAnswers.reduce((sum, a) => sum + a.duration, 0) / 60
                  )}{' '}
                  min
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

// Helper Component
const PortalStat: React.FC<{ label: string; value: string | number }> = ({ label, value }) => (
  <div className="bg-white rounded-lg p-4">
    <p className="text-sm text-gray-600 mb-1">{label}</p>
    <p className="text-2xl font-bold text-gray-900">{value}</p>
  </div>
);

export default CandidatePage;
