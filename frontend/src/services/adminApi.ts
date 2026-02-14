import apiClient from './api';
import {
  AdminStats,
  ModerationQueueItem,
  UserActivity,
  AnalyticsData,
  UserModerationAction,
  BulkOperationResult,
  ElectionConfig,
  CitySettings,
  Question,
  Report,
  AuditLog,
  PaginatedResponse,
} from '../types';

/**
 * Admin API Service
 *
 * Handles all admin panel API calls including:
 * - Dashboard statistics
 * - Question moderation
 * - User management
 * - Content moderation
 * - Analytics
 * - City configuration
 */

// Dashboard API
export const adminDashboardAPI = {
  getStats: async (cityId?: string): Promise<AdminStats> => {
    const params = cityId ? { city_id: cityId } : {};
    const response = await apiClient.get<AdminStats>('/admin/stats', { params });
    return response.data;
  },

  getAlerts: async (): Promise<Array<{ id: number; type: string; message: string; severity: string; created_at: string }>> => {
    const response = await apiClient.get('/admin/alerts');
    return response.data;
  },

  getRecentActivity: async (limit: number = 10): Promise<AuditLog[]> => {
    const response = await apiClient.get<AuditLog[]>('/admin/activity', {
      params: { limit },
    });
    return response.data;
  },
};

