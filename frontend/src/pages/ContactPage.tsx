import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import {
  EnvelopeIcon,
  PhoneIcon,
  MapPinIcon,
  QuestionMarkCircleIcon,
  UserGroupIcon,
  BuildingOfficeIcon,
  ChatBubbleLeftRightIcon
} from '@heroicons/react/24/outline';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    category: 'general',
    message: ''
  });
  const [submitted, setSubmitted] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    // TODO: Integrate with backend contact form API
    // For now, just simulate submission
    await new Promise(resolve => setTimeout(resolve, 1000));

    setSubmitted(true);
    setIsSubmitting(false);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const contactReasons = [
    {
      icon: QuestionMarkCircleIcon,
      title: 'General Questions',
      description: 'Learn more about CivicQ and how it works',
      category: 'general'
    },
    {
      icon: UserGroupIcon,
      title: 'For Candidates',
      description: 'Information about joining as a candidate',
      category: 'candidate'
    },
    {
      icon: BuildingOfficeIcon,
      title: 'For Cities',
      description: 'Bring CivicQ to your community',
      category: 'city'
    },
    {
      icon: ChatBubbleLeftRightIcon,
      title: 'Support & Feedback',
      description: 'Report issues or share suggestions',
      category: 'support'
    }
  ];

  return (
    <>
      <Helmet>
        <title>Contact Us - CivicQ</title>
        <meta
          name="description"
          content="Get in touch with CivicQ. Whether you're a voter, candidate, or city official, we're here to help you get started."
        />
        <meta property="og:title" content="Contact CivicQ" />
        <meta
          property="og:description"
          content="Have questions about CivicQ? Contact our team for support, partnership opportunities, or general inquiries."
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
                  Get in Touch
                </h1>
                <p className="text-xl text-blue-100 max-w-2xl mx-auto">
                  Have questions or want to bring CivicQ to your community? We'd love to hear from you.
                </p>
              </div>
            </div>
          </div>

          {/* Contact Reasons Grid */}
          <div className="bg-white py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {contactReasons.map((reason) => (
                  <div
                    key={reason.category}
                    className="bg-gray-50 rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
                    onClick={() => setFormData({ ...formData, category: reason.category })}
                  >
                    <reason.icon className="h-8 w-8 text-blue-600 mb-3" aria-hidden="true" />
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{reason.title}</h3>
                    <p className="text-gray-600 text-sm">{reason.description}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Contact Form and Info */}
          <div className="py-16 bg-gray-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="grid lg:grid-cols-3 gap-8">
                {/* Contact Form */}
                <div className="lg:col-span-2">
                  <div className="bg-white rounded-lg shadow-sm p-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">Send Us a Message</h2>

                    {submitted ? (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                        <div className="text-green-600 mb-2">
                          <svg
                            className="h-12 w-12 mx-auto"
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M5 13l4 4L19 7"
                            />
                          </svg>
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          Message Sent Successfully!
                        </h3>
                        <p className="text-gray-600 mb-4">
                          Thank you for contacting us. We'll get back to you within 1-2 business days.
                        </p>
                        <button
                          onClick={() => {
                            setSubmitted(false);
                            setFormData({ name: '', email: '', subject: '', category: 'general', message: '' });
                          }}
                          className="text-blue-600 hover:text-blue-700 font-medium"
                        >
                          Send Another Message
                        </button>
                      </div>
                    ) : (
                      <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="grid md:grid-cols-2 gap-6">
                          <div>
                            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
                              Full Name <span className="text-red-500">*</span>
                            </label>
                            <input
                              type="text"
                              id="name"
                              name="name"
                              required
                              value={formData.name}
                              onChange={handleChange}
                              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              placeholder="John Doe"
                            />
                          </div>

                          <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                              Email Address <span className="text-red-500">*</span>
                            </label>
                            <input
                              type="email"
                              id="email"
                              name="email"
                              required
                              value={formData.email}
                              onChange={handleChange}
                              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                              placeholder="john@example.com"
                            />
                          </div>
                        </div>

                        <div>
                          <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                            Category <span className="text-red-500">*</span>
                          </label>
                          <select
                            id="category"
                            name="category"
                            required
                            value={formData.category}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                          >
                            <option value="general">General Questions</option>
                            <option value="candidate">For Candidates</option>
                            <option value="city">For Cities</option>
                            <option value="support">Support & Feedback</option>
                            <option value="partnership">Partnership Opportunities</option>
                            <option value="press">Press & Media</option>
                            <option value="other">Other</option>
                          </select>
                        </div>

                        <div>
                          <label htmlFor="subject" className="block text-sm font-medium text-gray-700 mb-2">
                            Subject <span className="text-red-500">*</span>
                          </label>
                          <input
                            type="text"
                            id="subject"
                            name="subject"
                            required
                            value={formData.subject}
                            onChange={handleChange}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                            placeholder="How can we help?"
                          />
                        </div>

                        <div>
                          <label htmlFor="message" className="block text-sm font-medium text-gray-700 mb-2">
                            Message <span className="text-red-500">*</span>
                          </label>
                          <textarea
                            id="message"
                            name="message"
                            required
                            value={formData.message}
                            onChange={handleChange}
                            rows={6}
                            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                            placeholder="Tell us more about your inquiry..."
                          />
                        </div>

                        <button
                          type="submit"
                          disabled={isSubmitting}
                          className="w-full bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                          {isSubmitting ? 'Sending...' : 'Send Message'}
                        </button>
                      </form>
                    )}
                  </div>
                </div>

                {/* Contact Info Sidebar */}
                <div className="lg:col-span-1 space-y-6">
                  {/* Contact Info Card */}
                  <div className="bg-white rounded-lg shadow-sm p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">Contact Information</h3>
                    <div className="space-y-4">
                      <div className="flex items-start gap-3">
                        <EnvelopeIcon className="h-6 w-6 text-blue-600 flex-shrink-0" aria-hidden="true" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">Email</div>
                          <a
                            href="mailto:hello@civicq.com"
                            className="text-blue-600 hover:text-blue-700"
                          >
                            hello@civicq.com
                          </a>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <PhoneIcon className="h-6 w-6 text-blue-600 flex-shrink-0" aria-hidden="true" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">Phone</div>
                          <a
                            href="tel:+18005551234"
                            className="text-blue-600 hover:text-blue-700"
                          >
                            (800) 555-1234
                          </a>
                        </div>
                      </div>

                      <div className="flex items-start gap-3">
                        <MapPinIcon className="h-6 w-6 text-blue-600 flex-shrink-0" aria-hidden="true" />
                        <div>
                          <div className="text-sm font-medium text-gray-900">Address</div>
                          <div className="text-gray-600 text-sm">
                            123 Democracy Street<br />
                            Suite 100<br />
                            Washington, DC 20001
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Quick Links Card */}
                  <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-4">Quick Links</h3>
                    <div className="space-y-3">
                      <Link
                        to="/how-it-works"
                        className="block text-blue-600 hover:text-blue-700 font-medium"
                      >
                        How CivicQ Works →
                      </Link>
                      <Link
                        to="/about"
                        className="block text-blue-600 hover:text-blue-700 font-medium"
                      >
                        About Us →
                      </Link>
                      <Link
                        to="/ballot"
                        className="block text-blue-600 hover:text-blue-700 font-medium"
                      >
                        Find Your Ballot →
                      </Link>
                      <Link
                        to="/city/register"
                        className="block text-blue-600 hover:text-blue-700 font-medium"
                      >
                        Register Your City →
                      </Link>
                    </div>
                  </div>

                  {/* FAQ Link */}
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                    <h3 className="text-lg font-bold text-gray-900 mb-2">Have a Quick Question?</h3>
                    <p className="text-gray-600 text-sm mb-4">
                      Check out our FAQ page for answers to common questions.
                    </p>
                    <Link
                      to="/how-it-works"
                      className="text-blue-600 hover:text-blue-700 font-medium"
                    >
                      View FAQ →
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>

        <Footer />
      </div>
    </>
  );
}
