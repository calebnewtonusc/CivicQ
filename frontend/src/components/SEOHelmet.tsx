import React from 'react';
import { Helmet } from 'react-helmet-async';
import {
  SEOConfig,
  defaultSEO,
  generateTitle,
  generateCanonicalURL,
  generateOpenGraphTags,
  generateTwitterCardTags,
  generateRobotsTag,
} from '../utils/seo';

interface SEOHelmetProps extends Partial<SEOConfig> {
  children?: React.ReactNode;
}

/**
 * SEO Helmet Component
 * Manages all meta tags, OpenGraph, Twitter Cards, and structured data
 */
const SEOHelmet: React.FC<SEOHelmetProps> = ({
  title,
  description,
  canonical,
  keywords,
  author,
  image,
  type,
  publishedTime,
  modifiedTime,
  section,
  tags,
  twitterCard,
  noindex,
  nofollow,
  children,
}) => {
  const seoConfig: SEOConfig = {
    title: title || defaultSEO.title,
    description: description || defaultSEO.description,
    canonical: canonical,
    keywords: keywords || defaultSEO.keywords,
    author: author,
    image: image,
    type: type || defaultSEO.type,
    publishedTime,
    modifiedTime,
    section,
    tags,
    twitterCard: twitterCard || defaultSEO.twitterCard,
    noindex,
    nofollow,
  };

  const pageTitle = generateTitle(title);
  const canonicalURL = canonical || generateCanonicalURL(window.location.pathname);
  const ogTags = generateOpenGraphTags({ ...seoConfig, canonical: canonicalURL });
  const twitterTags = generateTwitterCardTags(seoConfig);
  const robotsTag = generateRobotsTag(seoConfig);

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{pageTitle}</title>
      <meta name="description" content={seoConfig.description} />
      {seoConfig.keywords && seoConfig.keywords.length > 0 && (
        <meta name="keywords" content={seoConfig.keywords.join(', ')} />
      )}
      {seoConfig.author && <meta name="author" content={seoConfig.author} />}
      <meta name="robots" content={robotsTag} />
      <link rel="canonical" href={canonicalURL} />

      {/* OpenGraph Tags */}
      {Object.entries(ogTags).map(([property, content]) => (
        <meta key={property} property={property} content={content} />
      ))}

      {/* Twitter Card Tags */}
      {Object.entries(twitterTags).map(([name, content]) => (
        <meta key={name} name={name} content={content} />
      ))}

      {/* Additional Meta Tags */}
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
      <meta httpEquiv="X-UA-Compatible" content="IE=edge" />
      <meta name="theme-color" content="#1E40AF" />

      {/* Language */}
      <html lang="en" />

      {/* Additional elements passed as children */}
      {children}
    </Helmet>
  );
};

export default SEOHelmet;
