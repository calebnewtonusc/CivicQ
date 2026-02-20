import React from 'react';

interface SkeletonProps {
  className?: string;
}

const Skeleton: React.FC<SkeletonProps> = ({ className = '' }) => (
  <div className={`skeleton ${className}`} aria-hidden="true" />
);

export const QuestionCardSkeleton: React.FC = () => (
  <div className="bg-white rounded-2xl border border-gray-100 shadow-card p-6 animate-fade-in">
    <div className="flex items-start gap-4">
      {/* Vote column */}
      <div className="flex flex-col items-center gap-2 pt-1">
        <Skeleton className="w-8 h-8 rounded-lg" />
        <Skeleton className="w-6 h-4 rounded" />
        <Skeleton className="w-8 h-8 rounded-lg" />
      </div>
      {/* Content */}
      <div className="flex-1 space-y-3">
        <Skeleton className="h-6 w-3/4 rounded-lg" />
        <Skeleton className="h-4 w-full rounded" />
        <Skeleton className="h-4 w-5/6 rounded" />
        <div className="flex gap-2 pt-1">
          <Skeleton className="h-5 w-16 rounded-full" />
          <Skeleton className="h-5 w-20 rounded-full" />
          <Skeleton className="h-5 w-14 rounded-full" />
        </div>
        <div className="flex items-center gap-4 pt-2">
          <Skeleton className="h-4 w-16 rounded" />
          <Skeleton className="h-4 w-20 rounded" />
        </div>
      </div>
    </div>
  </div>
);

export const ContestCardSkeleton: React.FC = () => (
  <div className="bg-white rounded-2xl border border-gray-100 shadow-card p-6 animate-fade-in">
    <div className="flex items-start justify-between">
      <div className="flex-1 space-y-3">
        <Skeleton className="h-5 w-16 rounded-full" />
        <Skeleton className="h-7 w-2/3 rounded-lg" />
        <Skeleton className="h-4 w-1/3 rounded" />
        <Skeleton className="h-4 w-full rounded" />
        <Skeleton className="h-4 w-4/5 rounded" />
        <div className="flex gap-4 pt-1">
          <Skeleton className="h-4 w-24 rounded" />
          <Skeleton className="h-4 w-20 rounded" />
        </div>
      </div>
      <Skeleton className="w-6 h-6 rounded ml-4 flex-shrink-0" />
    </div>
  </div>
);

export const BallotHeaderSkeleton: React.FC = () => (
  <div className="bg-white rounded-2xl border border-gray-100 shadow-card p-8 animate-fade-in">
    <div className="flex items-start gap-4">
      <Skeleton className="w-14 h-14 rounded-xl flex-shrink-0" />
      <div className="flex-1 space-y-3">
        <Skeleton className="h-4 w-20 rounded" />
        <Skeleton className="h-10 w-1/2 rounded-lg" />
        <Skeleton className="h-5 w-40 rounded" />
      </div>
    </div>
  </div>
);

export const CandidateCardSkeleton: React.FC = () => (
  <div className="bg-white rounded-2xl border border-gray-100 shadow-card overflow-hidden animate-fade-in">
    <Skeleton className="aspect-video w-full rounded-none" />
    <div className="p-4 space-y-2">
      <Skeleton className="h-5 w-3/4 rounded-lg" />
      <Skeleton className="h-4 w-1/2 rounded" />
    </div>
  </div>
);

export const ProfileSkeleton: React.FC = () => (
  <div className="animate-fade-in">
    <div className="relative rounded-2xl overflow-hidden mb-8">
      <Skeleton className="h-32 w-full rounded-none" />
      <div className="px-8 pb-8">
        <div className="flex items-end gap-6 -mt-16">
          <Skeleton className="w-40 h-40 rounded-full flex-shrink-0 border-4 border-white" />
          <div className="flex-1 pb-4 space-y-3">
            <Skeleton className="h-10 w-1/2 rounded-lg" />
            <div className="flex gap-2">
              <Skeleton className="h-7 w-20 rounded-full" />
              <Skeleton className="h-7 w-28 rounded-full" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default Skeleton;
