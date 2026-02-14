import React from 'react';
import { Link } from 'react-router-dom';

const SimpleHomePage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-blue-600">CivicQ</h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h2 className="text-5xl font-bold text-gray-900 mb-6">
            Civic Engagement for Local Elections
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
            Turning campaigning into a standardized, verifiable public record of candidates
            answering the public's top questions, city by city, with integrity by design.
          </p>
          <div className="flex gap-4 justify-center">
            <Link
              to="/ballot"
              className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition"
            >
              View Your Ballot
            </Link>
            <button className="bg-gray-200 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:bg-gray-300 transition">
              Learn More
            </button>
          </div>
        </div>

        {/* AI-Powered Section */}
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 mb-16 border border-blue-100">
          <div className="flex items-center justify-center mb-6">
            <div className="bg-blue-600 text-white px-4 py-2 rounded-full text-sm font-semibold flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
              </svg>
              <span>AI-POWERED BY CLAUDE</span>
            </div>
          </div>
          <h3 className="text-3xl font-bold text-center mb-4 text-gray-900">
            Intelligent Question Assistance
          </h3>
          <p className="text-center text-gray-700 text-lg mb-8 max-w-3xl mx-auto">
            CivicQ uses advanced AI to help you ask better questions and make your voice heard more effectively
          </p>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h4 className="font-semibold text-lg mb-2">Smart Quality Analysis</h4>
              <p className="text-gray-600 text-sm">
                Get instant feedback on your question's clarity, relevance, and quality score before submitting
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
              </div>
              <h4 className="font-semibold text-lg mb-2">Duplicate Detection</h4>
              <p className="text-gray-600 text-sm">
                AI checks if similar questions already exist, helping focus community attention on unique issues
              </p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h4 className="font-semibold text-lg mb-2">Question Suggestions</h4>
              <p className="text-gray-600 text-sm">
                Get AI-generated question ideas tailored to each specific race or ballot measure
              </p>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="text-4xl mb-4">🗳️</div>
            <h3 className="text-xl font-semibold mb-2">Your Ballot</h3>
            <p className="text-gray-600">
              View all contests and measures for your local election in one place
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="text-4xl mb-4">❓</div>
            <h3 className="text-xl font-semibold mb-2">Ask Questions</h3>
            <p className="text-gray-600">
              Submit and vote on questions you want candidates to answer
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-sm">
            <div className="text-4xl mb-4">📹</div>
            <h3 className="text-xl font-semibold mb-2">Watch Answers</h3>
            <p className="text-gray-600">
              See candidates respond to your questions in structured video format
            </p>
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-lg shadow-sm p-8">
          <h3 className="text-2xl font-bold mb-6 text-center">How CivicQ Works</h3>
          <div className="grid md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-3">
                1
              </div>
              <p className="text-gray-700">Enter your address to see your ballot</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-3">
                2
              </div>
              <p className="text-gray-700">Submit questions for candidates</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-3">
                3
              </div>
              <p className="text-gray-700">Vote on important questions</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xl font-bold mx-auto mb-3">
                4
              </div>
              <p className="text-gray-700">Watch candidate video answers</p>
            </div>
          </div>
        </div>

        {/* Core Principles */}
        <div className="mt-16 text-center">
          <h3 className="text-2xl font-bold mb-8">Built on Core Principles</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-blue-50 p-6 rounded-lg">
              <h4 className="font-semibold text-lg mb-2">No Pay-to-Win</h4>
              <p className="text-gray-600 text-sm">No ads, no boosting, no sponsored content</p>
            </div>
            <div className="bg-blue-50 p-6 rounded-lg">
              <h4 className="font-semibold text-lg mb-2">Everything On Record</h4>
              <p className="text-gray-600 text-sm">Questions versioned, answers permanent</p>
            </div>
            <div className="bg-blue-50 p-6 rounded-lg">
              <h4 className="font-semibold text-lg mb-2">Anti-Polarization</h4>
              <p className="text-gray-600 text-sm">Designed to reduce faction warfare</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 text-center text-gray-600">
          <p>Built to make local democracy more transparent, accessible, and focused on what voters actually care about.</p>
        </div>
      </footer>
    </div>
  );
};

export default SimpleHomePage;
