import React from 'react';
import { generateSkipLinks } from '../utils/accessibility';

/**
 * Skip Links Component
 * Provides keyboard navigation shortcuts for accessibility
 * WCAG 2.1 AA Requirement: Bypass Blocks (2.4.1)
 */
const SkipLinks: React.FC = () => {
  const skipLinks = generateSkipLinks();

  return (
    <div className="skip-links">
      {skipLinks.map((link) => (
        <a
          key={link.target}
          href={link.target}
          className="skip-link"
          aria-label={link.label}
        >
          {link.label}
        </a>
      ))}
      <style>{`
        .skip-links {
          position: relative;
        }

        .skip-link {
          position: absolute;
          top: -40px;
          left: 0;
          background: #1E40AF;
          color: white;
          padding: 8px 16px;
          text-decoration: none;
          border-radius: 0 0 4px 0;
          font-weight: 600;
          z-index: 100;
          transition: top 0.2s ease-in-out;
        }

        .skip-link:focus {
          top: 0;
          outline: 3px solid #FBBF24;
          outline-offset: 2px;
        }

        .skip-link:hover {
          background: #1E3A8A;
        }
      `}</style>
    </div>
  );
};

export default SkipLinks;
