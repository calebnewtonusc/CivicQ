import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { candidateAPI, videoAnswerAPI } from '../services/api';
import { Candidate } from '../types';

export const useCandidate = (candidateId: number | undefined) => {
  return useQuery({
    queryKey: ['candidates', candidateId],
    queryFn: () => candidateAPI.getById(candidateId!),
    enabled: !!candidateId,
  });
};

export const useCandidateVideoAnswers = (candidateId: number | undefined) => {
  return useQuery({
    queryKey: ['candidates', candidateId, 'answers'],
    queryFn: () => candidateAPI.getVideoAnswers(candidateId!),
    enabled: !!candidateId,
  });
};

export const useUpdateCandidate = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<Candidate> }) =>
      candidateAPI.update(id, data),
    onSuccess: (updatedCandidate) => {
      queryClient.setQueryData(['candidates', updatedCandidate.id], updatedCandidate);
      queryClient.invalidateQueries({ queryKey: ['contests', updatedCandidate.contest_id] });
    },
  });
};

export const useVideoAnswer = (answerId: number | undefined) => {
  return useQuery({
    queryKey: ['answers', answerId],
    queryFn: () => videoAnswerAPI.getById(answerId!),
    enabled: !!answerId,
  });
};

export const useCreateVideoAnswer = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (formData: FormData) => videoAnswerAPI.create(formData),
    onSuccess: (newAnswer) => {
      queryClient.invalidateQueries({
        queryKey: ['candidates', newAnswer.candidate_id, 'answers'],
      });
      queryClient.invalidateQueries({
        queryKey: ['questions', newAnswer.question_id, 'answers'],
      });
    },
  });
};

export const usePublishVideoAnswer = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (answerId: number) => videoAnswerAPI.publish(answerId),
    onSuccess: (publishedAnswer) => {
      queryClient.setQueryData(['answers', publishedAnswer.id], publishedAnswer);
      queryClient.invalidateQueries({
        queryKey: ['candidates', publishedAnswer.candidate_id, 'answers'],
      });
      queryClient.invalidateQueries({
        queryKey: ['questions', publishedAnswer.question_id, 'answers'],
      });
    },
  });
};
