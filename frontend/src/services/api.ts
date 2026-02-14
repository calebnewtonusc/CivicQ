import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  User,
  Ballot,
  Contest,
  Candidate,
  Question,
  VideoAnswer,
  Vote,
  LoginCredentials,
  RegisterData,
  AuthResponse,
  QuestionSubmit,
  PaginatedResponse,
  ApiError,
  QuestionAnalysisResponse,
  DuplicateCheckResult,
  SuggestedQuestionsResponse,
  LLMHealthResponse,
} from '../types';
import {
  getMockBallots,
  getMockBallotById,
  getMockContestById,
  getMockContestCandidates,
  getMockContestQuestions,
  getMockQuestionById,
  getMockQuestionVideoAnswers,
  getMockCandidateById,
  getMockCandidateVideoAnswers,
} from '../data/mockData';
import { setDemoMode, getDemoMode } from './demoMode';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling with comprehensive error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    // Network error (no response from server)
    if (!error.response) {
      if (error.code === 'ERR_NETWORK') {
        console.warn('Network error: Backend may be unavailable, falling back to demo mode where applicable');
      } else if (error.code === 'ECONNABORTED') {
        console.error('Request timeout:', error.message);
      } else {
        console.error('Request failed:', error.message);
      }
      return Promise.reject(error);
    }

    // Handle specific HTTP status codes
    const status = error.response.status;

    if (status === 401) {
      // Token expired or invalid
      console.warn('Authentication failed: Token expired or invalid');
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');

      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    } else if (status === 403) {
      console.error('Access forbidden: Insufficient permissions');
    } else if (status === 404) {
      console.warn('Resource not found:', error.config?.url);
    } else if (status === 422) {
      console.error('Validation error:', error.response.data);
    } else if (status >= 500) {
      console.error('Server error:', error.response.data);
    }

    return Promise.reject(error);
  }
);

// Helper function to handle API errors
export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<ApiError>;
    return axiosError.response?.data?.detail || 'An error occurred';
  }
  return 'An unexpected error occurred';
};

// Authentication API
export const authAPI = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const response = await apiClient.post<AuthResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
    return response.data;
  },

  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/auth/register', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
  },
};

// Ballot API
export const ballotAPI = {
  getAll: async (params?: {
    city_id?: string;
    is_published?: boolean;
  }): Promise<Ballot[]> => {
    try {
      const response = await apiClient.get<Ballot[]>('/ballots', { params });
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
        setDemoMode(true);
        return getMockBallots(params);
      }
      throw error;
    }
  },

  getById: async (id: number): Promise<Ballot> => {
    try {
      const response = await apiClient.get<Ballot>(`/ballots/${id}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
        setDemoMode(true);
        const ballot = getMockBallotById(id);
        if (!ballot) throw new Error('Ballot not found');
        return ballot;
      }
      throw error;
    }
  },

  getByCityAndDate: async (cityId: string, electionDate: string): Promise<Ballot> => {
    try {
      const response = await apiClient.get<Ballot>(`/ballots/city/${cityId}/date/${electionDate}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
        setDemoMode(true);
        const ballots = getMockBallots({ city_id: cityId });
        if (ballots.length === 0) throw new Error('Ballot not found');
        return ballots[0];
      }
      throw error;
    }
  },
};

