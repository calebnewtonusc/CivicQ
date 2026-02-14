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
