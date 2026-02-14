/**
 * SEO Utility Functions
 * Handles dynamic meta tags, OpenGraph, Twitter Cards, and structured data
 */

export interface SEOConfig {
  title: string;
  description: string;
  canonical?: string;
  keywords?: string[];
  author?: string;
  image?: string;
  type?: 'website' | 'article' | 'profile';
  publishedTime?: string;
  modifiedTime?: string;
  section?: string;
  tags?: string[];
  twitterCard?: 'summary' | 'summary_large_image' | 'app' | 'player';
  noindex?: boolean;
  nofollow?: boolean;
}

export const defaultSEO: SEOConfig = {
  title: 'CivicQ - Civic Engagement for Local Elections',
  description:
    'CivicQ connects voters with local candidates through video Q&A. Make informed decisions in local elections by watching candidates answer community questions.',
  type: 'website',
  twitterCard: 'summary_large_image',
  keywords: [
    'local elections',
    'civic engagement',
    'voter information',
    'candidate Q&A',
    'democracy',
    'local government',
    'community engagement',
  ],
};

/**
 * Generate full page title with site name
 */
export const generateTitle = (pageTitle?: string): string => {
  if (!pageTitle) return defaultSEO.title;
  return `${pageTitle} | CivicQ`;
};

/**
 * Generate canonical URL
 */
export const generateCanonicalURL = (path: string): string => {
  const baseURL = process.env.REACT_APP_BASE_URL || 'https://civicq.com';
  return `${baseURL}${path}`;
};

/**
 * Generate meta tags for OpenGraph
 */
export const generateOpenGraphTags = (config: SEOConfig) => {
  const image = config.image || `${process.env.REACT_APP_BASE_URL || 'https://civicq.com'}/og-image.png`;

  return {
    'og:type': config.type || 'website',
    'og:title': config.title,
    'og:description': config.description,
    'og:image': image,
    'og:url': config.canonical || '',
    'og:site_name': 'CivicQ',
    ...(config.publishedTime && { 'article:published_time': config.publishedTime }),
    ...(config.modifiedTime && { 'article:modified_time': config.modifiedTime }),
    ...(config.section && { 'article:section': config.section }),
    ...(config.tags && config.tags.length > 0 && { 'article:tag': config.tags.join(', ') }),
  };
};

/**
 * Generate Twitter Card meta tags
 */
export const generateTwitterCardTags = (config: SEOConfig) => {
  const image = config.image || `${process.env.REACT_APP_BASE_URL || 'https://civicq.com'}/twitter-card.png`;

  return {
    'twitter:card': config.twitterCard || 'summary_large_image',
    'twitter:title': config.title,
    'twitter:description': config.description,
    'twitter:image': image,
    'twitter:site': '@CivicQ',
    'twitter:creator': config.author || '@CivicQ',
  };
};

/**
 * Generate robots meta tag
 */
export const generateRobotsTag = (config: SEOConfig): string => {
  const directives: string[] = [];

  if (config.noindex) directives.push('noindex');
  else directives.push('index');

  if (config.nofollow) directives.push('nofollow');
  else directives.push('follow');

  return directives.join(', ');
};

/**
 * Structured Data (JSON-LD) Generators
 */

export interface OrganizationSchema {
  '@context': string;
  '@type': string;
  name: string;
  description: string;
  url: string;
  logo: string;
  sameAs: string[];
  contactPoint: {
    '@type': string;
    contactType: string;
    email: string;
  };
}

export const generateOrganizationSchema = (): OrganizationSchema => {
  const baseURL = process.env.REACT_APP_BASE_URL || 'https://civicq.com';

  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: 'CivicQ',
    description: 'Civic engagement platform for local elections',
    url: baseURL,
    logo: `${baseURL}/logo.png`,
    sameAs: [
      'https://twitter.com/CivicQ',
      'https://facebook.com/CivicQ',
      'https://linkedin.com/company/civicq',
    ],
    contactPoint: {
      '@type': 'ContactPoint',
      contactType: 'Customer Service',
      email: 'support@civicq.com',
    },
  };
};

