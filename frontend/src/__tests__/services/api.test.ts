/**
 * Unit tests for API service layer
 */

import { apiClient } from '../../services/api';
import { fetchQuestions, submitQuestion, voteOnQuestion } from '../../services/questionService';

// Mock fetch
global.fetch = jest.fn();

describe('API Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('fetchQuestions', () => {
    it('fetches top questions successfully', async () => {
      const mockQuestions = [
        { id: 1, text: 'Question 1', voteCount: 10 },
        { id: 2, text: 'Question 2', voteCount: 5 },
      ];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockQuestions,
      });

      const questions = await fetchQuestions();

      expect(questions).toEqual(mockQuestions);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/questions/top'),
        expect.any(Object)
      );
    });

    it('handles API errors gracefully', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      });

      await expect(fetchQuestions()).rejects.toThrow('Internal Server Error');
    });

    it('filters questions by contest ID', async () => {
      const mockQuestions = [{ id: 1, text: 'Question 1', contestId: 5 }];

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockQuestions,
      });

      await fetchQuestions({ contestId: 5 });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('contestId=5'),
        expect.any(Object)
      );
    });
  });

  describe('submitQuestion', () => {
    it('submits new question successfully', async () => {
      const newQuestion = {
        text: 'What is your climate policy?',
        issueTags: ['environment', 'climate'],
        contestId: 1,
      };

      const mockResponse = {
        id: 123,
        ...newQuestion,
        createdAt: '2024-02-01T00:00:00Z',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => mockResponse,
      });

      const result = await submitQuestion(newQuestion, 'fake-token');

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/questions'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            Authorization: 'Bearer fake-token',
          }),
          body: JSON.stringify(newQuestion),
        })
      );
    });

    it('requires authentication token', async () => {
      const newQuestion = {
        text: 'Question without auth',
        issueTags: ['test'],
        contestId: 1,
      };

      await expect(submitQuestion(newQuestion, '')).rejects.toThrow(
        /authentication required/i
      );
    });

    it('validates question text length', async () => {
      const shortQuestion = {
        text: 'Too short',
        issueTags: ['test'],
        contestId: 1,
      };

      await expect(submitQuestion(shortQuestion, 'token')).rejects.toThrow(
        /question too short/i
      );
    });
  });

  describe('voteOnQuestion', () => {
    it('submits upvote successfully', async () => {
      const mockResponse = {
        questionId: 1,
        voteCount: 43,
        userVote: 1,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await voteOnQuestion(1, 1, 'fake-token');

      expect(result.voteCount).toBe(43);
      expect(result.userVote).toBe(1);
    });

    it('submits downvote successfully', async () => {
      const mockResponse = {
        questionId: 1,
        voteCount: 41,
        userVote: -1,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      });

      const result = await voteOnQuestion(1, -1, 'fake-token');

      expect(result.voteCount).toBe(41);
      expect(result.userVote).toBe(-1);
    });

    it('handles unauthorized voting', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
      });

      await expect(voteOnQuestion(1, 1, '')).rejects.toThrow(/unauthorized/i);
    });

    it('validates vote value', async () => {
      await expect(voteOnQuestion(1, 2, 'token')).rejects.toThrow(
        /invalid vote value/i
      );
    });
  });

  describe('API client configuration', () => {
    it('includes base URL in requests', () => {
      expect(apiClient.defaults.baseURL).toContain('/api/v1');
    });

    it('sets appropriate headers', () => {
      expect(apiClient.defaults.headers['Content-Type']).toBe('application/json');
    });

    it('attaches auth token when available', () => {
      const token = 'test-token';
      apiClient.setAuthToken(token);

      expect(apiClient.defaults.headers.Authorization).toBe(`Bearer ${token}`);
    });
  });
});
