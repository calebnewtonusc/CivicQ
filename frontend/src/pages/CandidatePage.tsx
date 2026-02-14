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
        <div className="container mx-auto px-4 py-8 min-h-screen flex items-center justify-center">
          <div className="text-center animate-fadeIn">
            <div className="w-20 h-20 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin mx-auto mb-4"></div>
            <LoadingSpinner size="lg" message="Loading candidate profile..." />
          </div>
        </div>
      </Layout>
    );
  }

  if (candidateError || !candidate) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8 min-h-screen flex items-center justify-center">
          <div className="max-w-md w-full animate-scaleIn">
            <div className="bg-red-50 border-2 border-red-200 rounded-2xl p-8 text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Unable to Load Profile</h3>
              <ErrorMessage message="Failed to load candidate profile. Please try again." />
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  const isCandidateUser = user?.id === candidate.user_id;
  const publishedAnswers = videoAnswers?.filter((a) => a.status === 'published') || [];
  const draftAnswers = videoAnswers?.filter((a) => a.status === 'draft') || [];

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8 animate-fadeIn">
        {/* Candidate Header - YouTube channel style */}
        <div className="relative bg-gradient-to-br from-white to-blue-50/50 rounded-2xl shadow-xl border border-gray-200 overflow-hidden mb-8">
          {/* Background Banner */}
          <div className="h-32 bg-gradient-to-r from-blue-600 to-indigo-600"></div>

          <div className="px-8 pb-8">
            <div className="flex items-end gap-6 -mt-16">
              {/* Photo - Overlapping the banner */}
              <div className="flex-shrink-0">
                {candidate.photo_url ? (
                  <img
                    src={candidate.photo_url}
                    alt={candidate.name}
                    className="w-40 h-40 rounded-full object-cover border-4 border-white shadow-2xl"
                  />
                ) : (
                  <div className="w-40 h-40 rounded-full bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center text-gray-600 text-6xl font-bold border-4 border-white shadow-2xl">
                    {candidate.name.charAt(0)}
                  </div>
                )}
              </div>

              {/* Info */}
              <div className="flex-1 pb-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h1 className="text-4xl font-extrabold text-gray-900 mb-3">{candidate.name}</h1>

                    {/* Status Badges */}
                    <div className="flex items-center flex-wrap gap-2 mb-4">
                      <span
                        className={`inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-bold shadow-sm ${
                          candidate.status === 'active'
                            ? 'bg-green-100 text-green-800 border border-green-200'
                            : candidate.status === 'verified'
                            ? 'bg-blue-100 text-blue-800 border border-blue-200'
                            : 'bg-gray-100 text-gray-800 border border-gray-200'
                        }`}
                      >
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        {candidate.status}
                      </span>
                      {candidate.identity_verified && (
                        <span className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-full text-sm font-bold bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-md">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                          Verified Identity
                        </span>
                      )}
                    </div>

                    {/* Profile Fields */}
                    {candidate.profile_fields && (
                      <div className="flex flex-wrap gap-4">
                        {Object.entries(candidate.profile_fields).map(([key, value]) => (
                          <div key={key} className="flex items-center gap-2 text-gray-700">
                            <svg className="w-4 h-4 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                            <span className="font-semibold capitalize">{key.replace(/_/g, ' ')}:</span>
                            <span>{String(value)}</span>
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
                        className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all shadow-md hover:shadow-lg font-semibold"
                      >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
                        className="px-6 py-3 bg-white text-gray-700 rounded-xl hover:bg-gray-50 transition-all border-2 border-gray-200 hover:border-gray-300 font-semibold shadow-md"
                      >
                        Edit Profile
                      </Link>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Candidate Portal (for logged-in candidate) - Enhanced */}
        {isCandidateUser && (
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-2xl p-8 mb-8 shadow-xl text-white">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center">
                <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4M7.835 4.697a3.42 3.42 0 001.946-.806 3.42 3.42 0 014.438 0 3.42 3.42 0 001.946.806 3.42 3.42 0 013.138 3.138 3.42 3.42 0 00.806 1.946 3.42 3.42 0 010 4.438 3.42 3.42 0 00-.806 1.946 3.42 3.42 0 01-3.138 3.138 3.42 3.42 0 00-1.946.806 3.42 3.42 0 01-4.438 0 3.42 3.42 0 00-1.946-.806 3.42 3.42 0 01-3.138-3.138 3.42 3.42 0 00-.806-1.946 3.42 3.42 0 010-4.438 3.42 3.42 0 00.806-1.946 3.42 3.42 0 013.138-3.138z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold">Candidate Portal</h2>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <PortalStat label="Published Answers" value={publishedAnswers.length} />
              <PortalStat label="Draft Answers" value={draftAnswers.length} />
              <PortalStat label="Profile Status" value={candidate.status} />
            </div>
            <div className="flex flex-wrap gap-3">
              <Link
                to={`/candidate/${candidate.id}/questions`}
                className="px-6 py-3 bg-white text-blue-600 rounded-xl hover:bg-blue-50 transition-all font-bold shadow-lg hover:shadow-xl flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                View Questions to Answer
              </Link>
              <Link
                to={`/candidate/${candidate.id}/record`}
                className="px-6 py-3 bg-green-600 text-white rounded-xl hover:bg-green-700 transition-all font-bold shadow-lg hover:shadow-xl flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Record New Answer
              </Link>
            </div>
          </div>
        )}

        {/* Video Answers - YouTube-style grid */}
        <div>
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center shadow-lg">
              <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-gray-900">
              Video Answers <span className="text-gray-500">({publishedAnswers.length})</span>
            </h2>
          </div>

          {answersLoading && (
            <div className="flex justify-center py-12">
              <LoadingSpinner message="Loading answers..." />
            </div>
          )}

          {publishedAnswers.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {publishedAnswers.map((answer, index) => (
                <button
                  key={answer.id}
                  onClick={() => setSelectedAnswer(answer)}
                  className={`group text-left rounded-2xl overflow-hidden transition-all animate-fadeIn ${
                    selectedAnswer?.id === answer.id
                      ? 'ring-4 ring-blue-500 shadow-2xl scale-105'
                      : 'bg-white border-2 border-gray-200 hover:border-blue-300 hover:shadow-xl hover:scale-105'
                  }`}
                  style={{ animationDelay: `${index * 0.05}s` }}
                >
                  {/* Video Thumbnail */}
                  <div className="relative aspect-video bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center overflow-hidden">
                    {answer.video_url ? (
                      <div className="absolute inset-0 bg-black/10 group-hover:bg-black/20 transition-colors flex items-center justify-center">
                        <div className="w-16 h-16 bg-black/60 backdrop-blur-sm rounded-full flex items-center justify-center group-hover:scale-110 transition-transform">
                          <svg className="w-8 h-8 text-white ml-1" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M6.3 2.841A1.5 1.5 0 004 4.11V15.89a1.5 1.5 0 002.3 1.269l9.344-5.89a1.5 1.5 0 000-2.538L6.3 2.84z" />
                          </svg>
                        </div>
                      </div>
                    ) : (
                      <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    )}
                    {/* Duration badge */}
                    <div className="absolute bottom-2 right-2 px-2 py-1 bg-black/80 backdrop-blur-sm text-white text-xs font-bold rounded">
                      {Math.floor(answer.duration / 60)}:{(answer.duration % 60).toFixed(0).padStart(2, '0')}
                    </div>
                  </div>

                  {/* Video Info */}
                  <div className="p-4">
                    <h3 className="font-semibold text-gray-900 line-clamp-2 mb-2 group-hover:text-blue-600 transition-colors">
                      {answer.question?.question_text || 'Unknown Question'}
                    </h3>
                    {selectedAnswer?.id === answer.id && (
                      <div className="flex items-center gap-2 text-blue-600 text-sm font-bold">
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        Now Playing
                      </div>
                    )}
                  </div>
                </button>
              ))}
            </div>
          ) : (
            !answersLoading && (
              <div className="bg-gradient-to-br from-gray-50 to-blue-50/30 rounded-2xl p-16 text-center border-2 border-dashed border-gray-300">
                <div className="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">No Video Answers Yet</h3>
                <p className="text-lg text-gray-600 mb-6">
                  {isCandidateUser
                    ? 'You haven\'t recorded any answers yet. Start by recording your first answer!'
                    : 'This candidate hasn\'t recorded any answers yet.'}
                </p>
                {isCandidateUser && (
                  <Link
                    to={`/candidate/${candidate.id}/record`}
                    className="inline-block px-6 py-3 bg-green-600 text-white rounded-xl font-semibold hover:bg-green-700 transition-all shadow-md hover:shadow-lg"
                  >
                    Record Your First Answer
                  </Link>
                )}
              </div>
            )
          )}

          {/* Draft Answers (only for candidate) */}
          {isCandidateUser && draftAnswers.length > 0 && (
            <div className="mt-10">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 bg-gradient-to-br from-yellow-500 to-yellow-600 rounded-xl flex items-center justify-center shadow-lg">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </div>
                <h3 className="text-2xl font-bold text-gray-900">
                  Draft Answers <span className="text-gray-500">({draftAnswers.length})</span>
                </h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {draftAnswers.map((answer) => (
                  <div
                    key={answer.id}
                    className="p-5 bg-gradient-to-br from-yellow-50 to-orange-50 border-2 border-yellow-200 rounded-xl hover:shadow-lg transition-all"
                  >
                    <div className="flex items-start gap-2 mb-2">
                      <svg className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      <p className="font-semibold text-gray-900 line-clamp-2 flex-1">
                        {answer.question?.question_text || 'Unknown Question'}
                      </p>
                    </div>
                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-200 text-yellow-900 rounded-lg text-xs font-bold">
                      Draft - Not Published
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Video Player Modal - appears when video is selected */}
        {selectedAnswer && (
          <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-fadeIn">
            <div className="bg-white rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-y-auto shadow-2xl animate-scaleIn">
              {/* Close Button */}
              <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between z-10">
                <Link
                  to={`/question/${selectedAnswer.question_id}`}
                  className="group inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 font-semibold"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  View Full Question
                </Link>
                <button
                  onClick={() => setSelectedAnswer(null)}
                  className="p-2 hover:bg-gray-100 rounded-xl transition-colors"
                >
                  <svg className="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* Video Content */}
              <div className="p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">
                  {selectedAnswer.question?.question_text}
                </h2>
                <VideoPlayer answer={selectedAnswer} />
              </div>
            </div>
          </div>
        )}

        {/* Additional Info - Enhanced cards */}
        <div className="mt-10 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Contact (if available) */}
          {(candidate.email || candidate.phone) && !isCandidateUser && (
            <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
              <div className="bg-gradient-to-r from-gray-50 to-blue-50 px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Contact Information
                </h3>
              </div>
              <div className="p-6 space-y-3">
                {candidate.email && (
                  <a
                    href={`mailto:${candidate.email}`}
                    className="flex items-center gap-3 p-3 bg-blue-50 hover:bg-blue-100 rounded-xl transition-colors group"
                  >
                    <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    <span className="text-blue-600 group-hover:underline font-medium">{candidate.email}</span>
                  </a>
                )}
                {candidate.phone && (
                  <a
                    href={`tel:${candidate.phone}`}
                    className="flex items-center gap-3 p-3 bg-green-50 hover:bg-green-100 rounded-xl transition-colors group"
                  >
                    <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                    </svg>
                    <span className="text-green-600 group-hover:underline font-medium">{candidate.phone}</span>
                  </a>
                )}
              </div>
            </div>
          )}

          {/* Stats */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-200 overflow-hidden">
            <div className="bg-gradient-to-r from-gray-50 to-blue-50 px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                Activity Stats
              </h3>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex justify-between items-center p-3 bg-purple-50 rounded-xl">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  <span className="text-gray-700 font-medium">Published Answers</span>
                </div>
                <span className="text-2xl font-bold text-purple-600">{publishedAnswers.length}</span>
              </div>
              <div className="flex justify-between items-center p-3 bg-blue-50 rounded-xl">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span className="text-gray-700 font-medium">Total Video Time</span>
                </div>
                <span className="text-2xl font-bold text-blue-600">
                  {Math.floor(
                    publishedAnswers.reduce((sum, a) => sum + a.duration, 0) / 60
                  )} min
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

// Helper Component - Enhanced with better styling
const PortalStat: React.FC<{ label: string; value: string | number }> = ({ label, value }) => (
  <div className="bg-white/95 backdrop-blur-sm rounded-xl p-5 border border-white/50 shadow-md">
    <p className="text-sm text-gray-600 mb-1 font-medium">{label}</p>
    <p className="text-3xl font-extrabold text-gray-900">{value}</p>
  </div>
);

export default CandidatePage;
