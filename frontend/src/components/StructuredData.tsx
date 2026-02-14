import React from 'react';
import { Helmet } from 'react-helmet-async';

interface StructuredDataProps {
  data: object | object[];
}

/**
 * Structured Data Component
 * Renders JSON-LD structured data for SEO
 */
const StructuredData: React.FC<StructuredDataProps> = ({ data }) => {
  const jsonLD = Array.isArray(data) ? data : [data];

  return (
    <Helmet>
      {jsonLD.map((item, index) => (
        <script key={index} type="application/ld+json">
          {JSON.stringify(item)}
        </script>
      ))}
    </Helmet>
  );
};

export default StructuredData;
