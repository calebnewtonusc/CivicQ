import React from 'react';
import { Layout } from '../components';
import SEOHelmet from '../components/SEOHelmet';
import StructuredData from '../components/StructuredData';
import { generateWebPageSchema } from '../utils/seo';

/**
 * Cookie Policy Page
 * Comprehensive cookie usage disclosure
 */
const CookiePolicyPage: React.FC = () => {
  const lastUpdated = 'February 14, 2026';

  const structuredData = generateWebPageSchema({
    name: 'Cookie Policy - CivicQ',
    description: 'Learn about how CivicQ uses cookies and similar tracking technologies',
    url: window.location.href,
  });

  return (
    <Layout>
      <SEOHelmet
        title="Cookie Policy"
        description="Learn about how CivicQ uses cookies and similar tracking technologies to improve your experience."
        canonical={window.location.href}
        type="article"
      />
      <StructuredData data={structuredData} />

      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Cookie Policy</h1>
        <p className="text-gray-600 mb-8">Last Updated: {lastUpdated}</p>

        <div className="prose prose-blue max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">What Are Cookies?</h2>
            <p className="text-gray-700 mb-4">
              Cookies are small text files that are placed on your device (computer, smartphone,
              tablet) when you visit a website. They are widely used to make websites work more
              efficiently and provide information to website owners.
            </p>
            <p className="text-gray-700 mb-4">
              Cookies can be "persistent" (remain on your device until deleted or expired) or
              "session" (deleted when you close your browser).
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">How We Use Cookies</h2>
            <p className="text-gray-700 mb-4">
              CivicQ uses cookies and similar technologies for the following purposes:
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">1. Essential Cookies</h3>
            <p className="text-gray-700 mb-4">
              These cookies are necessary for the website to function properly. They enable core
              functionality such as security, network management, and accessibility.
            </p>
            <div className="overflow-x-auto mb-4">
              <table className="min-w-full border border-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="border border-gray-300 px-4 py-2 text-left">Cookie Name</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Purpose</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Duration</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="border border-gray-300 px-4 py-2">session_id</td>
                    <td className="border border-gray-300 px-4 py-2">Maintains your login session</td>
                    <td className="border border-gray-300 px-4 py-2">Session</td>
                  </tr>
                  <tr>
                    <td className="border border-gray-300 px-4 py-2">csrf_token</td>
                    <td className="border border-gray-300 px-4 py-2">Security protection against cross-site attacks</td>
                    <td className="border border-gray-300 px-4 py-2">Session</td>
                  </tr>
                  <tr>
                    <td className="border border-gray-300 px-4 py-2">cookie_consent</td>
                    <td className="border border-gray-300 px-4 py-2">Remembers your cookie preferences</td>
                    <td className="border border-gray-300 px-4 py-2">1 year</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="text-gray-700 mb-4">
              <strong>Can you opt out?</strong> No. These cookies are essential for the website
              to function and cannot be disabled.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">2. Functional Cookies</h3>
            <p className="text-gray-700 mb-4">
              These cookies enable enhanced functionality and personalization, such as remembering
              your preferences and settings.
            </p>
            <div className="overflow-x-auto mb-4">
              <table className="min-w-full border border-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="border border-gray-300 px-4 py-2 text-left">Cookie Name</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Purpose</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Duration</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="border border-gray-300 px-4 py-2">user_preferences</td>
                    <td className="border border-gray-300 px-4 py-2">Stores your display preferences</td>
                    <td className="border border-gray-300 px-4 py-2">1 year</td>
                  </tr>
                  <tr>
                    <td className="border border-gray-300 px-4 py-2">language</td>
                    <td className="border border-gray-300 px-4 py-2">Remembers your language preference</td>
                    <td className="border border-gray-300 px-4 py-2">1 year</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="text-gray-700 mb-4">
              <strong>Can you opt out?</strong> Yes. You can disable these through cookie settings,
              but some features may not work as intended.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3. Analytics Cookies</h3>
            <p className="text-gray-700 mb-4">
              These cookies help us understand how visitors interact with our website by collecting
              and reporting information anonymously.
            </p>
            <div className="overflow-x-auto mb-4">
              <table className="min-w-full border border-gray-300">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="border border-gray-300 px-4 py-2 text-left">Cookie Name</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Purpose</th>
                    <th className="border border-gray-300 px-4 py-2 text-left">Duration</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="border border-gray-300 px-4 py-2">_ga</td>
                    <td className="border border-gray-300 px-4 py-2">Google Analytics - distinguishes users</td>
                    <td className="border border-gray-300 px-4 py-2">2 years</td>
                  </tr>
                  <tr>
                    <td className="border border-gray-300 px-4 py-2">_gid</td>
                    <td className="border border-gray-300 px-4 py-2">Google Analytics - distinguishes users</td>
                    <td className="border border-gray-300 px-4 py-2">24 hours</td>
                  </tr>
                  <tr>
                    <td className="border border-gray-300 px-4 py-2">_gat</td>
                    <td className="border border-gray-300 px-4 py-2">Google Analytics - throttles requests</td>
                    <td className="border border-gray-300 px-4 py-2">1 minute</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="text-gray-700 mb-4">
              <strong>Can you opt out?</strong> Yes. You can opt out through cookie settings or
              using the{' '}
              <a
                href="https://tools.google.com/dlpage/gaoptout"
                className="text-blue-600 hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                Google Analytics Opt-out Browser Add-on
              </a>
              .
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">4. Performance Cookies</h3>
            <p className="text-gray-700 mb-4">
              These cookies collect information about how you use our website to help us improve
              performance and user experience.
            </p>
            <p className="text-gray-700 mb-4">
              <strong>Can you opt out?</strong> Yes. You can disable these through cookie settings.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Third-Party Cookies</h2>
            <p className="text-gray-700 mb-4">
              In addition to our own cookies, we use cookies from third-party services:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li><strong>Google Analytics:</strong> For website analytics and performance monitoring</li>
              <li><strong>Video Hosting Services:</strong> For embedding and playing video content</li>
              <li><strong>CDN Services:</strong> For faster content delivery</li>
            </ul>
            <p className="text-gray-700 mb-4">
              These third parties have their own privacy policies and cookie policies. We recommend
              reviewing them.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Other Tracking Technologies</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Local Storage</h3>
            <p className="text-gray-700 mb-4">
              We use browser local storage to save preferences and improve performance. This data
              stays on your device and is not transmitted to our servers unless you take specific
              actions (e.g., saving a setting).
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Web Beacons</h3>
            <p className="text-gray-700 mb-4">
              We may use web beacons (small graphic images) in our emails to track whether emails
              have been opened and links clicked.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Managing Your Cookie Preferences</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Cookie Settings</h3>
            <p className="text-gray-700 mb-4">
              You can manage your cookie preferences through our cookie consent banner or in your
              account settings. Your choices will be saved and respected.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Browser Controls</h3>
            <p className="text-gray-700 mb-4">
              Most web browsers allow you to control cookies through settings:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>
                <a
                  href="https://support.google.com/chrome/answer/95647"
                  className="text-blue-600 hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Chrome
                </a>
              </li>
              <li>
                <a
                  href="https://support.mozilla.org/en-US/kb/enhanced-tracking-protection-firefox-desktop"
                  className="text-blue-600 hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Firefox
                </a>
              </li>
              <li>
                <a
                  href="https://support.apple.com/guide/safari/manage-cookies-sfri11471/mac"
                  className="text-blue-600 hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Safari
                </a>
              </li>
              <li>
                <a
                  href="https://support.microsoft.com/en-us/microsoft-edge/delete-cookies-in-microsoft-edge-63947406-40ac-c3b8-57b9-2a946a29ae09"
                  className="text-blue-600 hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Edge
                </a>
              </li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Do Not Track</h3>
            <p className="text-gray-700 mb-4">
              Some browsers have a "Do Not Track" feature. At this time, there is no standard for
              how to respond to Do Not Track signals, but we respect your privacy choices.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Impact of Disabling Cookies</h2>
            <p className="text-gray-700 mb-4">
              If you disable cookies, some features of CivicQ may not function properly:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>You may not be able to stay logged in</li>
              <li>Your preferences may not be saved</li>
              <li>Some interactive features may not work</li>
              <li>You may see less relevant content</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Updates to This Policy</h2>
            <p className="text-gray-700 mb-4">
              We may update this Cookie Policy from time to time to reflect changes in our
              practices or for legal, operational, or regulatory reasons. We will notify you
              of material changes through our website or by email.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Contact Us</h2>
            <p className="text-gray-700 mb-4">
              If you have questions about our use of cookies, please contact us:
            </p>
            <address className="text-gray-700 not-italic">
              Email: privacy@civicq.com<br />
              Address: [Your Legal Address]
            </address>
          </section>

          <div className="mt-12 p-6 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Your Control</h3>
            <p className="text-blue-800">
              You are in control of your cookie preferences. We use cookies to improve your
              experience, but you can disable non-essential cookies at any time through your
              browser or our cookie settings.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CookiePolicyPage;
