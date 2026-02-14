import React from 'react';
import { Layout } from '../components';
import SEOHelmet from '../components/SEOHelmet';
import StructuredData from '../components/StructuredData';
import { generateWebPageSchema } from '../utils/seo';

/**
 * Accessibility Statement Page
 * WCAG 2.1 AA Compliance Statement
 */
const AccessibilityStatementPage: React.FC = () => {
  const lastUpdated = 'February 14, 2026';

  const structuredData = generateWebPageSchema({
    name: 'Accessibility Statement - CivicQ',
    description: 'CivicQ accessibility commitment and WCAG 2.1 AA compliance information',
    url: window.location.href,
  });

  return (
    <Layout>
      <SEOHelmet
        title="Accessibility Statement"
        description="CivicQ is committed to ensuring digital accessibility for people with disabilities. Learn about our WCAG 2.1 AA compliance efforts."
        canonical={window.location.href}
        type="article"
      />
      <StructuredData data={structuredData} />

      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Accessibility Statement</h1>
        <p className="text-gray-600 mb-8">Last Updated: {lastUpdated}</p>

        <div className="prose prose-blue max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Our Commitment</h2>
            <p className="text-gray-700 mb-4">
              CivicQ is committed to ensuring digital accessibility for people with disabilities.
              We are continually improving the user experience for everyone and applying the
              relevant accessibility standards.
            </p>
            <p className="text-gray-700 mb-4">
              We believe that civic engagement should be accessible to all citizens, regardless
              of ability. Making our platform accessible is not just a legal requirement—it's
              fundamental to our mission of strengthening democracy.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Conformance Status</h2>
            <p className="text-gray-700 mb-4">
              CivicQ aims to conform to the{' '}
              <a
                href="https://www.w3.org/WAI/WCAG21/quickref/"
                className="text-blue-600 hover:underline"
                target="_blank"
                rel="noopener noreferrer"
              >
                Web Content Accessibility Guidelines (WCAG) 2.1
              </a>{' '}
              at the AA level. These guidelines explain how to make web content more accessible
              for people with disabilities.
            </p>
            <p className="text-gray-700 mb-4">
              <strong>Conformance Level:</strong> WCAG 2.1 Level AA
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Accessibility Features</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Screen Reader Support</h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Semantic HTML5 elements for proper document structure</li>
              <li>ARIA labels and landmarks for navigation</li>
              <li>Alternative text for all images</li>
              <li>Descriptive link text and button labels</li>
              <li>Proper heading hierarchy</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Keyboard Navigation</h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Full keyboard accessibility for all features</li>
              <li>Visible focus indicators</li>
              <li>Logical tab order</li>
              <li>Skip links to bypass repetitive content</li>
              <li>Keyboard shortcuts for common actions</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Visual Design</h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Sufficient color contrast (minimum 4.5:1 for text)</li>
              <li>Text resizing up to 200% without loss of functionality</li>
              <li>No reliance on color alone to convey information</li>
              <li>Clear visual focus indicators</li>
              <li>Readable fonts and appropriate text spacing</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Content and Media</h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Video captions and transcripts (where applicable)</li>
              <li>Text alternatives for non-text content</li>
              <li>Clear and simple language</li>
              <li>Consistent navigation and interface</li>
              <li>Error identification and suggestions</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Forms and Input</h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Clearly labeled form fields</li>
              <li>Error messages associated with fields</li>
              <li>Instructions and help text</li>
              <li>Accessible date pickers and custom controls</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Compatible Technologies</h2>
            <p className="text-gray-700 mb-4">
              CivicQ is designed to be compatible with the following assistive technologies:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Screen readers (JAWS, NVDA, VoiceOver, TalkBack)</li>
              <li>Screen magnification software</li>
              <li>Speech recognition software</li>
              <li>Keyboard-only navigation</li>
              <li>Alternative input devices</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Supported Browsers</h3>
            <p className="text-gray-700 mb-4">
              CivicQ is tested with the following browsers and assistive technology combinations:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Chrome with NVDA (Windows)</li>
              <li>Firefox with NVDA (Windows)</li>
              <li>Safari with VoiceOver (macOS and iOS)</li>
              <li>Chrome with TalkBack (Android)</li>
              <li>Edge with Narrator (Windows)</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Known Limitations</h2>
            <p className="text-gray-700 mb-4">
              Despite our best efforts, some limitations may exist:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Third-party embedded content may not be fully accessible</li>
              <li>User-generated video content may lack captions (we encourage users to add them)</li>
              <li>Some legacy features are being updated to meet current standards</li>
              <li>PDF documents uploaded by users may not be accessible</li>
            </ul>
            <p className="text-gray-700 mb-4">
              We are actively working to address these limitations.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Testing and Evaluation</h2>
            <p className="text-gray-700 mb-4">
              We regularly test our platform for accessibility:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Automated accessibility testing with axe, WAVE, and Lighthouse</li>
              <li>Manual testing with screen readers and keyboard navigation</li>
              <li>User testing with people who use assistive technologies</li>
              <li>Code reviews for accessibility compliance</li>
              <li>Third-party accessibility audits</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Feedback and Contact</h2>
            <p className="text-gray-700 mb-4">
              We welcome your feedback on the accessibility of CivicQ. Please let us know if you
              encounter accessibility barriers:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Email: accessibility@civicq.com</li>
              <li>Phone: [Your Phone Number]</li>
              <li>Mail: [Your Mailing Address]</li>
            </ul>
            <p className="text-gray-700 mb-4">
              We aim to respond to accessibility feedback within 5 business days.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Formal Complaints</h2>
            <p className="text-gray-700 mb-4">
              If you are not satisfied with our response to your accessibility concern, you may:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>File a formal complaint with our accessibility team</li>
              <li>Contact the U.S. Department of Justice (for ADA compliance)</li>
              <li>Contact your local disability rights organization</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Ongoing Improvements</h2>
            <p className="text-gray-700 mb-4">
              Accessibility is an ongoing effort. We are committed to:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Regular accessibility audits and updates</li>
              <li>Training our team on accessibility best practices</li>
              <li>Incorporating accessibility from the design phase</li>
              <li>Staying current with accessibility standards and guidelines</li>
              <li>Engaging with the disability community for feedback</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Technical Specifications</h2>
            <p className="text-gray-700 mb-4">
              Accessibility of CivicQ relies on the following technologies:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>HTML5</li>
              <li>CSS3</li>
              <li>JavaScript (React)</li>
              <li>WAI-ARIA</li>
            </ul>
            <p className="text-gray-700 mb-4">
              These technologies are relied upon for conformance with the accessibility standards used.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">Additional Resources</h2>
            <p className="text-gray-700 mb-4">
              For more information about web accessibility:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>
                <a
                  href="https://www.w3.org/WAI/"
                  className="text-blue-600 hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Web Accessibility Initiative (WAI)
                </a>
              </li>
              <li>
                <a
                  href="https://www.ada.gov/"
                  className="text-blue-600 hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Americans with Disabilities Act (ADA)
                </a>
              </li>
              <li>
                <a
                  href="https://www.section508.gov/"
                  className="text-blue-600 hover:underline"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Section 508
                </a>
              </li>
            </ul>
          </section>

          <div className="mt-12 p-6 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Our Promise</h3>
            <p className="text-blue-800">
              We are dedicated to making CivicQ accessible to all users. Accessibility is not
              just compliance—it's about ensuring everyone can participate in civic engagement.
              Your feedback helps us improve.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AccessibilityStatementPage;