// Question Moderation API
export const questionModerationAPI = {
  getQueue: async (params?: {
    status?: string;
    page?: number;
    page_size?: number;
    priority?: string;
  }): Promise<PaginatedResponse<ModerationQueueItem>> => {
    const response = await apiClient.get<PaginatedResponse<ModerationQueueItem>>(
      '/admin/moderation/queue',
      { params }
    );
    return response.data;
  },

  getPendingQuestions: async (params?: {
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Question>> => {
    const response = await apiClient.get<PaginatedResponse<Question>>(
      '/admin/questions/pending',
      { params }
    );
    return response.data;
  },

  approveQuestion: async (questionId: number, notes?: string): Promise<Question> => {
    const response = await apiClient.post<Question>(
      `/admin/questions/${questionId}/approve`,
      { notes }
    );
    return response.data;
  },

  rejectQuestion: async (questionId: number, reason: string, notes?: string): Promise<void> => {
    await apiClient.post(`/admin/questions/${questionId}/reject`, {
      reason,
      notes,
    });
  },

  mergeQuestions: async (sourceIds: number[], targetId: number, notes?: string): Promise<Question> => {
    const response = await apiClient.post<Question>('/admin/questions/merge', {
      source_ids: sourceIds,
      target_id: targetId,
      notes,
    });
    return response.data;
  },

  bulkApprove: async (questionIds: number[]): Promise<BulkOperationResult> => {
    const response = await apiClient.post<BulkOperationResult>(
      '/admin/questions/bulk-approve',
      { question_ids: questionIds }
    );
    return response.data;
  },

  bulkReject: async (questionIds: number[], reason: string): Promise<BulkOperationResult> => {
    const response = await apiClient.post<BulkOperationResult>(
      '/admin/questions/bulk-reject',
      {
        question_ids: questionIds,
        reason,
      }
    );
    return response.data;
  },

  findDuplicates: async (questionId: number): Promise<Question[]> => {
    const response = await apiClient.get<Question[]>(
      `/admin/questions/${questionId}/duplicates`
    );
    return response.data;
  },
};

// User Management API
export const userManagementAPI = {
  getUsers: async (params?: {
    role?: string;
    status?: string;
    city_id?: string;
    page?: number;
    page_size?: number;
    search?: string;
  }): Promise<PaginatedResponse<UserActivity>> => {
    const response = await apiClient.get<PaginatedResponse<UserActivity>>(
      '/admin/users',
      { params }
    );
    return response.data;
  },

  getUserActivity: async (userId: number): Promise<UserActivity> => {
    const response = await apiClient.get<UserActivity>(`/admin/users/${userId}/activity`);
    return response.data;
  },

  warnUser: async (userId: number, reason: string, notes?: string): Promise<void> => {
    await apiClient.post(`/admin/users/${userId}/warn`, {
      reason,
      notes,
    });
  },

  suspendUser: async (userId: number, durationDays: number, reason: string, notes?: string): Promise<void> => {
    await apiClient.post(`/admin/users/${userId}/suspend`, {
      duration_days: durationDays,
      reason,
      notes,
    });
  },

  banUser: async (userId: number, reason: string, notes?: string): Promise<void> => {
    await apiClient.post(`/admin/users/${userId}/ban`, {
      reason,
      notes,
    });
  },

  restoreUser: async (userId: number, notes?: string): Promise<void> => {
    await apiClient.post(`/admin/users/${userId}/restore`, { notes });
  },

  bulkAction: async (action: UserModerationAction): Promise<BulkOperationResult> => {
    const response = await apiClient.post<BulkOperationResult>(
      '/admin/users/bulk-action',
      action
    );
    return response.data;
  },
};

// Content Moderation API
export const contentModerationAPI = {
  getReports: async (params?: {
    status?: string;
    target_type?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<Report>> => {
    const response = await apiClient.get<PaginatedResponse<Report>>(
      '/admin/reports',
      { params }
    );
    return response.data;
  },

  getReport: async (reportId: number): Promise<Report> => {
    const response = await apiClient.get<Report>(`/admin/reports/${reportId}`);
    return response.data;
  },

  resolveReport: async (reportId: number, action: string, notes?: string): Promise<void> => {
    await apiClient.post(`/admin/reports/${reportId}/resolve`, {
      action,
      notes,
    });
  },

  dismissReport: async (reportId: number, reason?: string): Promise<void> => {
    await apiClient.post(`/admin/reports/${reportId}/dismiss`, { reason });
  },

  flagContent: async (targetType: string, targetId: number, reason: string): Promise<void> => {
    await apiClient.post('/admin/content/flag', {
      target_type: targetType,
      target_id: targetId,
      reason,
    });
  },

  removeContent: async (targetType: string, targetId: number, reason: string): Promise<void> => {
    await apiClient.post('/admin/content/remove', {
      target_type: targetType,
      target_id: targetId,
      reason,
    });
  },

  bulkResolveReports: async (reportIds: number[], action: string): Promise<BulkOperationResult> => {
    const response = await apiClient.post<BulkOperationResult>(
      '/admin/reports/bulk-resolve',
      {
        report_ids: reportIds,
        action,
      }
    );
    return response.data;
  },
};

// Analytics API
export const analyticsAPI = {
  getAnalytics: async (params?: {
    city_id?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<AnalyticsData> => {
    const response = await apiClient.get<AnalyticsData>('/admin/analytics', { params });
    return response.data;
  },

  getEngagementMetrics: async (cityId?: string): Promise<{
    total_engagement: number;
    avg_votes_per_question: number;
    avg_answers_per_question: number;
    user_retention_rate: number;
  }> => {
    const params = cityId ? { city_id: cityId } : {};
    const response = await apiClient.get('/admin/analytics/engagement', { params });
    return response.data;
  },

  getTrendingTopics: async (limit: number = 10): Promise<Array<{ tag: string; count: number; trend: string }>> => {
    const response = await apiClient.get('/admin/analytics/trending', {
      params: { limit },
    });
    return response.data;
  },

  exportAnalytics: async (format: 'csv' | 'json', params?: {
    city_id?: string;
    start_date?: string;
    end_date?: string;
  }): Promise<Blob> => {
    const response = await apiClient.get('/admin/analytics/export', {
      params: { ...params, format },
      responseType: 'blob',
    });
    return response.data;
  },
};

// City Configuration API
export const cityConfigAPI = {
  getElections: async (cityId?: string): Promise<ElectionConfig[]> => {
    const params = cityId ? { city_id: cityId } : {};
    const response = await apiClient.get<ElectionConfig[]>('/admin/elections', { params });
    return response.data;
  },

  getElection: async (electionId: number): Promise<ElectionConfig> => {
    const response = await apiClient.get<ElectionConfig>(`/admin/elections/${electionId}`);
    return response.data;
  },

  createElection: async (data: Omit<ElectionConfig, 'id'>): Promise<ElectionConfig> => {
    const response = await apiClient.post<ElectionConfig>('/admin/elections', data);
    return response.data;
  },

  updateElection: async (electionId: number, data: Partial<ElectionConfig>): Promise<ElectionConfig> => {
    const response = await apiClient.put<ElectionConfig>(
      `/admin/elections/${electionId}`,
      data
    );
    return response.data;
  },

  deleteElection: async (electionId: number): Promise<void> => {
    await apiClient.delete(`/admin/elections/${electionId}`);
  },

  getCitySettings: async (cityId: string): Promise<CitySettings> => {
    const response = await apiClient.get<CitySettings>(`/admin/cities/${cityId}/settings`);
    return response.data;
  },

  updateCitySettings: async (cityId: string, settings: Partial<CitySettings>): Promise<CitySettings> => {
    const response = await apiClient.put<CitySettings>(
      `/admin/cities/${cityId}/settings`,
      settings
    );
    return response.data;
  },

  importBallot: async (cityId: string, file: File): Promise<{ ballot_id: number; contests_created: number }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post(
      `/admin/cities/${cityId}/import-ballot`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );
    return response.data;
  },
};

// Audit Log API
export const auditLogAPI = {
  getLogs: async (params?: {
    event_type?: string;
    actor_id?: number;
    city_id?: string;
    severity?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<PaginatedResponse<AuditLog>> => {
    const response = await apiClient.get<PaginatedResponse<AuditLog>>(
      '/admin/audit-logs',
      { params }
    );
    return response.data;
  },

  exportLogs: async (params?: {
    start_date?: string;
    end_date?: string;
    format?: 'csv' | 'json';
  }): Promise<Blob> => {
    const response = await apiClient.get('/admin/audit-logs/export', {
      params,
      responseType: 'blob',
    });
    return response.data;
  },
};

export default {
  dashboard: adminDashboardAPI,
  questions: questionModerationAPI,
  users: userManagementAPI,
  content: contentModerationAPI,
  analytics: analyticsAPI,
  config: cityConfigAPI,
  auditLog: auditLogAPI,
};