export interface PersonSchema {
  '@context': string;
  '@type': string;
  name: string;
  description?: string;
  image?: string;
  url: string;
  jobTitle?: string;
  affiliation?: {
    '@type': string;
    name: string;
  };
}

export const generateCandidateSchema = (candidate: {
  id: string;
  name: string;
  bio?: string;
  photo?: string;
  party?: string;
}): PersonSchema => {
  const baseURL = process.env.REACT_APP_BASE_URL || 'https://civicq.com';

  return {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name: candidate.name,
    description: candidate.bio,
    image: candidate.photo,
    url: `${baseURL}/candidate/${candidate.id}`,
    jobTitle: 'Political Candidate',
    ...(candidate.party && {
      affiliation: {
        '@type': 'Organization',
        name: candidate.party,
      },
    }),
  };
};

export interface QuestionSchema {
  '@context': string;
  '@type': string;
  name: string;
  text: string;
  answerCount: number;
  upvoteCount?: number;
  dateCreated: string;
  author?: {
    '@type': string;
    name: string;
  };
}

export const generateQuestionSchema = (question: {
  id: string;
  question: string;
  answers_count?: number;
  upvote_count?: number;
  created_at: string;
  author_name?: string;
}): QuestionSchema => {
  return {
    '@context': 'https://schema.org',
    '@type': 'Question',
    name: question.question,
    text: question.question,
    answerCount: question.answers_count || 0,
    upvoteCount: question.upvote_count || 0,
    dateCreated: question.created_at,
    ...(question.author_name && {
      author: {
        '@type': 'Person',
        name: question.author_name,
      },
    }),
  };
};

export interface WebPageSchema {
  '@context': string;
  '@type': string;
  name: string;
  description: string;
  url: string;
  breadcrumb?: {
    '@type': string;
    itemListElement: Array<{
      '@type': string;
      position: number;
      name: string;
      item: string;
    }>;
  };
}

export const generateWebPageSchema = (config: {
  name: string;
  description: string;
  url: string;
  breadcrumbs?: Array<{ name: string; url: string }>;
}): WebPageSchema => {
  const schema: WebPageSchema = {
    '@context': 'https://schema.org',
    '@type': 'WebPage',
    name: config.name,
    description: config.description,
    url: config.url,
  };

  if (config.breadcrumbs && config.breadcrumbs.length > 0) {
    schema.breadcrumb = {
      '@type': 'BreadcrumbList',
      itemListElement: config.breadcrumbs.map((crumb, index) => ({
        '@type': 'ListItem',
        position: index + 1,
        name: crumb.name,
        item: crumb.url,
      })),
    };
  }

  return schema;
};

/**
 * Sitemap generator helper
 */
export interface SitemapURL {
  loc: string;
  lastmod?: string;
  changefreq?: 'always' | 'hourly' | 'daily' | 'weekly' | 'monthly' | 'yearly' | 'never';
  priority?: number;
}

export const generateSitemapURLs = (): SitemapURL[] => {
  const baseURL = process.env.REACT_APP_BASE_URL || 'https://civicq.com';
  const now = new Date().toISOString();

  return [
    {
      loc: baseURL,
      lastmod: now,
      changefreq: 'daily',
      priority: 1.0,
    },
    {
      loc: `${baseURL}/ballot`,
      lastmod: now,
      changefreq: 'daily',
      priority: 0.9,
    },
    {
      loc: `${baseURL}/login`,
      lastmod: now,
      changefreq: 'monthly',
      priority: 0.5,
    },
    {
      loc: `${baseURL}/register`,
      lastmod: now,
      changefreq: 'monthly',
      priority: 0.5,
    },
    {
      loc: `${baseURL}/terms`,
      lastmod: now,
      changefreq: 'yearly',
      priority: 0.3,
    },
    {
      loc: `${baseURL}/privacy`,
      lastmod: now,
      changefreq: 'yearly',
      priority: 0.3,
    },
    {
      loc: `${baseURL}/accessibility`,
      lastmod: now,
      changefreq: 'yearly',
      priority: 0.3,
    },
    {
      loc: `${baseURL}/cookies`,
      lastmod: now,
      changefreq: 'yearly',
      priority: 0.3,
    },
  ];
};
