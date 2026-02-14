import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import {
  UserIcon,
  UserGroupIcon,
  BuildingOffice2Icon,
  QuestionMarkCircleIcon,
  VideoCameraIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
  ShieldCheckIcon,
  BellAlertIcon
} from '@heroicons/react/24/outline';

export default function HowItWorksPage() {
  const [activeTab, setActiveTab] = useState<'voters' | 'candidates' | 'cities'>('voters');

  const voterSteps = [
    {
      icon: MagnifyingGlassIcon,
      title: 'Find Your Ballot',
      description: 'Enter your address to see all candidates running for office in your area.',
      detail: 'Our system uses your location to pull accurate ballot information for your specific district, city, and state elections.'
    },
    {
      icon: QuestionMarkCircleIcon,
      title: 'Ask Questions',
      description: 'Submit questions about issues that matter to you and your community.',
      detail: 'Your questions are reviewed for appropriateness and clarity, then sent to all candidates in the race. Popular questions rise to the top.'
    },
    {
      icon: VideoCameraIcon,
      title: 'Watch Answers',
      description: 'See video responses from candidates side-by-side to compare their positions.',
      detail: 'Every answer is recorded and timestamped. Candidates can\'t edit or delete their responses, ensuring accountability.'
    },
    {
      icon: CheckCircleIcon,
      title: 'Make Informed Decisions',
      description: 'Vote with confidence knowing exactly where candidates stand on your issues.',
      detail: 'Access all candidate responses anytime, share them with friends and family, and track promises after the election.'
    }
  ];

  const candidateSteps = [
    {
      icon: UserIcon,
      title: 'Create Your Profile',
      description: 'Sign up with your official candidate information and verify your identity.',
      detail: 'We verify all candidates through official election records to ensure authenticity and prevent impersonation.'
    },
    {
      icon: BellAlertIcon,
      title: 'Receive Questions',
      description: 'Get notified when voters in your district submit questions.',
      detail: 'Questions are organized by topic and popularity. You can see which issues matter most to your constituents.'
    },
    {
      icon: VideoCameraIcon,
      title: 'Record Video Answers',
      description: 'Record clear, direct responses to voter questions using your camera.',
      detail: 'Our platform supports high-quality video recording with teleprompter features. You can review before publishing.'
    },
    {
      icon: UserGroupIcon,
      title: 'Connect with Voters',
      description: 'Build trust and transparency by going on the record with your positions.',
      detail: 'Your responses are permanently archived, allowing voters to compare your campaign promises with your voting record if elected.'
    }
  ];

  const citySteps = [
    {
      icon: BuildingOffice2Icon,
      title: 'Register Your City',
      description: 'Municipal officials can register their city to make CivicQ available to all voters.',
      detail: 'We verify your official role and work with you to customize the platform for your local elections.'
    },
    {
      icon: MagnifyingGlassIcon,
      title: 'Import Ballot Data',
      description: 'Upload candidate information and contest details for upcoming elections.',
      detail: 'We support multiple data formats and can help migrate existing voter information systems.'
    },
    {
      icon: ShieldCheckIcon,
      title: 'Moderate & Approve',
      description: 'Review submitted questions and manage candidate verification.',
      detail: 'City staff have tools to ensure questions are appropriate, verify candidate identities, and moderate content.'
    },
    {
      icon: CheckCircleIcon,
      title: 'Launch to Voters',
      description: 'Make CivicQ available to all registered voters in your jurisdiction.',
      detail: 'We provide marketing materials, voter education resources, and ongoing support throughout the election cycle.'
    }
  ];

  const faqs = [
    {
      question: 'Is CivicQ really free for voters?',
      answer: 'Yes, absolutely! CivicQ is 100% free for all voters. We believe access to candidate information is a fundamental right in a healthy democracy.'
    },
    {
      question: 'How do you verify candidates are real?',
      answer: 'We verify all candidates through official election records from your state or local election office. Candidates must provide proof of their candidacy status before being allowed to answer questions.'
    },
    {
      question: 'Can candidates edit or delete their answers?',
      answer: 'No. Once a video answer is published, it cannot be edited or deleted. This ensures accountability and creates a permanent record of campaign promises.'
    },
    {
      question: 'What if my city isn\'t on CivicQ yet?',
      answer: 'You can encourage your local election officials to register, or we can work directly with community organizations to bring CivicQ to your area. Contact us to get started!'
    },
    {
      question: 'How do you prevent spam or inappropriate questions?',
      answer: 'All submitted questions are reviewed by human moderators before being sent to candidates. We have clear community guidelines and remove any questions that violate them.'
    },
    {
      question: 'Is CivicQ partisan?',
      answer: 'No. CivicQ is strictly non-partisan. We serve voters across the political spectrum and treat all candidates equally, regardless of party affiliation.'
    },
    {
      question: 'What happens to the data after elections?',
      answer: 'All candidate responses remain permanently accessible as a public record. This allows voters to hold elected officials accountable to their campaign promises.'
    },
    {
      question: 'Can I share candidate videos?',
      answer: 'Yes! All candidate responses can be shared via social media, email, or direct links. We encourage voters to spread the word and help others make informed decisions.'
    }
  ];

  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  return (
    <>
      <Helmet>
        <title>How It Works - CivicQ</title>
        <meta
          name="description"
          content="Learn how CivicQ works for voters, candidates, and cities. Find your ballot, ask questions, watch video answers, and make informed voting decisions."
        />
        <meta property="og:title" content="How CivicQ Works - For Voters, Candidates & Cities" />
        <meta
          property="og:description"
          content="Discover how CivicQ connects voters with candidates through video Q&A, making elections more transparent and accessible."
        />
        <meta property="og:type" content="website" />
      </Helmet>

      <div className="min-h-screen bg-gray-50">
        <Navbar />

        <main className="pt-16">
          {/* Hero Section */}
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 text-white py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center">
                <h1 className="text-4xl md:text-5xl font-bold mb-4">
                  How CivicQ Works
                </h1>
                <p className="text-xl text-blue-100 max-w-2xl mx-auto">
                  Connecting voters, candidates, and communities through transparent video Q&A
                </p>
              </div>
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="bg-white border-b border-gray-200">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex space-x-8 overflow-x-auto">
                <button
                  onClick={() => setActiveTab('voters')}
                  className={`py-4 px-2 font-medium text-sm border-b-2 transition-colors whitespace-nowrap ${
                    activeTab === 'voters'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <UserIcon className="h-5 w-5 inline mr-2" />
                  For Voters
                </button>
                <button
                  onClick={() => setActiveTab('candidates')}
                  className={`py-4 px-2 font-medium text-sm border-b-2 transition-colors whitespace-nowrap ${
                    activeTab === 'candidates'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <UserGroupIcon className="h-5 w-5 inline mr-2" />
                  For Candidates
                </button>
                <button
                  onClick={() => setActiveTab('cities')}
                  className={`py-4 px-2 font-medium text-sm border-b-2 transition-colors whitespace-nowrap ${
                    activeTab === 'cities'
                      ? 'border-blue-600 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <BuildingOffice2Icon className="h-5 w-5 inline mr-2" />
                  For Cities
                </button>
              </div>
            </div>
          </div>

          {/* Tab Content */}
          <div className="py-16 bg-white">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              {activeTab === 'voters' && (
                <div>
                  <div className="text-center mb-12">
                    <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                      Make Informed Voting Decisions
                    </h2>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                      Get direct answers from candidates on the issues that matter most to you
                    </p>
                  </div>

                  <div className="grid gap-8 max-w-4xl mx-auto">
                    {voterSteps.map((step, index) => (
                      <div key={step.title} className="flex gap-6">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                            <step.icon className="h-6 w-6 text-blue-600" aria-hidden="true" />
                          </div>
                        </div>
                        <div className="flex-grow">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-sm font-semibold text-blue-600">
                              Step {index + 1}
                            </span>
                            <h3 className="text-2xl font-bold text-gray-900">{step.title}</h3>
                          </div>
                          <p className="text-gray-600 text-lg mb-2">{step.description}</p>
                          <p className="text-gray-500">{step.detail}</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="text-center mt-12">
                    <Link
                      to="/ballot"
                      className="inline-flex items-center px-8 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      Find Your Ballot
                    </Link>
                  </div>
                </div>
              )}

              {activeTab === 'candidates' && (
                <div>
                  <div className="text-center mb-12">
                    <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                      Connect Directly with Voters
                    </h2>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                      Build trust and transparency by answering voter questions on video
                    </p>
                  </div>

                  <div className="grid gap-8 max-w-4xl mx-auto">
                    {candidateSteps.map((step, index) => (
                      <div key={step.title} className="flex gap-6">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                            <step.icon className="h-6 w-6 text-green-600" aria-hidden="true" />
                          </div>
                        </div>
                        <div className="flex-grow">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-sm font-semibold text-green-600">
                              Step {index + 1}
                            </span>
                            <h3 className="text-2xl font-bold text-gray-900">{step.title}</h3>
                          </div>
                          <p className="text-gray-600 text-lg mb-2">{step.description}</p>
                          <p className="text-gray-500">{step.detail}</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="text-center mt-12">
                    <Link
                      to="/candidate/onboarding"
                      className="inline-flex items-center px-8 py-3 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Join as a Candidate
                    </Link>
                  </div>
                </div>
              )}

              {activeTab === 'cities' && (
                <div>
                  <div className="text-center mb-12">
                    <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                      Bring CivicQ to Your Community
                    </h2>
                    <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                      Empower your voters with direct access to candidate information
                    </p>
                  </div>

                  <div className="grid gap-8 max-w-4xl mx-auto">
                    {citySteps.map((step, index) => (
                      <div key={step.title} className="flex gap-6">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                            <step.icon className="h-6 w-6 text-purple-600" aria-hidden="true" />
                          </div>
                        </div>
                        <div className="flex-grow">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-sm font-semibold text-purple-600">
                              Step {index + 1}
                            </span>
                            <h3 className="text-2xl font-bold text-gray-900">{step.title}</h3>
                          </div>
                          <p className="text-gray-600 text-lg mb-2">{step.description}</p>
                          <p className="text-gray-500">{step.detail}</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="text-center mt-12">
                    <Link
                      to="/city/register"
                      className="inline-flex items-center px-8 py-3 bg-purple-600 text-white font-medium rounded-lg hover:bg-purple-700 transition-colors"
                    >
                      Register Your City
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* FAQ Section */}
          <div className="bg-gray-50 py-16">
            <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="text-center mb-12">
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                  Frequently Asked Questions
                </h2>
                <p className="text-xl text-gray-600">
                  Everything you need to know about CivicQ
                </p>
              </div>

              <div className="space-y-4">
                {faqs.map((faq, index) => (
                  <div key={index} className="bg-white rounded-lg shadow-sm overflow-hidden">
                    <button
                      onClick={() => setExpandedFaq(expandedFaq === index ? null : index)}
                      className="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-gray-50 transition-colors"
                    >
                      <span className="font-semibold text-gray-900">{faq.question}</span>
                      <svg
                        className={`h-5 w-5 text-gray-500 transition-transform ${
                          expandedFaq === index ? 'transform rotate-180' : ''
                        }`}
                        fill="none"
                        viewBox="0 0 24 24"
                        stroke="currentColor"
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                    {expandedFaq === index && (
                      <div className="px-6 pb-4 text-gray-600">
                        {faq.answer}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="text-center mt-8">
                <p className="text-gray-600 mb-4">Still have questions?</p>
                <Link
                  to="/contact"
                  className="text-blue-600 hover:text-blue-700 font-medium"
                >
                  Contact our team →
                </Link>
              </div>
            </div>
          </div>

          {/* CTA Section */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 py-16">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
                Ready to Get Started?
              </h2>
              <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
                Join thousands of voters making informed decisions with CivicQ
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/ballot"
                  className="inline-flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-blue-700 bg-white hover:bg-blue-50 transition-colors"
                >
                  Find Your Ballot
                </Link>
                <Link
                  to="/register"
                  className="inline-flex items-center justify-center px-8 py-3 border-2 border-white text-base font-medium rounded-md text-white hover:bg-white hover:text-blue-700 transition-colors"
                >
                  Create Account
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
