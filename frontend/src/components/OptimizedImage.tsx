/**
 * Optimized Image Component
 *
 * Features:
 * - Lazy loading
 * - WebP format with fallback
 * - Responsive images
 * - Loading placeholders
 * - Error handling
 */

import React, { useState, useEffect, useRef } from 'react';

interface OptimizedImageProps {
  src: string;
  alt: string;
  className?: string;
  width?: number;
  height?: number;
  sizes?: string;
  priority?: boolean;
  onLoad?: () => void;
  onError?: () => void;
}

export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src,
  alt,
  className = '',
  width,
  height,
  sizes = '100vw',
  priority = false,
  onLoad,
  onError,
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [hasError, setHasError] = useState(false);
  const [isInView, setIsInView] = useState(priority);
  const imgRef = useRef<HTMLImageElement>(null);

  // Intersection Observer for lazy loading
  useEffect(() => {
    if (priority || !imgRef.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setIsInView(true);
            observer.disconnect();
          }
        });
      },
      {
        rootMargin: '50px', // Load 50px before image comes into view
      }
    );

    observer.observe(imgRef.current);

    return () => {
      observer.disconnect();
    };
  }, [priority]);

  // Generate WebP source URL
  const getWebPUrl = (url: string): string => {
    const ext = url.split('.').pop()?.toLowerCase();
    if (ext && ['jpg', 'jpeg', 'png'].includes(ext)) {
      return url.replace(/\.(jpg|jpeg|png)$/i, '.webp');
    }
    return url;
  };

  // Generate srcset for responsive images
  const getSrcSet = (url: string): string => {
    const widths = [320, 640, 768, 1024, 1280, 1920];
    return widths
      .map((w) => `${url}?w=${w} ${w}w`)
      .join(', ');
  };

  const handleLoad = () => {
    setIsLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    setHasError(true);
    onError?.();
  };

  const imageClasses = [
    className,
    'transition-opacity duration-300',
    isLoaded ? 'opacity-100' : 'opacity-0',
  ].filter(Boolean).join(' ');

  return (
    <div
      ref={imgRef}
      className={`relative ${className}`}
      style={{ width, height }}
    >
      {/* Loading placeholder */}
      {!isLoaded && !hasError && (
        <div
          className="absolute inset-0 bg-gray-200 animate-pulse"
          style={{ width, height }}
        />
      )}

      {/* Error fallback */}
      {hasError && (
        <div
          className="absolute inset-0 bg-gray-100 flex items-center justify-center text-gray-400"
          style={{ width, height }}
        >
          <svg
            className="w-12 h-12"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
      )}

      {/* Image with WebP support */}
      {isInView && !hasError && (
        <picture>
          {/* WebP format */}
          <source
            type="image/webp"
            srcSet={getSrcSet(getWebPUrl(src))}
            sizes={sizes}
          />

          {/* Fallback format */}
          <source
            srcSet={getSrcSet(src)}
            sizes={sizes}
          />

          {/* Fallback img tag */}
          <img
            src={src}
            alt={alt}
            className={imageClasses}
            width={width}
            height={height}
            loading={priority ? 'eager' : 'lazy'}
            decoding="async"
            onLoad={handleLoad}
            onError={handleError}
          />
        </picture>
      )}
    </div>
  );
};

export default OptimizedImage;
