import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { questionAPI, contestAPI } from '../services/api';
import { Question, QuestionSubmit } from '../types';

export const useQuestion = (questionId: number | undefined) => {
  return useQuery<Question>({
    queryKey: ['questions', questionId],
    queryFn: () => questionAPI.getById(questionId!),
    enabled: !!questionId,
  });
};

export const useContestQuestions = (
  contestId: number | undefined,
  options?: {
    status?: string;
    page?: number;
    page_size?: number;
  }
) => {
  return useQuery({
    queryKey: ['contests', contestId, 'questions', options],
    queryFn: () => contestAPI.getQuestions(contestId!, options),
    enabled: !!contestId,
  });
};

export const useCreateQuestion = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: QuestionSubmit) => questionAPI.create(data),
    onSuccess: (newQuestion) => {
      // Invalidate contest questions to refetch
      queryClient.invalidateQueries({
        queryKey: ['contests', newQuestion.contest_id, 'questions'],
      });
    },
  });
};

export const useUpdateQuestion = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<QuestionSubmit> }) =>
      questionAPI.update(id, data),
    onSuccess: (updatedQuestion) => {
      // Update cache for this specific question
      queryClient.setQueryData(['questions', updatedQuestion.id], updatedQuestion);
      // Invalidate contest questions
      queryClient.invalidateQueries({
        queryKey: ['contests', updatedQuestion.contest_id, 'questions'],
      });
    },
  });
};

export const useDeleteQuestion = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => questionAPI.delete(id),
    onSuccess: (_, _id) => {
      // Invalidate all question queries
      queryClient.invalidateQueries({ queryKey: ['questions'] });
      queryClient.invalidateQueries({ queryKey: ['contests'] });
    },
  });
};

export const useQuestionVideoAnswers = (questionId: number | undefined) => {
  return useQuery({
    queryKey: ['questions', questionId, 'answers'],
    queryFn: () => questionAPI.getVideoAnswers(questionId!),
    enabled: !!questionId,
  });
};
