import React from 'react';
import { Layout } from '../components';
import SEOHelmet from '../components/SEOHelmet';
import StructuredData from '../components/StructuredData';
import { generateWebPageSchema } from '../utils/seo';

/**
 * Data Processing Agreement Page
 * GDPR-compliant DPA for data processors
 */
const DataProcessingAgreementPage: React.FC = () => {
  const lastUpdated = 'February 14, 2026';

  const structuredData = generateWebPageSchema({
    name: 'Data Processing Agreement - CivicQ',
    description: 'GDPR-compliant Data Processing Agreement for CivicQ services',
    url: window.location.href,
  });

  return (
    <Layout>
      <SEOHelmet
        title="Data Processing Agreement"
        description="GDPR-compliant Data Processing Agreement outlining how CivicQ processes and protects personal data."
        canonical={window.location.href}
        type="article"
        noindex={true}
      />
      <StructuredData data={structuredData} />

      <div className="max-w-4xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">Data Processing Agreement</h1>
        <p className="text-gray-600 mb-8">Last Updated: {lastUpdated}</p>

        <div className="prose prose-blue max-w-none">
          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">1. Introduction and Scope</h2>
            <p className="text-gray-700 mb-4">
              This Data Processing Agreement ("DPA") forms part of the Terms of Service between
              you ("Data Controller") and CivicQ ("Data Processor") and applies where CivicQ
              processes personal data on your behalf in accordance with the General Data
              Protection Regulation (GDPR) and other applicable data protection laws.
            </p>
            <p className="text-gray-700 mb-4">
              This DPA applies to all processing of personal data by CivicQ on behalf of
              organizational users (e.g., campaign organizations, political parties, civic
              organizations).
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">2. Definitions</h2>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li><strong>Personal Data:</strong> Information relating to an identified or identifiable natural person</li>
              <li><strong>Processing:</strong> Any operation performed on personal data</li>
              <li><strong>Data Controller:</strong> The entity that determines purposes and means of processing</li>
              <li><strong>Data Processor:</strong> The entity that processes data on behalf of the controller</li>
              <li><strong>Data Subject:</strong> The individual whose personal data is being processed</li>
              <li><strong>Sub-processor:</strong> Third-party processor engaged by CivicQ</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">3. Processing Details</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.1 Subject Matter</h3>
            <p className="text-gray-700 mb-4">
              The subject matter of processing is the provision of the CivicQ platform services
              as described in the Terms of Service.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.2 Duration</h3>
            <p className="text-gray-700 mb-4">
              Processing will continue for the duration of the service agreement and for a
              retention period of up to 90 days after termination.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.3 Nature and Purpose</h3>
            <p className="text-gray-700 mb-4">
              CivicQ processes personal data to:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Provide civic engagement platform services</li>
              <li>Facilitate communication between voters and candidates</li>
              <li>Store and display user-generated content</li>
              <li>Provide analytics and insights</li>
              <li>Ensure platform security and integrity</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.4 Types of Personal Data</h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Contact information (name, email, phone)</li>
              <li>Account credentials</li>
              <li>Profile information and photos</li>
              <li>User-generated content (questions, answers, comments)</li>
              <li>Usage and activity data</li>
              <li>Location data (geographic region)</li>
              <li>Video and audio recordings</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">3.5 Categories of Data Subjects</h3>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Voters and constituents</li>
              <li>Political candidates</li>
              <li>Campaign staff and representatives</li>
              <li>Community organizers</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">4. Data Processor Obligations</h2>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">4.1 Processing Instructions</h3>
            <p className="text-gray-700 mb-4">
              CivicQ shall process personal data only on documented instructions from the Data
              Controller, unless required by law. If CivicQ believes an instruction violates
              GDPR or other data protection laws, it will immediately inform the Data Controller.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">4.2 Confidentiality</h3>
            <p className="text-gray-700 mb-4">
              CivicQ ensures that persons authorized to process personal data have committed
              themselves to confidentiality or are under an appropriate statutory obligation of
              confidentiality.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">4.3 Security Measures</h3>
            <p className="text-gray-700 mb-4">
              CivicQ implements appropriate technical and organizational measures to ensure a
              level of security appropriate to the risk, including:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Encryption of data in transit and at rest</li>
              <li>Access controls and authentication</li>
              <li>Regular security testing and monitoring</li>
              <li>Incident response procedures</li>
              <li>Data backup and disaster recovery</li>
              <li>Employee security training</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">4.4 Sub-processors</h3>
            <p className="text-gray-700 mb-4">
              The Data Controller provides general authorization for CivicQ to engage sub-processors.
              Current sub-processors include:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Cloud hosting providers (AWS, Google Cloud, Azure)</li>
              <li>Analytics services (Google Analytics)</li>
              <li>Email service providers</li>
              <li>Video hosting and CDN services</li>
            </ul>
            <p className="text-gray-700 mb-4">
              CivicQ will notify the Data Controller of any intended changes concerning the
              addition or replacement of sub-processors at least 30 days in advance, giving the
              Data Controller the opportunity to object.
            </p>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">4.5 Data Subject Rights</h3>
            <p className="text-gray-700 mb-4">
              CivicQ shall assist the Data Controller in fulfilling data subject requests:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Right of access</li>
              <li>Right to rectification</li>
              <li>Right to erasure</li>
              <li>Right to restriction of processing</li>
              <li>Right to data portability</li>
              <li>Right to object</li>
            </ul>

            <h3 className="text-xl font-semibold text-gray-800 mb-3">4.6 Data Breach Notification</h3>
            <p className="text-gray-700 mb-4">
              In the event of a personal data breach, CivicQ shall:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Notify the Data Controller without undue delay (within 72 hours)</li>
              <li>Provide details of the breach, affected data, and impact</li>
              <li>Describe measures taken or proposed to address the breach</li>
              <li>Assist in notifying supervisory authorities and data subjects if required</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">5. Data Controller Obligations</h2>
            <p className="text-gray-700 mb-4">
              The Data Controller shall:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Ensure it has a legal basis for processing personal data</li>
              <li>Provide clear privacy notices to data subjects</li>
              <li>Obtain necessary consents where required</li>
              <li>Respond to data subject requests within legal timeframes</li>
              <li>Ensure processing instructions comply with applicable laws</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">6. Audits and Compliance</h2>
            <p className="text-gray-700 mb-4">
              CivicQ shall make available to the Data Controller all information necessary to
              demonstrate compliance with this DPA and allow for and contribute to audits,
              including inspections, conducted by the Data Controller or another auditor
              mandated by the Data Controller.
            </p>
            <p className="text-gray-700 mb-4">
              Audit requests must be:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Made with at least 30 days' notice</li>
              <li>Conducted during business hours</li>
              <li>Subject to confidentiality obligations</li>
              <li>Limited to once per year unless required by a breach or regulatory request</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">7. International Data Transfers</h2>
            <p className="text-gray-700 mb-4">
              Personal data may be transferred to and processed in countries outside the European
              Economic Area (EEA). For such transfers, CivicQ ensures appropriate safeguards:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>EU Standard Contractual Clauses</li>
              <li>Adequacy decisions by the European Commission</li>
              <li>Other approved transfer mechanisms</li>
            </ul>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">8. Data Deletion and Return</h2>
            <p className="text-gray-700 mb-4">
              Upon termination of services, CivicQ shall, at the choice of the Data Controller:
            </p>
            <ul className="list-disc list-inside text-gray-700 mb-4 ml-4">
              <li>Delete all personal data and existing copies (within 90 days)</li>
              <li>Return all personal data to the Data Controller in a portable format</li>
            </ul>
            <p className="text-gray-700 mb-4">
              CivicQ may retain data only to the extent required by law, with continued compliance
              with confidentiality obligations.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">9. Liability and Indemnification</h2>
            <p className="text-gray-700 mb-4">
              Each party shall be liable for damages caused by its processing of personal data
              that violates this DPA or applicable data protection laws. Liability is subject to
              the limitations set forth in the Terms of Service.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">10. Term and Termination</h2>
            <p className="text-gray-700 mb-4">
              This DPA takes effect upon your acceptance of the Terms of Service and continues
              until termination of services. Provisions concerning data deletion, confidentiality,
              and liability survive termination.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">11. Governing Law and Jurisdiction</h2>
            <p className="text-gray-700 mb-4">
              This DPA is governed by the same law as the Terms of Service. For EU-based Data
              Controllers, EU data protection law shall apply to data protection matters.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">12. Contact Information</h2>
            <p className="text-gray-700 mb-4">
              For DPA-related inquiries:
            </p>
            <address className="text-gray-700 not-italic">
              <strong>Data Protection Officer</strong><br />
              CivicQ<br />
              Email: dpo@civicq.com<br />
              Address: [Your Legal Address]
            </address>
          </section>

          <div className="mt-12 p-6 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="text-lg font-semibold text-blue-900 mb-2">For Organizations</h3>
            <p className="text-blue-800">
              This DPA is designed to meet GDPR Article 28 requirements for organizational users
              who are Data Controllers. For individual users, the Privacy Policy governs our
              data handling practices.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default DataProcessingAgreementPage;
