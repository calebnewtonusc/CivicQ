# CivicQ - SEO & Accessibility Quick Implementation Guide

**Quick reference for developers implementing SEO and accessibility features**

---

## Quick Start Checklist

When creating a new page:

- [ ] Add SEOHelmet with title and description
- [ ] Use Layout component (includes skip links)
- [ ] Add structured data if applicable
- [ ] Use semantic HTML (not divs for everything)
- [ ] Add ARIA labels to interactive elements
- [ ] Ensure keyboard navigation works
- [ ] Test with tab key only
- [ ] Check color contrast
- [ ] Add to sitemap.xml if public page

---

## Common Patterns

### 1. Basic Page Setup

```tsx
import React from 'react';
import { Layout, SEOHelmet } from '../components';

const MyPage: React.FC = () => {
  return (
    <Layout>
      <SEOHelmet
        title="Page Title"
        description="Brief description for search engines"
        keywords={['relevant', 'keywords']}
      />

      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Page Title</h1>
        {/* Your content */}
      </div>
    </Layout>
  );
};

export default MyPage;
```

### 2. Candidate Profile Page (with Structured Data)

```tsx
import React from 'react';
import { Layout, SEOHelmet, StructuredData } from '../components';
import { generateCandidateSchema } from '../utils/seo';

const CandidateProfile: React.FC = () => {
  const candidate = /* ... fetch candidate data ... */;

  const schema = generateCandidateSchema({
    id: candidate.id,
    name: candidate.name,
    bio: candidate.bio,
    photo: candidate.photo,
    party: candidate.party
  });

  return (
    <Layout>
      <SEOHelmet
        title={candidate.name}
        description={`${candidate.name} - ${candidate.party} candidate for ${candidate.office}`}
        type="profile"
        image={candidate.photo}
      />
      <StructuredData data={schema} />

      {/* Page content */}
    </Layout>
  );
};
```

### 3. Accessible Form

```tsx
import React, { useState } from 'react';
import { generateFormFieldId, generateFormFieldAriaDescribedBy } from '../utils/accessibility';

const MyForm: React.FC = () => {
  const [errors, setErrors] = useState<Record<string, string>>({});

  const emailId = generateFormFieldId('email');
  const passwordId = generateFormFieldId('password');

  return (
    <form onSubmit={handleSubmit}>
      <div className="mb-4">
        <label htmlFor={emailId} className="block text-sm font-medium mb-2">
          Email <span className="text-red-500" aria-label="required">*</span>
        </label>
        <input
          id={emailId}
          type="email"
          required
          aria-required="true"
          aria-invalid={!!errors.email}
          aria-describedby={generateFormFieldAriaDescribedBy(emailId, !!errors.email, true)}
          className="w-full px-3 py-2 border rounded"
        />
        {errors.email && (
          <p id={`${emailId}-error`} className="text-red-600 text-sm mt-1" role="alert">
            {errors.email}
          </p>
        )}
        <p id={`${emailId}-help`} className="text-gray-600 text-sm mt-1">
          We'll never share your email
        </p>
      </div>

      <button
        type="submit"
        className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        aria-label="Submit registration form"
      >
        Submit
      </button>
    </form>
  );
};
```

### 4. Accessible Button/Link

```tsx
// Button
<button
  onClick={handleClick}
  aria-label="Delete question"
  className="p-2 hover:bg-gray-100 rounded"
>
  <TrashIcon className="w-5 h-5" aria-hidden="true" />
</button>

// External Link
import { generateExternalLinkProps } from '../utils/accessibility';

<a
  href="https://example.com"
  {...generateExternalLinkProps('https://example.com')}
  className="text-blue-600 hover:underline"
>
  External Link
</a>

// Internal Link
<Link
  to="/somewhere"
  className="text-blue-600 hover:underline"
  aria-label="Navigate to somewhere"
>
  Go Somewhere
</Link>
```

### 5. Accessible Modal

```tsx
import React, { useEffect, useRef } from 'react';
import { trapFocus, handleKeyboardNavigation } from '../utils/accessibility';

const Modal: React.FC<{ isOpen: boolean; onClose: () => void }> = ({ isOpen, onClose, children }) => {
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen && modalRef.current) {
      const cleanup = trapFocus(modalRef.current);
      modalRef.current.focus();
      return cleanup;
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        ref={modalRef}
        className="bg-white rounded-lg p-6 max-w-md w-full"
        tabIndex={-1}
        onKeyDown={(e) => handleKeyboardNavigation(e, {
          ESCAPE: onClose
        })}
      >
        <h2 id="modal-title" className="text-xl font-bold mb-4">
          Modal Title
        </h2>

        {children}

        <button
          onClick={onClose}
          className="mt-4 px-4 py-2 bg-gray-200 rounded"
          aria-label="Close modal"
        >
          Close
        </button>
      </div>
    </div>
  );
};
```

### 6. Accessible Dropdown/Menu