// Contest API
export const contestAPI = {
  getById: async (id: number): Promise<Contest> => {
    try {
      const response = await apiClient.get<Contest>(`/contests/${id}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
        setDemoMode(true);
        const contest = getMockContestById(id);
        if (!contest) throw new Error('Contest not found');
        return contest;
      }
      throw error;
    }
  },

  getByBallot: async (ballotId: number): Promise<Contest[]> => {
    try {
      const response = await apiClient.get<Contest[]>(`/ballots/${ballotId}/contests`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
        setDemoMode(true);
        const ballot = getMockBallotById(ballotId);
        return ballot?.contests || [];
      }
      throw error;
    }
  },

  getCandidates: async (contestId: number): Promise<Candidate[]> => {
    try {
      const response = await apiClient.get<Candidate[]>(`/contests/${contestId}/candidates`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
        setDemoMode(true);
        return getMockContestCandidates(contestId);
      }
      throw error;
    }
  },

  getQuestions: async (
    contestId: number,
    params?: {
      status?: string;
      page?: number;
      page_size?: number;
    }
  ): Promise<PaginatedResponse<Question>> => {
    try {
      const response = await apiClient.get<PaginatedResponse<Question>>(
        `/contests/${contestId}/questions`,
        { params }
      );
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
        setDemoMode(true);
        return getMockContestQuestions(contestId, params);
      }
      throw error;
    }
  },
};

// Candidate API
export const candidateAPI = {
  getById: async (id: number): Promise<Candidate> => {
    try {
      const response = await apiClient.get<Candidate>(`/candidates/${id}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
        setDemoMode(true);
        const candidate = getMockCandidateById(id);
        if (!candidate) throw new Error('Candidate not found');
        return candidate;
      }
      throw error;
    }
  },

  getVideoAnswers: async (candidateId: number): Promise<VideoAnswer[]> => {
    try {
      const response = await apiClient.get<VideoAnswer[]>(`/candidates/${candidateId}/answers`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
        setDemoMode(true);
        return getMockCandidateVideoAnswers(candidateId);
      }
      throw error;
    }
  },

  update: async (id: number, data: Partial<Candidate>): Promise<Candidate> => {
    if (getDemoMode()) {
      throw new Error('Cannot update candidates in demo mode');
    }
    const response = await apiClient.put<Candidate>(`/candidates/${id}`, data);
    return response.data;
  },
};

// Question API
export const questionAPI = {
  getById: async (id: number): Promise<Question> => {
    try {
      const response = await apiClient.get<Question>(`/questions/${id}`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
        setDemoMode(true);
        const question = getMockQuestionById(id);
        if (!question) throw new Error('Question not found');
        return question;
      }
      throw error;
    }
  },

  create: async (data: QuestionSubmit): Promise<Question> => {
    if (getDemoMode()) {
      throw new Error('Cannot create questions in demo mode. This is a read-only demo.');
    }
    const response = await apiClient.post<Question>('/questions', data);
    return response.data;
  },

  update: async (id: number, data: Partial<QuestionSubmit>): Promise<Question> => {
    if (getDemoMode()) {
      throw new Error('Cannot update questions in demo mode');
    }
    const response = await apiClient.put<Question>(`/questions/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    if (getDemoMode()) {
      throw new Error('Cannot delete questions in demo mode');
    }
    await apiClient.delete(`/questions/${id}`);
  },

  getVideoAnswers: async (questionId: number): Promise<VideoAnswer[]> => {
    try {
      const response = await apiClient.get<VideoAnswer[]>(`/questions/${questionId}/answers`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && (!error.response || error.code === 'ERR_NETWORK')) {
        setDemoMode(true);
        return getMockQuestionVideoAnswers(questionId);
      }
      throw error;
    }
  },
};

// Vote API
export const voteAPI = {
  upvote: async (questionId: number): Promise<Vote> => {
    if (getDemoMode()) {
      // Simulate client-side voting in demo mode
      const mockVote: Vote = {
        id: Math.floor(Math.random() * 10000),
        user_id: 1,
        question_id: questionId,
        value: 1,
        weight: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      localStorage.setItem(`demo_vote_${questionId}`, JSON.stringify(mockVote));
      return mockVote;
    }
    const response = await apiClient.post<Vote>(`/questions/${questionId}/vote`, {
      value: 1,
    });
    return response.data;
  },

  downvote: async (questionId: number): Promise<Vote> => {
    if (getDemoMode()) {
      // Simulate client-side voting in demo mode
      const mockVote: Vote = {
        id: Math.floor(Math.random() * 10000),
        user_id: 1,
        question_id: questionId,
        value: -1,
        weight: 1,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      localStorage.setItem(`demo_vote_${questionId}`, JSON.stringify(mockVote));
      return mockVote;
    }
    const response = await apiClient.post<Vote>(`/questions/${questionId}/vote`, {
      value: -1,
    });
    return response.data;
  },

  removeVote: async (questionId: number): Promise<void> => {
    if (getDemoMode()) {
      localStorage.removeItem(`demo_vote_${questionId}`);
      return;
    }
    await apiClient.delete(`/questions/${questionId}/vote`);
  },

  getMyVote: async (questionId: number): Promise<Vote | null> => {
    if (getDemoMode()) {
      const stored = localStorage.getItem(`demo_vote_${questionId}`);
      return stored ? JSON.parse(stored) : null;
    }
    try {
      const response = await apiClient.get<Vote>(`/questions/${questionId}/vote`);
      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  },
};

// Video Answer API
export const videoAnswerAPI = {
  getById: async (id: number): Promise<VideoAnswer> => {
    const response = await apiClient.get<VideoAnswer>(`/answers/${id}`);
    return response.data;
  },

  create: async (data: FormData): Promise<VideoAnswer> => {
    const response = await apiClient.post<VideoAnswer>('/answers', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000, // 2 minutes for video upload
    });
    return response.data;
  },

  update: async (id: number, data: Partial<VideoAnswer>): Promise<VideoAnswer> => {
    const response = await apiClient.put<VideoAnswer>(`/answers/${id}`, data);
    return response.data;
  },

  publish: async (id: number): Promise<VideoAnswer> => {
    const response = await apiClient.post<VideoAnswer>(`/answers/${id}/publish`);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/answers/${id}`);
  },
};

