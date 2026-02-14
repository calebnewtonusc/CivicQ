/**
 * Accessibility Utility Functions
 * WCAG 2.1 AA Compliance helpers
 */

/**
 * Color Contrast Checker
 * WCAG 2.1 AA requires:
 * - Normal text: 4.5:1 contrast ratio
 * - Large text (18pt+): 3:1 contrast ratio
 */

export interface ColorContrastResult {
  ratio: number;
  isAA: boolean;
  isAAA: boolean;
  isLargeTextAA: boolean;
  isLargeTextAAA: boolean;
}

/**
 * Convert hex color to RGB
 */
const hexToRGB = (hex: string): { r: number; g: number; b: number } => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : { r: 0, g: 0, b: 0 };
};

/**
 * Calculate relative luminance
 */
const getLuminance = (r: number, g: number, b: number): number => {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
};

/**
 * Calculate contrast ratio between two colors
 */
export const getContrastRatio = (color1: string, color2: string): number => {
  const rgb1 = hexToRGB(color1);
  const rgb2 = hexToRGB(color2);

  const lum1 = getLuminance(rgb1.r, rgb1.g, rgb1.b);
  const lum2 = getLuminance(rgb2.r, rgb2.g, rgb2.b);

  const lighter = Math.max(lum1, lum2);
  const darker = Math.min(lum1, lum2);

  return (lighter + 0.05) / (darker + 0.05);
};

/**
 * Check if color contrast meets WCAG standards
 */
export const checkColorContrast = (
  foreground: string,
  background: string
): ColorContrastResult => {
  const ratio = getContrastRatio(foreground, background);

  return {
    ratio,
    isAA: ratio >= 4.5,
    isAAA: ratio >= 7,
    isLargeTextAA: ratio >= 3,
    isLargeTextAAA: ratio >= 4.5,
  };
};

/**
 * CivicQ Color Palette Contrast Validation
 */
export const validateCivicQColorPalette = () => {
  const palette = {
    primary: '#1E40AF', // blue-800
    secondary: '#6B7280', // gray-500
    background: '#FFFFFF',
    text: '#111827', // gray-900
    textLight: '#6B7280', // gray-500
  };

  const results = {
    primaryOnWhite: checkColorContrast(palette.primary, palette.background),
    textOnWhite: checkColorContrast(palette.text, palette.background),
    textLightOnWhite: checkColorContrast(palette.textLight, palette.background),
    whiteOnPrimary: checkColorContrast(palette.background, palette.primary),
  };

  return results;
};

/**
 * ARIA Label Helpers
 */

export const generateAriaLabel = (element: string, context?: string): string => {
  if (context) {
    return `${element} - ${context}`;
  }
  return element;
};

/**
 * Keyboard Navigation Helpers
 */

export const KEYBOARD_KEYS = {
  ENTER: 'Enter',
  SPACE: ' ',
  ESCAPE: 'Escape',
  TAB: 'Tab',
  ARROW_UP: 'ArrowUp',
  ARROW_DOWN: 'ArrowDown',
  ARROW_LEFT: 'ArrowLeft',
  ARROW_RIGHT: 'ArrowRight',
  HOME: 'Home',
  END: 'End',
} as const;

export const handleKeyboardNavigation = (
  event: React.KeyboardEvent,
  handlers: Partial<Record<keyof typeof KEYBOARD_KEYS, () => void>>
) => {
  const key = event.key;

  Object.entries(KEYBOARD_KEYS).forEach(([name, value]) => {
    if (key === value && handlers[name as keyof typeof KEYBOARD_KEYS]) {
      event.preventDefault();
      handlers[name as keyof typeof KEYBOARD_KEYS]?.();
    }
  });
};

/**
 * Focus Management
 */

export const trapFocus = (element: HTMLElement) => {
  const focusableElements = element.querySelectorAll<HTMLElement>(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );

  const firstFocusable = focusableElements[0];
  const lastFocusable = focusableElements[focusableElements.length - 1];

  const handleTabKey = (e: KeyboardEvent) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      if (document.activeElement === firstFocusable) {
        e.preventDefault();
        lastFocusable.focus();
      }
    } else {
      if (document.activeElement === lastFocusable) {
        e.preventDefault();
        firstFocusable.focus();
      }
    }
  };

  element.addEventListener('keydown', handleTabKey);

  return () => {
    element.removeEventListener('keydown', handleTabKey);
  };
};

/**
 * Screen Reader Announcements
 */

export const announceToScreenReader = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
};

/**
 * Skip Link Generator
 */