```tsx
import React, { useState } from 'react';
import { handleKeyboardNavigation } from '../utils/accessibility';

const Dropdown: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const items = ['Option 1', 'Option 2', 'Option 3'];

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        className="px-4 py-2 border rounded"
      >
        {items[selectedIndex]}
      </button>

      {isOpen && (
        <ul
          role="listbox"
          aria-activedescendant={`option-${selectedIndex}`}
          className="absolute mt-1 bg-white border rounded shadow-lg"
          onKeyDown={(e) => handleKeyboardNavigation(e, {
            ARROW_DOWN: () => setSelectedIndex((i) => Math.min(i + 1, items.length - 1)),
            ARROW_UP: () => setSelectedIndex((i) => Math.max(i - 1, 0)),
            ENTER: () => setIsOpen(false),
            ESCAPE: () => setIsOpen(false)
          })}
        >
          {items.map((item, index) => (
            <li
              key={index}
              id={`option-${index}`}
              role="option"
              aria-selected={index === selectedIndex}
              onClick={() => {
                setSelectedIndex(index);
                setIsOpen(false);
              }}
              className={`px-4 py-2 cursor-pointer ${
                index === selectedIndex ? 'bg-blue-100' : 'hover:bg-gray-100'
              }`}
            >
              {item}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
```

### 7. Accessible Image

```tsx
import { generateImageAlt } from '../utils/accessibility';

// Candidate photo
<img
  src={candidate.photo}
  alt={generateImageAlt('candidate', candidate.name)}
  className="w-24 h-24 rounded-full object-cover"
/>

// Decorative icon (empty alt)
<img
  src="/icon.svg"
  alt=""
  aria-hidden="true"
  className="w-6 h-6"
/>

// Logo
<img
  src="/logo.png"
  alt={generateImageAlt('logo', 'CivicQ')}
  className="h-8"
/>
```

### 8. Accessible Loading State

```tsx
import { announceToScreenReader } from '../utils/accessibility';
import { LoadingSpinner } from '../components';

const MyComponent: React.FC = () => {
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (loading) {
      announceToScreenReader('Loading content', 'polite');
    }
  }, [loading]);

  if (loading) {
    return (
      <div role="status" aria-live="polite" aria-busy="true">
        <LoadingSpinner />
        <span className="sr-only">Loading...</span>
      </div>
    );
  }

  return <div>{/* content */}</div>;
};
```

---

## Utility Functions Quick Reference

### SEO Utils (`/frontend/src/utils/seo.ts`)

```tsx
// Generate page title
generateTitle('My Page') // "My Page | CivicQ"

// Generate canonical URL
generateCanonicalURL('/ballot') // "https://civicq.com/ballot"

// Generate OpenGraph tags
generateOpenGraphTags(config) // Returns object of OG tags

// Generate Twitter Card tags
generateTwitterCardTags(config) // Returns object of Twitter tags

// Generate schemas
generateOrganizationSchema()
generateCandidateSchema(candidate)
generateQuestionSchema(question)
generateWebPageSchema({ name, description, url, breadcrumbs })
```

### Accessibility Utils (`/frontend/src/utils/accessibility.ts`)

```tsx
// Color contrast
checkColorContrast('#1E40AF', '#FFFFFF') // { ratio: 8.59, isAA: true, ... }
validateCivicQColorPalette() // Validate entire color scheme

// ARIA helpers
generateAriaLabel('Button', 'context') // "Button - context"

// Keyboard navigation
handleKeyboardNavigation(event, {
  ENTER: handleEnter,
  ESCAPE: handleEscape,
  ARROW_UP: handleUp,
  ARROW_DOWN: handleDown
})

// Focus management
trapFocus(element) // Returns cleanup function

// Screen reader
announceToScreenReader('Message', 'polite' | 'assertive')

// Form helpers
generateFormFieldId('email', 'prefix') // "prefix-email"
generateFormFieldAriaDescribedBy(fieldId, hasError, hasHelp)

// Image alt text
generateImageAlt('candidate', 'John Doe') // "Photo of John Doe"

// External links
generateExternalLinkProps(url) // { target, rel, aria-label }

// Motion preference
prefersReducedMotion() // boolean

// Audit
auditPageAccessibility() // Returns array of issues
```

---

## CSS Classes for Accessibility

### Screen Reader Only

```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border-width: 0;
}
```

### Focus Visible

```css
/* Use for custom focus indicators */
.focus-visible:focus {
  outline: 3px solid #FBBF24;
  outline-offset: 2px;
}
```

---

## Testing Commands

```bash
# Run accessibility audit in browser console
import { auditPageAccessibility } from './utils/accessibility';
console.table(auditPageAccessibility());

# Validate color contrast
import { validateCivicQColorPalette } from './utils/accessibility';
console.log(validateCivicQColorPalette());

# Test keyboard navigation
# 1. Unplug mouse
# 2. Use Tab, Shift+Tab, Enter, Space, Arrows, Escape
# 3. All functionality should work

# Test screen reader
# macOS: VoiceOver (Cmd+F5)
# Windows: NVDA (free) or JAWS
# Chrome: ChromeVox extension
```

---

## Common Mistakes to Avoid

1. **Don't** use `<div>` for buttons - use `<button>`
2. **Don't** forget alt text on images
3. **Don't** use click handlers on non-interactive elements
4. **Don't** rely on color alone to convey information
5. **Don't** skip heading levels (h1 → h3)
6. **Don't** use placeholder as label
7. **Don't** forget to test keyboard navigation
8. **Don't** use low contrast colors
9. **Don't** forget aria-label on icon buttons
10. **Don't** trap focus without a way out

---

## Resources

- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [Google Lighthouse](https://developers.google.com/web/tools/lighthouse)

---

**Remember**: Accessibility is not optional—it's a legal requirement and the right thing to do.
