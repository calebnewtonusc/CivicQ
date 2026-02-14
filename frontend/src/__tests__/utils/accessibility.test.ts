/**
 * Accessibility utility tests
 */

import {
  generateAriaLabel,
  formatScreenReaderText,
  checkColorContrast,
  validateKeyboardNavigation,
} from '../../utils/accessibility';

describe('Accessibility Utilities', () => {
  describe('generateAriaLabel', () => {
    it('generates descriptive aria labels for questions', () => {
      const question = {
        id: 1,
        text: 'What is your housing policy?',
        voteCount: 42,
        answerCount: 3,
      };

      const label = generateAriaLabel('question', question);

      expect(label).toContain('Question:');
      expect(label).toContain('42 votes');
      expect(label).toContain('3 answers');
    });

    it('generates labels for video players', () => {
      const answer = {
        candidateName: 'Jane Candidate',
        questionText: 'Housing policy',
        duration: 90,
      };

      const label = generateAriaLabel('video', answer);

      expect(label).toContain('Jane Candidate');
      expect(label).toContain('Housing policy');
      expect(label).toContain('1 minute 30 seconds');
    });

    it('handles missing data gracefully', () => {
      const incomplete = { id: 1 };

      const label = generateAriaLabel('question', incomplete);

      expect(label).toBeTruthy();
      expect(label).not.toContain('undefined');
    });
  });

  describe('formatScreenReaderText', () => {
    it('formats numbers with appropriate units', () => {
      expect(formatScreenReaderText('voteCount', 1)).toBe('1 vote');
      expect(formatScreenReaderText('voteCount', 5)).toBe('5 votes');
    });

    it('formats time durations', () => {
      expect(formatScreenReaderText('duration', 45)).toBe('45 seconds');
      expect(formatScreenReaderText('duration', 90)).toBe('1 minute 30 seconds');
      expect(formatScreenReaderText('duration', 125)).toBe('2 minutes 5 seconds');
    });

    it('formats dates in readable format', () => {
      const date = new Date('2024-02-14T10:30:00Z');
      const formatted = formatScreenReaderText('date', date);

      expect(formatted).toContain('February');
      expect(formatted).toContain('2024');
    });
  });

  describe('checkColorContrast', () => {
    it('validates WCAG AA contrast ratio', () => {
      // White text on dark blue background (good contrast)
      expect(checkColorContrast('#FFFFFF', '#1E3A8A')).toBeGreaterThan(4.5);

      // Light gray on white (poor contrast)
      expect(checkColorContrast('#CCCCCC', '#FFFFFF')).toBeLessThan(4.5);
    });

    it('calculates correct contrast ratio', () => {
      // Black on white should be maximum contrast (21:1)
      const contrast = checkColorContrast('#000000', '#FFFFFF');
      expect(contrast).toBeCloseTo(21, 0);
    });

    it('handles invalid color formats', () => {
      expect(() => checkColorContrast('invalid', '#FFFFFF')).toThrow();
    });
  });

  describe('validateKeyboardNavigation', () => {
    it('identifies keyboard-accessible elements', () => {
      const button = document.createElement('button');
      button.textContent = 'Click me';

      expect(validateKeyboardNavigation(button)).toBe(true);
    });

    it('flags non-keyboard-accessible elements', () => {
      const div = document.createElement('div');
      div.onclick = () => {};

      expect(validateKeyboardNavigation(div)).toBe(false);
    });

    it('validates tabIndex correctly', () => {
      const link = document.createElement('a');
      link.href = '#';
      link.tabIndex = 0;

      expect(validateKeyboardNavigation(link)).toBe(true);

      link.tabIndex = -1;
      expect(validateKeyboardNavigation(link)).toBe(false);
    });
  });
});
