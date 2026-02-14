/**
 * Validation and defensive programming utilities
 * Provides type-safe null checks and array validation
 */

// Original validations
export const isValidEmail = (email: string): boolean => {
  if (!email || typeof email !== 'string') return false;
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidPassword = (password: string): boolean => {
  if (!password || password.length < 8) return false;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumber = /[0-9]/.test(password);
  return hasUpperCase && hasLowerCase && hasNumber;
};

export const getPasswordStrengthMessage = (password: string): string => {
  if (!password || password.length === 0) return '';
  if (password.length < 8) return 'Password must be at least 8 characters';
  if (!/[A-Z]/.test(password)) return 'Password must contain an uppercase letter';
  if (!/[a-z]/.test(password)) return 'Password must contain a lowercase letter';
  if (!/[0-9]/.test(password)) return 'Password must contain a number';
  return 'Password is strong';
};

export const isValidPhone = (phone: string): boolean => {
  if (!phone || typeof phone !== 'string') return false;
  const phoneRegex = /^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$/;
  return phoneRegex.test(phone.replace(/\s/g, ''));
};

export const isValidUrl = (url: string): boolean => {
  if (!url || typeof url !== 'string') return false;
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

export const isValidQuestion = (text: string): { valid: boolean; message?: string } => {
  if (!text || typeof text !== 'string') {
    return { valid: false, message: 'Question cannot be empty' };
  }
  const trimmed = text.trim();
  if (trimmed.length < 10) {
    return { valid: false, message: 'Question must be at least 10 characters' };
  }
  if (trimmed.length > 500) {
    return { valid: false, message: 'Question must be less than 500 characters' };
  }
  if (!trimmed.endsWith('?')) {
    return { valid: false, message: 'Question should end with a question mark' };
  }
  return { valid: true };
};

export const sanitizeHtml = (html: string): string => {
  if (!html || typeof html !== 'string') return '';
  const div = document.createElement('div');
  div.textContent = html;
  return div.innerHTML;
};

export const isValidFileSize = (file: File | null, maxSizeMB: number): boolean => {
  if (!file) return false;
  const maxSizeBytes = maxSizeMB * 1024 * 1024;
  return file.size <= maxSizeBytes;
};

export const isValidFileType = (file: File | null, allowedTypes: string[]): boolean => {
  if (!file || !Array.isArray(allowedTypes)) return false;
  return allowedTypes.includes(file.type);
};

// NEW: Defensive programming utilities
export function isNonEmptyArray<T>(value: unknown): value is T[] {
  return Array.isArray(value) && value.length > 0;
}

export function safeArray<T>(value: T[] | null | undefined): T[] {
  return Array.isArray(value) ? value : [];
}

export function safeString(value: string | null | undefined, defaultValue = ''): string {
  return typeof value === 'string' ? value : defaultValue;
}

export function safeNumber(value: number | null | undefined, defaultValue = 0): number {
  return typeof value === 'number' && !isNaN(value) ? value : defaultValue;
}

export function isDefined<T>(value: T | null | undefined): value is T {
  return value !== null && value !== undefined;
}

export function filterNullish<T>(array: (T | null | undefined)[]): T[] {
  return array.filter((item): item is T => item !== null && item !== undefined);
}

export function safeParseJSON<T>(json: string, defaultValue: T): T {
  if (!json || typeof json !== 'string') return defaultValue;
  try {
    return JSON.parse(json) as T;
  } catch (error) {
    console.error('Failed to parse JSON:', error);
    return defaultValue;
  }
}

export function truncate(str: string, maxLength: number, ellipsis = '...'): string {
  if (!str || typeof str !== 'string') return '';
  if (str.length <= maxLength) return str;
  return str.slice(0, maxLength - ellipsis.length) + ellipsis;
}