export interface SkipLink {
  target: string;
  label: string;
}

export const generateSkipLinks = (): SkipLink[] => {
  return [
    { target: '#main-content', label: 'Skip to main content' },
    { target: '#navigation', label: 'Skip to navigation' },
    { target: '#footer', label: 'Skip to footer' },
  ];
};

/**
 * Form Accessibility Helpers
 */

export const generateFormFieldId = (name: string, prefix?: string): string => {
  const id = name.toLowerCase().replace(/\s+/g, '-');
  return prefix ? `${prefix}-${id}` : id;
};

export const generateFormFieldAriaDescribedBy = (
  fieldId: string,
  hasError?: boolean,
  hasHelp?: boolean
): string | undefined => {
  const ids: string[] = [];

  if (hasError) ids.push(`${fieldId}-error`);
  if (hasHelp) ids.push(`${fieldId}-help`);

  return ids.length > 0 ? ids.join(' ') : undefined;
};

/**
 * Semantic HTML Helpers
 */

export const getLandmarkRole = (
  element: 'header' | 'nav' | 'main' | 'footer' | 'aside' | 'section'
): string => {
  const roles: Record<string, string> = {
    header: 'banner',
    nav: 'navigation',
    main: 'main',
    footer: 'contentinfo',
    aside: 'complementary',
    section: 'region',
  };

  return roles[element] || '';
};

/**
 * Image Accessibility
 */

export const generateImageAlt = (
  type: 'candidate' | 'logo' | 'icon',
  name?: string
): string => {
  switch (type) {
    case 'candidate':
      return name ? `Photo of ${name}` : 'Candidate photo';
    case 'logo':
      return name ? `${name} logo` : 'Logo';
    case 'icon':
      return ''; // Decorative icons should have empty alt
    default:
      return '';
  }
};

/**
 * Link Accessibility
 */

export const shouldOpenInNewTab = (url: string): boolean => {
  const currentDomain = window.location.hostname;
  try {
    const urlDomain = new URL(url).hostname;
    return urlDomain !== currentDomain;
  } catch {
    return false;
  }
};

export const generateExternalLinkProps = (url: string) => {
  if (shouldOpenInNewTab(url)) {
    return {
      target: '_blank',
      rel: 'noopener noreferrer',
      'aria-label': 'Opens in new tab',
    };
  }
  return {};
};

/**
 * Table Accessibility
 */

export const generateTableHeaders = (columns: string[]) => {
  return columns.map((col) => ({
    id: col.toLowerCase().replace(/\s+/g, '-'),
    label: col,
  }));
};

/**
 * Motion Preferences
 */

export const prefersReducedMotion = (): boolean => {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
};

/**
 * Accessibility Audit
 */

export interface AccessibilityIssue {
  severity: 'error' | 'warning' | 'notice';
  message: string;
  element?: string;
}

export const auditPageAccessibility = (): AccessibilityIssue[] => {
  const issues: AccessibilityIssue[] = [];

  // Check for page title
  if (!document.title || document.title.trim() === '') {
    issues.push({
      severity: 'error',
      message: 'Page is missing a title',
    });
  }

  // Check for main landmark
  const mainLandmark = document.querySelector('main, [role="main"]');
  if (!mainLandmark) {
    issues.push({
      severity: 'error',
      message: 'Page is missing a main landmark',
    });
  }

  // Check images for alt text
  const images = document.querySelectorAll('img');
  images.forEach((img, index) => {
    if (!img.hasAttribute('alt')) {
      issues.push({
        severity: 'error',
        message: `Image at index ${index} is missing alt attribute`,
        element: `img[src="${img.src}"]`,
      });
    }
  });

  // Check form inputs for labels
  const inputs = document.querySelectorAll('input, select, textarea');
  inputs.forEach((input, index) => {
    const id = input.id;
    if (id) {
      const label = document.querySelector(`label[for="${id}"]`);
      if (!label && !input.getAttribute('aria-label')) {
        issues.push({
          severity: 'error',
          message: `Form input at index ${index} is missing a label`,
          element: `#${id}`,
        });
      }
    }
  });

  // Check for heading hierarchy
  const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'));
  if (headings.length > 0) {
    const h1Count = headings.filter((h) => h.tagName === 'H1').length;
    if (h1Count === 0) {
      issues.push({
        severity: 'warning',
        message: 'Page should have exactly one H1 heading',
      });
    } else if (h1Count > 1) {
      issues.push({
        severity: 'warning',
        message: 'Page has multiple H1 headings',
      });
    }
  }

  return issues;
};
