import React from 'react';
import { Layout } from '../components';
import SEOHelmet from '../components/SEOHelmet';
import StructuredData from '../components/StructuredData';
import { generateWebPageSchema } from '../utils/seo';

/**
 * Privacy Policy Page
 * GDPR and CCPA Compliant Privacy Policy
 */
const PrivacyPolicyPage: React.FC = () => {
  const lastUpdated = 'February 14, 2026';

  const structuredData = generateWebPageSchema({
    name: 'Privacy Policy - CivicQ',
    description: 'Privacy Policy for CivicQ - GDPR and CCPA compliant data protection information',
    url: window.location.href,
  });

  return (
    <Layout>
      <SEOHelmet
        title="Privacy Policy"
        description="Privacy Policy for CivicQ. Learn how we collect, use, and protect your personal information in compliance with GDPR and CCPA."
        canonical={window.location.href}
        type="article"
      />
      <StructuredData data={structuredData} />

      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
        <p className="text-gray-600 mb-8">Last Updated: {lastUpdated}</p>

        <div className="prose prose-blue max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Introduction</h2>
            <p className="text-gray-700 mb-4">
              CivicQ ("we", "us", or "our") is committed to protecting your privacy. This Privacy
              Policy explains how we collect, use, disclose, and safeguard your information when
              you use our civic engagement platform.
            </p>
            <p className="text-gray-700 mb-4">
              This policy complies with the General Data Protection Regulation (GDPR), California
              Consumer Privacy Act (CCPA), and other applicable data protection laws.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Information We Collect</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">2.1 Information You Provide</h3>
            <p className="text-gray-700 mb-4">We collect information you voluntarily provide:</p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li><strong>Account Information:</strong> Name, email address, password, username</li>
              <li><strong>Profile Information:</strong> Bio, photo, location, political affiliation</li>
              <li><strong>Candidate Information:</strong> Campaign details, contact information, verification documents</li>
              <li><strong>User Content:</strong> Questions, answers, comments, votes, video recordings</li>
              <li><strong>Communication:</strong> Messages sent through the platform, support inquiries</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">2.2 Automatically Collected Information</h3>
            <p className="text-gray-700 mb-4">We automatically collect certain information:</p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li><strong>Usage Data:</strong> Pages viewed, features used, time spent, interaction patterns</li>
              <li><strong>Device Information:</strong> IP address, browser type, operating system, device identifiers</li>
              <li><strong>Location Data:</strong> General geographic location based on IP address</li>
              <li><strong>Cookies and Tracking:</strong> Session data, preferences, analytics data</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">2.3 Third-Party Information</h3>
            <p className="text-gray-700 mb-4">We may receive information from:</p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Public records and election databases for candidate verification</li>
              <li>Analytics and service providers</li>
              <li>Social media platforms (if you connect your account)</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. How We Use Your Information</h2>
            <p className="text-gray-700 mb-4">We use your information for:</p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.1 Service Provision</h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Creating and managing your account</li>
              <li>Providing platform features and functionality</li>
              <li>Processing and displaying your content</li>
              <li>Facilitating communication between users and candidates</li>
              <li>Verifying candidate identities</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.2 Improvement and Analytics</h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Analyzing usage patterns and trends</li>
              <li>Improving platform features and user experience</li>
              <li>Conducting research and development</li>
              <li>Testing new features</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.3 Communication</h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Sending account-related notifications</li>
              <li>Responding to support requests</li>
              <li>Sending updates about the Service (with your consent)</li>
              <li>Sending marketing communications (with opt-in consent)</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.4 Security and Compliance</h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Preventing fraud and abuse</li>
              <li>Enforcing our Terms of Service</li>
              <li>Complying with legal obligations</li>
              <li>Protecting rights and safety</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Legal Basis for Processing (GDPR)</h2>
            <p className="text-gray-700 mb-4">
              For users in the European Union, we process your data based on:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li><strong>Consent:</strong> You have given clear consent for specific purposes</li>
              <li><strong>Contract:</strong> Processing is necessary to fulfill our contract with you</li>
              <li><strong>Legal Obligation:</strong> Processing is necessary to comply with the law</li>
              <li><strong>Legitimate Interests:</strong> Processing is necessary for our legitimate interests (e.g., fraud prevention, improving services)</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Information Sharing and Disclosure</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.1 Public Information</h3>
            <p className="text-gray-700 mb-4">
              Certain information is public by default:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Candidate profiles and campaign information</li>
              <li>Questions and answers posted publicly</li>
              <li>Comments and votes on public content</li>
              <li>Public portions of user profiles</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.2 Service Providers</h3>
            <p className="text-gray-700 mb-4">
              We share data with trusted service providers who assist us:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Cloud hosting and storage providers</li>
              <li>Analytics and monitoring services</li>
              <li>Email and communication services</li>
              <li>Payment processors (if applicable)</li>
              <li>Video hosting and streaming services</li>
            </ul>
            <p className="text-gray-700 mb-4">
              All service providers are contractually obligated to protect your data and use it
              only for specified purposes.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.3 Legal Requirements</h3>
            <p className="text-gray-700 mb-4">We may disclose information when required by law or to:</p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Comply with legal processes, court orders, or government requests</li>
              <li>Enforce our Terms of Service</li>
              <li>Protect rights, property, or safety of CivicQ, users, or the public</li>
              <li>Prevent fraud or illegal activity</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.4 Business Transfers</h3>
            <p className="text-gray-700 mb-4">
              In the event of a merger, acquisition, or sale of assets, your information may be
              transferred to the acquiring entity.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.5 With Your Consent</h3>
            <p className="text-gray-700 mb-4">
              We may share information for other purposes with your explicit consent.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Your Privacy Rights</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">6.1 GDPR Rights (EU Users)</h3>
            <p className="text-gray-700 mb-4">You have the right to:</p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li><strong>Access:</strong> Request a copy of your personal data</li>
              <li><strong>Rectification:</strong> Correct inaccurate or incomplete data</li>
              <li><strong>Erasure:</strong> Request deletion of your data ("right to be forgotten")</li>
              <li><strong>Restriction:</strong> Limit how we use your data</li>
              <li><strong>Portability:</strong> Receive your data in a portable format</li>
              <li><strong>Objection:</strong> Object to processing based on legitimate interests</li>
              <li><strong>Withdraw Consent:</strong> Withdraw consent at any time</li>
              <li><strong>Complain:</strong> Lodge a complaint with a supervisory authority</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">6.2 CCPA Rights (California Residents)</h3>
            <p className="text-gray-700 mb-4">California residents have the right to:</p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li><strong>Know:</strong> Request disclosure of data collected, used, and shared</li>
              <li><strong>Delete:</strong> Request deletion of personal information</li>
              <li><strong>Opt-Out:</strong> Opt-out of the sale of personal information (we do not sell your data)</li>
              <li><strong>Non-Discrimination:</strong> Not be discriminated against for exercising rights</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">6.3 Exercising Your Rights</h3>
            <p className="text-gray-700 mb-4">
              To exercise these rights, contact us at privacy@civicq.com. We will respond within
              30 days (GDPR) or 45 days (CCPA). We may request verification of your identity
              before processing requests.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Data Security</h2>
            <p className="text-gray-700 mb-4">
              We implement appropriate technical and organizational measures to protect your data:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Encryption of data in transit (HTTPS/TLS) and at rest</li>
              <li>Access controls and authentication mechanisms</li>
              <li>Regular security assessments and updates</li>
              <li>Employee training on data protection</li>
              <li>Incident response procedures</li>
            </ul>
            <p className="text-gray-700 mb-4">
              However, no system is completely secure. We cannot guarantee absolute security of
              your information.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Data Retention</h2>
            <p className="text-gray-700 mb-4">
              We retain your information for as long as necessary to:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Provide the Service to you</li>
              <li>Comply with legal obligations</li>
              <li>Resolve disputes and enforce agreements</li>
              <li>Maintain historical archives of public civic information</li>
            </ul>
            <p className="text-gray-700 mb-4">
              When you delete your account, we will delete or anonymize your personal information
              within 90 days, except for information we must retain for legal reasons or legitimate
              archival purposes (e.g., public questions and answers may be retained for historical
              civic records).
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. International Data Transfers</h2>
            <p className="text-gray-700 mb-4">
              Your information may be transferred to and processed in countries other than your own.
              We ensure adequate protection through:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Standard Contractual Clauses approved by the European Commission</li>
              <li>Privacy Shield certification (where applicable)</li>
              <li>Ensuring service providers meet adequate data protection standards</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Cookies and Tracking Technologies</h2>
            <p className="text-gray-700 mb-4">
              We use cookies and similar technologies. See our Cookie Policy for details.
            </p>
            <p className="text-gray-700 mb-4">
              You can control cookies through your browser settings and opt-out of analytics
              tracking. However, some features may not function properly without cookies.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Children's Privacy</h2>
            <p className="text-gray-700 mb-4">
              CivicQ is not intended for users under 13 years of age. We do not knowingly collect
              information from children under 13. If we learn we have collected information from
              a child under 13, we will delete it promptly.
            </p>
            <p className="text-gray-700 mb-4">
              For users between 13 and 18, parental consent may be required depending on
              jurisdiction and the type of account.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Third-Party Links</h2>
            <p className="text-gray-700 mb-4">
              The Service may contain links to third-party websites or services. We are not
              responsible for the privacy practices of these third parties. We encourage you
              to review their privacy policies.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">13. Data Breach Notification</h2>
            <p className="text-gray-700 mb-4">
              In the event of a data breach that affects your personal information, we will:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Notify affected users within 72 hours (as required by GDPR)</li>
              <li>Inform relevant supervisory authorities</li>
              <li>Provide details about the breach and remediation steps</li>
              <li>Offer support and guidance to affected users</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">14. Changes to This Privacy Policy</h2>
            <p className="text-gray-700 mb-4">
              We may update this Privacy Policy from time to time. We will notify you of material
              changes by:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Email notification to your registered address</li>
              <li>Prominent notice on the Service</li>
              <li>Updating the "Last Updated" date</li>
            </ul>
            <p className="text-gray-700 mb-4">
              Your continued use after changes constitutes acceptance of the updated Privacy Policy.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">15. Contact Information</h2>
            <p className="text-gray-700 mb-4">
              For privacy-related questions, requests, or complaints, contact:
            </p>
            <address className="text-gray-700 not-italic mb-4">
              <strong>Data Protection Officer</strong><br />
              CivicQ<br />
              Email: privacy@civicq.com<br />
              Address: [Your Legal Address]<br />
            </address>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">EU Representative</h3>
            <p className="text-gray-700 mb-4">
              If you are in the European Union, you may also contact our EU representative at
              eu-privacy@civicq.com.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">Supervisory Authority</h3>
            <p className="text-gray-700 mb-4">
              EU users have the right to lodge a complaint with their local data protection
              authority if they believe their data protection rights have been violated.
            </p>
          </section>

          <div className="mt-12 p-6 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Your Privacy Matters</h3>
            <p className="text-blue-800 mb-2">
              We are committed to transparency and protecting your privacy. If you have any
              questions or concerns, please don't hesitate to contact us.
            </p>
            <p className="text-blue-800">
              <strong>We do not sell your personal information.</strong>
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default PrivacyPolicyPage;
