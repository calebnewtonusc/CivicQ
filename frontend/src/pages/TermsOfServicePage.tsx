import React from 'react';
import { Layout } from '../components';
import SEOHelmet from '../components/SEOHelmet';
import StructuredData from '../components/StructuredData';
import { generateWebPageSchema } from '../utils/seo';

/**
 * Terms of Service Page
 * Comprehensive legal terms covering platform usage, user responsibilities,
 * and liability limitations
 */
const TermsOfServicePage: React.FC = () => {
  const lastUpdated = 'February 14, 2026';

  const structuredData = generateWebPageSchema({
    name: 'Terms of Service - CivicQ',
    description: 'Terms of Service and conditions for using the CivicQ platform',
    url: window.location.href,
  });

  return (
    <Layout>
      <SEOHelmet
        title="Terms of Service"
        description="Terms of Service and conditions for using the CivicQ civic engagement platform. Last updated February 14, 2026."
        canonical={window.location.href}
        type="article"
      />
      <StructuredData data={structuredData} />

      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Terms of Service</h1>
        <p className="text-gray-600 mb-8">Last Updated: {lastUpdated}</p>

        <div className="prose prose-blue max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Acceptance of Terms</h2>
            <p className="text-gray-700 mb-4">
              By accessing or using CivicQ ("the Service", "Platform", "we", "us", or "our"),
              you agree to be bound by these Terms of Service ("Terms"). If you do not agree to
              these Terms, you may not access or use the Service.
            </p>
            <p className="text-gray-700 mb-4">
              These Terms constitute a legally binding agreement between you and CivicQ. We reserve
              the right to update these Terms at any time, and your continued use of the Service
              constitutes acceptance of any changes.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Description of Service</h2>
            <p className="text-gray-700 mb-4">
              CivicQ is a civic engagement platform that connects voters with local political
              candidates through video-based questions and answers. The Service allows:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Voters to submit, vote on, and view questions for candidates</li>
              <li>Candidates to create profiles and submit video responses to questions</li>
              <li>Public access to candidate information and video responses</li>
              <li>Community engagement features including voting and commenting</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. User Accounts</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.1 Account Creation</h3>
            <p className="text-gray-700 mb-4">
              To access certain features, you must create an account. You agree to:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Provide accurate, current, and complete information</li>
              <li>Maintain and update your information to keep it accurate</li>
              <li>Maintain the security of your password</li>
              <li>Accept responsibility for all activities under your account</li>
              <li>Notify us immediately of any unauthorized use</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.2 Account Types</h3>
            <p className="text-gray-700 mb-4">
              CivicQ offers two types of accounts:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li><strong>Voter Accounts:</strong> For community members to engage with questions and candidates</li>
              <li><strong>Candidate Accounts:</strong> For verified political candidates to create profiles and answer questions</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.3 Candidate Verification</h3>
            <p className="text-gray-700 mb-4">
              Candidate accounts require verification to ensure authenticity. By creating a
              candidate account, you represent and warrant that you are a legitimate candidate
              for public office and will provide accurate information about your candidacy.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. User Conduct</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">4.1 Prohibited Activities</h3>
            <p className="text-gray-700 mb-4">
              You agree not to:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Violate any local, state, federal, or international law</li>
              <li>Infringe on intellectual property rights</li>
              <li>Transmit harmful, offensive, or inappropriate content</li>
              <li>Harass, threaten, or intimidate other users</li>
              <li>Impersonate any person or entity</li>
              <li>Manipulate voting or engagement metrics</li>
              <li>Upload viruses, malware, or malicious code</li>
              <li>Scrape, crawl, or use automated systems without permission</li>
              <li>Interfere with the Service's operation</li>
              <li>Share false or misleading information</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">4.2 Content Standards</h3>
            <p className="text-gray-700 mb-4">
              All content must:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Be civil and respectful</li>
              <li>Comply with campaign finance and election laws</li>
              <li>Not contain hate speech, discrimination, or threats</li>
              <li>Not contain explicit, violent, or inappropriate material</li>
              <li>Not violate others' privacy or confidentiality</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Content Ownership and License</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.1 Your Content</h3>
            <p className="text-gray-700 mb-4">
              You retain ownership of content you submit to CivicQ. By submitting content, you grant
              us a worldwide, non-exclusive, royalty-free, transferable license to use, reproduce,
              distribute, prepare derivative works of, display, and perform your content in connection
              with the Service.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.2 Public Content</h3>
            <p className="text-gray-700 mb-4">
              Content you post publicly (questions, answers, comments, profiles) may be viewed,
              shared, and used by other users and the general public. You understand that such
              content may be indexed by search engines and archived.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">5.3 Our Content</h3>
            <p className="text-gray-700 mb-4">
              All CivicQ branding, logos, designs, and platform features are owned by us and
              protected by copyright, trademark, and other intellectual property laws.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Privacy and Data Protection</h2>
            <p className="text-gray-700 mb-4">
              Your use of the Service is subject to our Privacy Policy, which describes how we
              collect, use, and protect your personal information. By using the Service, you
              consent to our data practices as described in the Privacy Policy.
            </p>
            <p className="text-gray-700 mb-4">
              For users in the European Union, we comply with GDPR requirements. For California
              residents, we comply with CCPA requirements. See our Privacy Policy for details.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. Moderation and Enforcement</h2>
            <p className="text-gray-700 mb-4">
              We reserve the right, but not the obligation, to:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Monitor and review user content</li>
              <li>Remove or modify content that violates these Terms</li>
              <li>Suspend or terminate accounts for violations</li>
              <li>Cooperate with law enforcement</li>
              <li>Take legal action against violators</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Disclaimers</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">8.1 No Warranty</h3>
            <p className="text-gray-700 mb-4">
              THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND,
              EXPRESS OR IMPLIED, INCLUDING WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
              PURPOSE, AND NON-INFRINGEMENT.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">8.2 No Endorsement</h3>
            <p className="text-gray-700 mb-4">
              CivicQ does not endorse any candidate, political party, or viewpoint. The inclusion
              of a candidate on the platform does not constitute an endorsement.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">8.3 Third-Party Content</h3>
            <p className="text-gray-700 mb-4">
              We are not responsible for the accuracy, completeness, or reliability of user-generated
              content. Users are solely responsible for their own content.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">8.4 Availability</h3>
            <p className="text-gray-700 mb-4">
              We do not guarantee uninterrupted or error-free service. The Service may be modified,
              suspended, or discontinued at any time without notice.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Limitation of Liability</h2>
            <p className="text-gray-700 mb-4">
              TO THE MAXIMUM EXTENT PERMITTED BY LAW, CIVICQ SHALL NOT BE LIABLE FOR ANY INDIRECT,
              INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, INCLUDING LOSS OF PROFITS,
              DATA, USE, OR GOODWILL, ARISING FROM:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Your use or inability to use the Service</li>
              <li>User content or conduct</li>
              <li>Unauthorized access to your account or data</li>
              <li>Service interruptions or errors</li>
              <li>Any third-party content or services</li>
            </ul>
            <p className="text-gray-700 mb-4">
              Our total liability shall not exceed the amount you paid us in the past 12 months,
              or $100, whichever is greater.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Indemnification</h2>
            <p className="text-gray-700 mb-4">
              You agree to indemnify and hold harmless CivicQ, its officers, directors, employees,
              and agents from any claims, damages, losses, liabilities, and expenses (including
              legal fees) arising from:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Your use of the Service</li>
              <li>Your content</li>
              <li>Your violation of these Terms</li>
              <li>Your violation of any rights of another</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Dispute Resolution</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">11.1 Governing Law</h3>
            <p className="text-gray-700 mb-4">
              These Terms shall be governed by and construed in accordance with the laws of the
              State of California, without regard to conflict of law principles.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">11.2 Arbitration</h3>
            <p className="text-gray-700 mb-4">
              Any dispute arising from these Terms or the Service shall be resolved through binding
              arbitration in accordance with the American Arbitration Association's rules, except
              that either party may seek injunctive relief in court.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">11.3 Class Action Waiver</h3>
            <p className="text-gray-700 mb-4">
              You agree that disputes will be resolved individually and you waive the right to
              participate in class actions or class-wide arbitration.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Termination</h2>
            <p className="text-gray-700 mb-4">
              Either party may terminate this agreement at any time. We may suspend or terminate
              your account immediately without notice for:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Violation of these Terms</li>
              <li>Fraudulent or illegal activity</li>
              <li>Harm to other users or the Service</li>
              <li>Extended inactivity</li>
            </ul>
            <p className="text-gray-700 mb-4">
              Upon termination, your right to use the Service ceases immediately. Provisions
              concerning ownership, warranties, indemnification, and limitations of liability
              survive termination.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">13. General Provisions</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">13.1 Entire Agreement</h3>
            <p className="text-gray-700 mb-4">
              These Terms, together with our Privacy Policy and Cookie Policy, constitute the
              entire agreement between you and CivicQ.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">13.2 Severability</h3>
            <p className="text-gray-700 mb-4">
              If any provision is found unenforceable, the remaining provisions remain in effect.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">13.3 Assignment</h3>
            <p className="text-gray-700 mb-4">
              You may not assign these Terms without our consent. We may assign these Terms
              without restriction.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">13.4 No Waiver</h3>
            <p className="text-gray-700 mb-4">
              Our failure to enforce any right or provision does not constitute a waiver.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">14. Contact Information</h2>
            <p className="text-gray-700 mb-4">
              For questions about these Terms, please contact us at:
            </p>
            <address className="text-gray-700 not-italic">
              <strong>CivicQ Legal Department</strong><br />
              Email: legal@civicq.com<br />
              Address: [Your Legal Address]<br />
            </address>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">15. Updates to Terms</h2>
            <p className="text-gray-700 mb-4">
              We may update these Terms from time to time. We will notify you of material changes
              by email or through the Service. Your continued use after changes constitutes
              acceptance of the updated Terms.
            </p>
            <p className="text-gray-700 mb-4">
              We recommend reviewing these Terms periodically to stay informed of your rights
              and obligations.
            </p>
          </section>

          <div className="mt-12 p-6 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">Acknowledgment</h3>
            <p className="text-blue-800">
              BY USING CIVICQ, YOU ACKNOWLEDGE THAT YOU HAVE READ, UNDERSTOOD, AND AGREE TO BE
              BOUND BY THESE TERMS OF SERVICE.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default TermsOfServicePage;
