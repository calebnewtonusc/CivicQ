/**
 * React Query Client Configuration
 *
 * Optimized configuration for caching, prefetching, and background updates.
 */

import { QueryClient, QueryCache, MutationCache } from '@tanstack/react-query';

// Error handler for query errors
const handleQueryError = (error: unknown) => {
  console.error('Query error:', error);
  // You can integrate with error tracking service here (e.g., Sentry)
};

// Error handler for mutation errors
const handleMutationError = (error: unknown) => {
  console.error('Mutation error:', error);
  // You can show toast notifications here
};

// Create optimized query client
export const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: handleQueryError,
  }),
  mutationCache: new MutationCache({
    onError: handleMutationError,
  }),
  defaultOptions: {
    queries: {
      // Caching
      staleTime: 5 * 60 * 1000, // 5 minutes - data is fresh for 5 min
      gcTime: 10 * 60 * 1000, // 10 minutes - cache garbage collection time (formerly cacheTime)

      // Refetching
      refetchOnWindowFocus: true, // Refetch when window regains focus
      refetchOnReconnect: true, // Refetch when reconnecting
      refetchOnMount: true, // Refetch on component mount

      // Retries
      retry: 2, // Retry failed requests 2 times
      retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),

      // Network mode
      networkMode: 'online', // Only fetch when online

      // Error handling
      throwOnError: false, // Don't throw errors, handle them gracefully
    },
    mutations: {
      // Retry failed mutations once
      retry: 1,
      retryDelay: 1000,

      // Error handling
      throwOnError: false,
    },
  },
});

// Query key factory for consistent key generation
export const queryKeys = {
  // Ballots
  ballots: {
    all: ['ballots'] as const,
    byCity: (citySlug: string) => ['ballots', citySlug] as const,
    detail: (ballotId: number) => ['ballots', ballotId] as const,
  },

  // Contests
  contests: {
    all: ['contests'] as const,
    byBallot: (ballotId: number) => ['contests', 'ballot', ballotId] as const,
    detail: (contestId: number) => ['contests', contestId] as const,
  },

  // Questions
  questions: {
    all: ['questions'] as const,
    list: (filters: {
      contestId?: number;
      page?: number;
      sort?: string;
      limit?: number;
    }) => ['questions', 'list', filters] as const,
    detail: (questionId: number) => ['questions', questionId] as const,
    trending: (contestId?: number) => ['questions', 'trending', contestId] as const,
  },

  // Candidates
  candidates: {
    all: ['candidates'] as const,
    byContest: (contestId: number) => ['candidates', 'contest', contestId] as const,
    detail: (candidateId: number) => ['candidates', candidateId] as const,
    responses: (candidateId: number, page?: number) =>
      ['candidates', candidateId, 'responses', page] as const,
  },

  // Cities
  cities: {
    all: ['cities'] as const,
    detail: (citySlug: string) => ['cities', citySlug] as const,
  },

  // Videos
  videos: {
    all: ['videos'] as const,
    detail: (videoId: number) => ['videos', videoId] as const,
    stream: (videoId: number, quality?: string) =>
      ['videos', videoId, 'stream', quality] as const,
  },

  // User
  user: {
    profile: ['user', 'profile'] as const,
    votes: ['user', 'votes'] as const,
    questions: ['user', 'questions'] as const,
  },

  // Analytics
  analytics: {
    overview: (citySlug: string, date: string) =>
      ['analytics', citySlug, date] as const,
    contestStats: (contestId: number) =>
      ['analytics', 'contest', contestId] as const,
  },
};

// Prefetch utilities
export const prefetchUtils = {
  // Prefetch ballot data
  prefetchBallot: async (citySlug: string) => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.ballots.byCity(citySlug),
      queryFn: async () => {
        const response = await fetch(`/api/ballots/${citySlug}`);
        if (!response.ok) throw new Error('Failed to fetch ballot');
        return response.json();
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
    });
  },

  // Prefetch trending questions
  prefetchTrendingQuestions: async (contestId?: number) => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.questions.trending(contestId),
      queryFn: async () => {
        const url = contestId
          ? `/api/questions/trending?contest_id=${contestId}`
          : '/api/questions/trending';
        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch trending questions');
        return response.json();
      },
      staleTime: 15 * 60 * 1000, // 15 minutes
    });
  },

  // Prefetch candidate profiles for a contest
  prefetchCandidates: async (contestId: number) => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.candidates.byContest(contestId),
      queryFn: async () => {
        const response = await fetch(`/api/contests/${contestId}/candidates`);
        if (!response.ok) throw new Error('Failed to fetch candidates');
        return response.json();
      },
      staleTime: 30 * 60 * 1000, // 30 minutes
    });
  },

  // Prefetch city data
  prefetchCity: async (citySlug: string) => {
    await queryClient.prefetchQuery({
      queryKey: queryKeys.cities.detail(citySlug),
      queryFn: async () => {
        const response = await fetch(`/api/cities/${citySlug}`);
        if (!response.ok) throw new Error('Failed to fetch city');
        return response.json();
      },
      staleTime: 24 * 60 * 60 * 1000, // 24 hours
    });
  },
};

// Optimistic update utilities
export const optimisticUpdates = {
  // Optimistic vote
  voteOnQuestion: (questionId: number, voteType: 'upvote' | 'downvote') => {
    const queryKey = queryKeys.questions.detail(questionId);

    queryClient.setQueryData(queryKey, (oldData: any) => {
      if (!oldData) return oldData;

      const voteChange = voteType === 'upvote' ? 1 : -1;

      return {
        ...oldData,
        vote_count: (oldData.vote_count || 0) + voteChange,
        user_vote: voteType,
      };
    });
  },

  // Rollback vote on error
  rollbackVote: (questionId: number) => {
    queryClient.invalidateQueries({
      queryKey: queryKeys.questions.detail(questionId),
    });
  },

  // Optimistic question submission
  addQuestion: (contestId: number, questionData: any) => {
    const listQueryKey = queryKeys.questions.list({ contestId, page: 1 });

    queryClient.setQueryData(listQueryKey, (oldData: any) => {
      if (!oldData) return oldData;

      return {
        ...oldData,
        results: [
          {
            ...questionData,
            id: `temp-${Date.now()}`,
            created_at: new Date().toISOString(),
            vote_count: 0,
            status: 'pending',
          },
          ...oldData.results,
        ],
      };
    });
  },
};

// Cache invalidation utilities
export const invalidateCache = {
  // Invalidate all question caches
  questions: () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.questions.all });
  },

  // Invalidate specific contest questions
  contestQuestions: (contestId: number) => {
    queryClient.invalidateQueries({
      queryKey: queryKeys.questions.list({ contestId }),
    });
  },

  // Invalidate candidate data
  candidate: (candidateId: number) => {
    queryClient.invalidateQueries({
      queryKey: queryKeys.candidates.detail(candidateId),
    });
  },

  // Invalidate all caches (use sparingly)
  all: () => {
    queryClient.invalidateQueries();
  },
};

// Background refetch configuration
export const enableBackgroundRefetch = () => {
  // Refetch trending questions every 5 minutes
  setInterval(() => {
    queryClient.invalidateQueries({
      queryKey: ['questions', 'trending'],
    });
  }, 5 * 60 * 1000);

  // Refetch user data every 10 minutes
  setInterval(() => {
    queryClient.invalidateQueries({
      queryKey: queryKeys.user.profile,
    });
  }, 10 * 60 * 1000);
};

export default queryClient;
