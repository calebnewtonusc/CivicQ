import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import {
  CheckCircleIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  GlobeAltIcon,
  SparklesIcon,
  HeartIcon
} from '@heroicons/react/24/outline';

export default function AboutPage() {
  const values = [
    {
      icon: CheckCircleIcon,
      title: 'Transparency',
      description: 'Every answer is recorded, verified, and permanently accessible. No more dodging questions or broken promises.'
    },
    {
      icon: UserGroupIcon,
      title: 'Community-Driven',
      description: 'Voters ask the questions that matter to them. No corporate sponsors, no hidden agendas.'
    },
    {
      icon: ShieldCheckIcon,
      title: 'Non-Partisan',
      description: 'We serve voters across the political spectrum. Our platform treats all candidates and viewpoints equally.'
    },
    {
      icon: GlobeAltIcon,
      title: 'Accessible',
      description: 'Free for all voters and candidates. Built with accessibility in mind to serve everyone in our democracy.'
    }
  ];

  const team = [
    {
      name: 'Our Mission',
      role: 'Why We Exist',
      description: 'To empower voters with the information they need to make informed decisions and hold elected officials accountable.',
      icon: SparklesIcon
    },
    {
      name: 'Our Vision',
      role: 'Where We\'re Going',
      description: 'A democracy where every voter has direct access to candidate positions on the issues that matter most to their community.',
      icon: HeartIcon
    }
  ];

  return (
    <>
      <Helmet>
        <title>About Us - CivicQ</title>
        <meta
          name="description"
          content="Learn about CivicQ's mission to empower voters with direct access to candidate positions through video Q&A. Non-partisan, transparent, and community-driven."
        />
        <meta property="og:title" content="About CivicQ - Empowering Informed Voting" />
        <meta
          property="og:description"
          content="Discover how CivicQ connects voters directly with candidates through video Q&A, making elections more transparent and accessible."
        />
        <meta property="og:type" content="website" />
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        <Navbar />

        <main className="pt-16">
          {/* Hero Section */}
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 text-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
              <div className="text-center">
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
                  Democracy Deserves Better
                </h1>
                <p className="text-xl md:text-2xl text-blue-100 max-w-3xl mx-auto mb-8">
                  We're building a platform that connects voters directly with candidates through video Q&A,
                  making elections more transparent, accessible, and accountable.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link
                    to="/ballot"
                    className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50 transition-colors"
                  >
                    See Your Ballot
                  </Link>
                  <Link
                    to="/how-it-works"
                    className="inline-flex items-center justify-center px-8 py-3 border-2 border-white text-base font-medium rounded-md text-white hover:bg-white hover:text-blue-700 transition-colors"
                  >
                    How It Works
                  </Link>
                </div>
              </div>
            </div>
          </div>

          {/* The Problem Section */}
          <div className="bg-white py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="max-w-3xl mx-auto">
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-6 text-center">
                  The Problem We're Solving
                </h2>
                <div className="prose prose-lg text-gray-600 max-w-none">
                  <p className="mb-4">
                    Every election cycle, voters face the same frustration: candidates make promises on the campaign
                    trail, but it's nearly impossible to find clear, direct answers to the questions that matter most
                    to your community.
                  </p>
                  <p className="mb-4">
                    Traditional town halls reach only a handful of voters. Debate questions are chosen by media, not
                    communities. Campaign websites are filled with vague platitudes. And once elected, promises are
                    easily forgotten.
                  </p>
                  <p>
                    <strong className="text-gray-900">We built CivicQ to change that.</strong>
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Our Solution Section */}
          <div className="bg-gray-50 py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-12">
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                  How CivicQ Works
                </h2>
                <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                  A simple platform that puts voters in control
                </p>
              </div>

              <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
                <div className="bg-white rounded-lg shadow-sm p-6 text-center">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-blue-600">1</span>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Voters Ask</h3>
                  <p className="text-gray-600">
                    Community members submit questions about local issues, policies, and priorities
                  </p>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6 text-center">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-blue-600">2</span>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Candidates Answer</h3>
                  <p className="text-gray-600">
                    Candidates record video responses, going on the record with their positions
                  </p>
                </div>

                <div className="bg-white rounded-lg shadow-sm p-6 text-center">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <span className="text-2xl font-bold text-blue-600">3</span>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">Community Decides</h3>
                  <p className="text-gray-600">
                    Voters compare answers side-by-side and make informed decisions at the polls
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Values Section */}
          <div className="bg-white py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-12">
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                  Our Values
                </h2>
                <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                  The principles that guide everything we do
                </p>
              </div>

              <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                {values.map((value) => (
                  <div key={value.title} className="flex gap-4">
                    <div className="flex-shrink-0">
                      <value.icon className="h-8 w-8 text-blue-600" aria-hidden="true" />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2">{value.title}</h3>
                      <p className="text-gray-600">{value.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Mission & Vision Section */}
          <div className="bg-gradient-to-br from-indigo-50 to-blue-50 py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
                {team.map((item) => (
                  <div key={item.name} className="bg-white rounded-lg shadow-sm p-8">
                    <item.icon className="h-12 w-12 text-blue-600 mb-4" aria-hidden="true" />
                    <h3 className="text-2xl font-bold text-gray-900 mb-2">{item.name}</h3>
                    <p className="text-sm font-medium text-blue-600 mb-4">{item.role}</p>
                    <p className="text-gray-600 text-lg">{item.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Impact Section */}
          <div className="bg-white py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-12">
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                  Our Impact
                </h2>
                <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                  Building a more informed democracy, one community at a time
                </p>
              </div>

              <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto text-center">
                <div>
                  <div className="text-4xl md:text-5xl font-bold text-blue-600 mb-2">100%</div>
                  <div className="text-gray-600">Free for Voters</div>
                </div>
                <div>
                  <div className="text-4xl md:text-5xl font-bold text-blue-600 mb-2">Every</div>
                  <div className="text-gray-600">Voice Heard</div>
                </div>
                <div>
                  <div className="text-4xl md:text-5xl font-bold text-blue-600 mb-2">Zero</div>
                  <div className="text-gray-600">Partisan Bias</div>
                </div>
              </div>
            </div>
          </div>

          {/* CTA Section */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                Join Us in Building Better Democracy
              </h2>
              <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
                Whether you're a voter, candidate, or community leader, you have a role to play
                in making our democracy more transparent and accountable.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/ballot"
                  className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50 transition-colors"
                >
                  Find Your Ballot
                </Link>
                <Link
                  to="/contact"
                  className="inline-flex items-center justify-center px-8 py-3 border-2 border-white text-base font-medium rounded-md text-white hover:bg-white hover:text-blue-700 transition-colors"
                >
                  Contact Us
                </Link>
              </div>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
}