// LLM/AI Features API
export const llmAPI = {
  analyzeQuestion: async (
    questionText: string,
    contestId: number
  ): Promise<QuestionAnalysisResponse> => {
    try {
      const response = await apiClient.post<QuestionAnalysisResponse>(
        '/llm/analyze-question',
        {
          question_text: questionText,
          contest_id: contestId,
        }
      );
      return response.data;
    } catch (error) {
      // Return mock data if backend is unavailable
      if (axios.isAxiosError(error) && !error.response) {
        return {
          analysis: {
            quality_score: 75,
            is_appropriate: true,
            category: 'General',
            issues: [],
            suggestions: [],
          },
          success: false,
          message: 'AI analysis unavailable in demo mode',
        };
      }
      throw error;
    }
  },

  checkDuplicate: async (
    questionText: string,
    contestId: number
  ): Promise<DuplicateCheckResult> => {
    try {
      const response = await apiClient.post<DuplicateCheckResult>(
        '/llm/check-duplicate',
        {
          question_text: questionText,
          contest_id: contestId,
        }
      );
      return response.data;
    } catch (error) {
      // Return mock data if backend is unavailable
      if (axios.isAxiosError(error) && !error.response) {
        return {
          is_duplicate: false,
          similarity_score: 0,
          explanation: 'Duplicate check unavailable in demo mode',
          success: false,
        };
      }
      throw error;
    }
  },

  getSuggestedQuestions: async (
    contestId: number,
    numSuggestions: number = 5
  ): Promise<SuggestedQuestionsResponse> => {
    try {
      const response = await apiClient.get<SuggestedQuestionsResponse>(
        `/llm/suggested-questions/${contestId}?num_suggestions=${numSuggestions}`
      );
      return response.data;
    } catch (error) {
      // Return mock data if backend is unavailable
      if (axios.isAxiosError(error) && !error.response) {
        return {
          questions: [
            'What is your plan to address housing affordability in our city?',
            'How will you work to improve public safety while maintaining community trust?',
            'What are your priorities for infrastructure improvements?',
          ],
          success: false,
        };
      }
      throw error;
    }
  },

  checkHealth: async (): Promise<LLMHealthResponse> => {
    try {
      const response = await apiClient.get<LLMHealthResponse>('/llm/health');
      return response.data;
    } catch (error) {
      return {
        status: 'unhealthy',
        error: 'LLM service unavailable',
      };
    }
  },
};

// Export the main client for custom requests
export default apiClient;
