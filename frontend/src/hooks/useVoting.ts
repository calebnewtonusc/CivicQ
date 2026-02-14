import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { voteAPI } from '../services/api';
import { Vote } from '../types';

export const useVote = (questionId: number | undefined) => {
  const queryClient = useQueryClient();

  // Get user's current vote for this question
  const { data: currentVote, isLoading } = useQuery<Vote | null>({
    queryKey: ['votes', questionId],
    queryFn: () => voteAPI.getMyVote(questionId!),
    enabled: !!questionId,
  });

  // Upvote mutation
  const upvoteMutation = useMutation({
    mutationFn: (qId: number) => voteAPI.upvote(qId),
    onSuccess: (newVote) => {
      queryClient.setQueryData(['votes', newVote.question_id], newVote);
      queryClient.invalidateQueries({ queryKey: ['questions', newVote.question_id] });
      queryClient.invalidateQueries({ queryKey: ['contests'] });
    },
  });

  // Downvote mutation
  const downvoteMutation = useMutation({
    mutationFn: (qId: number) => voteAPI.downvote(qId),
    onSuccess: (newVote) => {
      queryClient.setQueryData(['votes', newVote.question_id], newVote);
      queryClient.invalidateQueries({ queryKey: ['questions', newVote.question_id] });
      queryClient.invalidateQueries({ queryKey: ['contests'] });
    },
  });

  // Remove vote mutation
  const removeVoteMutation = useMutation({
    mutationFn: (qId: number) => voteAPI.removeVote(qId),
    onSuccess: (_, qId) => {
      queryClient.setQueryData(['votes', qId], null);
      queryClient.invalidateQueries({ queryKey: ['questions', qId] });
      queryClient.invalidateQueries({ queryKey: ['contests'] });
    },
  });

  // Helper function to toggle vote
  const toggleVote = (questionId: number, newValue: 1 | -1) => {
    if (!questionId) return;

    if (currentVote?.value === newValue) {
      // Clicking same vote - remove it
      removeVoteMutation.mutate(questionId);
    } else if (newValue === 1) {
      upvoteMutation.mutate(questionId);
    } else {
      downvoteMutation.mutate(questionId);
    }
  };

  return {
    currentVote,
    isLoading,
    upvote: (qId: number) => toggleVote(qId, 1),
    downvote: (qId: number) => toggleVote(qId, -1),
    removeVote: removeVoteMutation.mutate,
    isVoting:
      upvoteMutation.isPending ||
      downvoteMutation.isPending ||
      removeVoteMutation.isPending,
  };
};
