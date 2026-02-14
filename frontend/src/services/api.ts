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
} from '../types';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

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
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      localStorage.removeItem('user');
      window.location.href = '/login';
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
    const response = await apiClient.get<Ballot[]>('/ballots', { params });
    return response.data;
  },

  getById: async (id: number): Promise<Ballot> => {
    const response = await apiClient.get<Ballot>(`/ballots/${id}`);
    return response.data;
  },

  getByCityAndDate: async (cityId: string, electionDate: string): Promise<Ballot> => {
    const response = await apiClient.get<Ballot>(`/ballots/city/${cityId}/date/${electionDate}`);
    return response.data;
  },
};

// Contest API
export const contestAPI = {
  getById: async (id: number): Promise<Contest> => {
    const response = await apiClient.get<Contest>(`/contests/${id}`);
    return response.data;
  },

  getByBallot: async (ballotId: number): Promise<Contest[]> => {
    const response = await apiClient.get<Contest[]>(`/ballots/${ballotId}/contests`);
    return response.data;
  },

  getCandidates: async (contestId: number): Promise<Candidate[]> => {
    const response = await apiClient.get<Candidate[]>(`/contests/${contestId}/candidates`);
    return response.data;
  },

  getQuestions: async (
    contestId: number,
    params?: {
      status?: string;
      page?: number;
      page_size?: number;
    }
  ): Promise<PaginatedResponse<Question>> => {
    const response = await apiClient.get<PaginatedResponse<Question>>(
      `/contests/${contestId}/questions`,
      { params }
    );
    return response.data;
  },
};

// Candidate API
export const candidateAPI = {
  getById: async (id: number): Promise<Candidate> => {
    const response = await apiClient.get<Candidate>(`/candidates/${id}`);
    return response.data;
  },

  getVideoAnswers: async (candidateId: number): Promise<VideoAnswer[]> => {
    const response = await apiClient.get<VideoAnswer[]>(`/candidates/${candidateId}/answers`);
    return response.data;
  },

  update: async (id: number, data: Partial<Candidate>): Promise<Candidate> => {
    const response = await apiClient.put<Candidate>(`/candidates/${id}`, data);
    return response.data;
  },
};

// Question API
export const questionAPI = {
  getById: async (id: number): Promise<Question> => {
    const response = await apiClient.get<Question>(`/questions/${id}`);
    return response.data;
  },

  create: async (data: QuestionSubmit): Promise<Question> => {
    const response = await apiClient.post<Question>('/questions', data);
    return response.data;
  },

  update: async (id: number, data: Partial<QuestionSubmit>): Promise<Question> => {
    const response = await apiClient.put<Question>(`/questions/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<void> => {
    await apiClient.delete(`/questions/${id}`);
  },

  getVideoAnswers: async (questionId: number): Promise<VideoAnswer[]> => {
    const response = await apiClient.get<VideoAnswer[]>(`/questions/${questionId}/answers`);
    return response.data;
  },
};

// Vote API
export const voteAPI = {
  upvote: async (questionId: number): Promise<Vote> => {
    const response = await apiClient.post<Vote>(`/questions/${questionId}/vote`, {
      value: 1,
    });
    return response.data;
  },

  downvote: async (questionId: number): Promise<Vote> => {
    const response = await apiClient.post<Vote>(`/questions/${questionId}/vote`, {
      value: -1,
    });
    return response.data;
  },

  removeVote: async (questionId: number): Promise<void> => {
    await apiClient.delete(`/questions/${questionId}/vote`);
  },

  getMyVote: async (questionId: number): Promise<Vote | null> => {
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

// Export the main client for custom requests
export default apiClient;
