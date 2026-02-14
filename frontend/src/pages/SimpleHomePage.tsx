import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const SimpleHomePage: React.FC = () => {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50/30">
      {/* Header - Sticky with smooth transition */}
      <header
        className={`sticky top-0 z-50 bg-white/95 backdrop-blur-sm transition-all duration-300 ${
          scrolled ? 'shadow-md' : 'shadow-sm'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              CivicQ
            </h1>
            <nav className="flex items-center gap-4">
              <Link
                to="/ballot"
                className="text-gray-700 hover:text-blue-600 transition-colors font-medium"
              >
                Your Ballot
              </Link>
              <Link
                to="/login"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-all hover:shadow-lg"
              >
                Get Started
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section - Enhanced with animations */}
        <div className="text-center mb-20 animate-fadeIn">
          <div className="mb-6 inline-block px-4 py-2 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold">
            Making Democracy More Accessible
          </div>
          <h2 className="text-6xl font-extrabold text-gray-900 mb-6 leading-tight">
            Civic Engagement for
            <br />
            <span className="bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
              Local Elections
            </span>
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-10 leading-relaxed">
            Turning campaigning into a standardized, verifiable public record of candidates
            answering the public's top questions, city by city, with integrity by design.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <Link
              to="/ballot"
              className="group bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-4 rounded-xl font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl hover:scale-105 transform flex items-center gap-2"
            >
              View Your Ballot
              <svg
                className="w-5 h-5 group-hover:translate-x-1 transition-transform"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M13 7l5 5m0 0l-5 5m5-5H6"
                />
              </svg>
            </Link>
            <button
              onClick={() =>
                document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })
              }
              className="bg-white text-gray-700 px-8 py-4 rounded-xl font-semibold hover:bg-gray-50 transition-all border-2 border-gray-200 hover:border-gray-300 hover:shadow-md"
            >
              Learn More
            </button>
          </div>
        </div>

        {/* AI-Powered Section - Enhanced with gradient and animations */}
        <div className="relative bg-gradient-to-br from-blue-600 to-indigo-700 rounded-3xl p-10 mb-20 overflow-hidden shadow-2xl">
          {/* Background Pattern */}
          <div className="absolute inset-0 opacity-10">
            <div className="absolute inset-0" style={{
              backgroundImage: 'radial-gradient(circle at 2px 2px, white 1px, transparent 0)',
              backgroundSize: '40px 40px'
            }}></div>
          </div>

          <div className="relative z-10">
            <div className="flex items-center justify-center mb-6">
              <div className="bg-white/20 backdrop-blur-sm text-white px-5 py-2 rounded-full text-sm font-bold flex items-center gap-2 border border-white/30">
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M11 3a1 1 0 10-2 0v1a1 1 0 102 0V3zM15.657 5.757a1 1 0 00-1.414-1.414l-.707.707a1 1 0 001.414 1.414l.707-.707zM18 10a1 1 0 01-1 1h-1a1 1 0 110-2h1a1 1 0 011 1zM5.05 6.464A1 1 0 106.464 5.05l-.707-.707a1 1 0 00-1.414 1.414l.707.707zM5 10a1 1 0 01-1 1H3a1 1 0 110-2h1a1 1 0 011 1zM8 16v-1h4v1a2 2 0 11-4 0zM12 14c.015-.34.208-.646.477-.859a4 4 0 10-4.954 0c.27.213.462.519.476.859h4.002z" />
                </svg>
                <span>AI-POWERED BY CLAUDE</span>
              </div>
            </div>
            <h3 className="text-4xl font-bold text-center mb-4 text-white">
              Intelligent Question Assistance
            </h3>
            <p className="text-center text-blue-100 text-lg mb-10 max-w-3xl mx-auto">
              CivicQ uses advanced AI to help you ask better questions and make your voice heard more effectively
            </p>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="group bg-white/95 backdrop-blur-sm p-7 rounded-2xl shadow-lg hover:shadow-2xl transition-all hover:-translate-y-1 border border-white/50">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h4 className="font-bold text-xl mb-3 text-gray-900">Smart Quality Analysis</h4>
                <p className="text-gray-600">
                  Get instant feedback on your question's clarity, relevance, and quality score before submitting
                </p>
              </div>
              <div className="group bg-white/95 backdrop-blur-sm p-7 rounded-2xl shadow-lg hover:shadow-2xl transition-all hover:-translate-y-1 border border-white/50">
                <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                </div>
                <h4 className="font-bold text-xl mb-3 text-gray-900">Duplicate Detection</h4>
                <p className="text-gray-600">
                  AI checks if similar questions already exist, helping focus community attention on unique issues
                </p>
              </div>
              <div className="group bg-white/95 backdrop-blur-sm p-7 rounded-2xl shadow-lg hover:shadow-2xl transition-all hover:-translate-y-1 border border-white/50">
                <div className="w-14 h-14 bg-gradient-to-br from-green-500 to-green-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform shadow-lg">
                  <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <h4 className="font-bold text-xl mb-3 text-gray-900">Question Suggestions</h4>
                <p className="text-gray-600">
                  Get AI-generated question ideas tailored to each specific race or ballot measure
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Features Grid - Enhanced with hover effects */}
        <div className="grid md:grid-cols-3 gap-8 mb-20">
          <div className="group bg-white p-8 rounded-2xl shadow-md hover:shadow-2xl transition-all hover:-translate-y-2 border border-gray-100 cursor-pointer">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-100 to-blue-200 rounded-2xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform text-3xl">
              <svg className="w-10 h-10 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold mb-3 text-gray-900">Your Ballot</h3>
            <p className="text-gray-600 leading-relaxed">
              View all contests and measures for your local election in one place
            </p>
          </div>
          <div className="group bg-white p-8 rounded-2xl shadow-md hover:shadow-2xl transition-all hover:-translate-y-2 border border-gray-100 cursor-pointer">
            <div className="w-16 h-16 bg-gradient-to-br from-purple-100 to-purple-200 rounded-2xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform text-3xl">
              <svg className="w-10 h-10 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold mb-3 text-gray-900">Ask Questions</h3>
            <p className="text-gray-600 leading-relaxed">
              Submit and vote on questions you want candidates to answer
            </p>
          </div>
          <div className="group bg-white p-8 rounded-2xl shadow-md hover:shadow-2xl transition-all hover:-translate-y-2 border border-gray-100 cursor-pointer">
            <div className="w-16 h-16 bg-gradient-to-br from-green-100 to-green-200 rounded-2xl flex items-center justify-center mb-5 group-hover:scale-110 transition-transform text-3xl">
              <svg className="w-10 h-10 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold mb-3 text-gray-900">Watch Answers</h3>
            <p className="text-gray-600 leading-relaxed">
              See candidates respond to your questions in structured video format
            </p>
          </div>
        </div>

        {/* How It Works - Scroll anchor */}
        <div id="how-it-works" className="bg-white rounded-3xl shadow-xl p-10 border border-gray-100">
          <h3 className="text-3xl font-bold mb-10 text-center text-gray-900">How CivicQ Works</h3>
          <div className="grid md:grid-cols-4 gap-8">
            <div className="text-center group">
              <div className="relative mb-5">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold mx-auto shadow-lg group-hover:scale-110 transition-transform">
                  1
                </div>
                {/* Connecting Line - hidden on last item */}
                <div className="hidden md:block absolute top-8 left-[calc(50%+2rem)] w-[calc(100%+2rem)] h-1 bg-gradient-to-r from-blue-200 to-transparent"></div>
              </div>
              <p className="text-gray-700 font-medium">Enter your address to see your ballot</p>
            </div>
            <div className="text-center group">
              <div className="relative mb-5">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold mx-auto shadow-lg group-hover:scale-110 transition-transform">
                  2
                </div>
                <div className="hidden md:block absolute top-8 left-[calc(50%+2rem)] w-[calc(100%+2rem)] h-1 bg-gradient-to-r from-blue-200 to-transparent"></div>
              </div>
              <p className="text-gray-700 font-medium">Submit questions for candidates</p>
            </div>
            <div className="text-center group">
              <div className="relative mb-5">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold mx-auto shadow-lg group-hover:scale-110 transition-transform">
                  3
                </div>
                <div className="hidden md:block absolute top-8 left-[calc(50%+2rem)] w-[calc(100%+2rem)] h-1 bg-gradient-to-r from-blue-200 to-transparent"></div>
              </div>
              <p className="text-gray-700 font-medium">Vote on important questions</p>
            </div>
            <div className="text-center group">
              <div className="relative mb-5">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold mx-auto shadow-lg group-hover:scale-110 transition-transform">
                  4
                </div>
              </div>
              <p className="text-gray-700 font-medium">Watch candidate video answers</p>
            </div>
          </div>
        </div>

        {/* Core Principles */}
        <div className="mt-20 text-center">
          <h3 className="text-3xl font-bold mb-10 text-gray-900">Built on Core Principles</h3>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="group bg-gradient-to-br from-blue-50 to-indigo-50 p-8 rounded-2xl border-2 border-blue-100 hover:border-blue-300 transition-all hover:shadow-lg">
              <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h4 className="font-bold text-xl mb-3 text-gray-900">No Pay-to-Win</h4>
              <p className="text-gray-600">No ads, no boosting, no sponsored content</p>
            </div>
            <div className="group bg-gradient-to-br from-blue-50 to-indigo-50 p-8 rounded-2xl border-2 border-blue-100 hover:border-blue-300 transition-all hover:shadow-lg">
              <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h4 className="font-bold text-xl mb-3 text-gray-900">Everything On Record</h4>
              <p className="text-gray-600">Questions versioned, answers permanent</p>
            </div>
            <div className="group bg-gradient-to-br from-blue-50 to-indigo-50 p-8 rounded-2xl border-2 border-blue-100 hover:border-blue-300 transition-all hover:shadow-lg">
              <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h4 className="font-bold text-xl mb-3 text-gray-900">Anti-Polarization</h4>
              <p className="text-gray-600">Designed to reduce faction warfare</p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-3">
              CivicQ
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Built to make local democracy more transparent, accessible, and focused on what voters actually care about.
            </p>
          </div>
          <div className="flex justify-center gap-8 text-sm text-gray-500">
            <Link to="/about" className="hover:text-blue-600 transition-colors">
              About
            </Link>
            <Link to="/privacy" className="hover:text-blue-600 transition-colors">
              Privacy
            </Link>
            <Link to="/terms" className="hover:text-blue-600 transition-colors">
              Terms
            </Link>
            <Link to="/contact" className="hover:text-blue-600 transition-colors">
              Contact
            </Link>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default SimpleHomePage;
