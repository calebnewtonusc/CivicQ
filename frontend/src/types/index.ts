// Core Types for CivicQ Frontend

// User Types
export enum UserRole {
  VOTER = 'voter',
  CANDIDATE = 'candidate',
  ADMIN = 'admin',
  MODERATOR = 'moderator',
  CITY_STAFF = 'city_staff',
}

export enum VerificationStatus {
  PENDING = 'pending',
  VERIFIED = 'verified',
  REJECTED = 'rejected',
  EXPIRED = 'expired',
}

export interface User {
  id: number;
  email: string;
  full_name?: string;
  phone_number?: string;
  role: UserRole;
  is_active: boolean;
  is_superuser: boolean;
  city_id?: string;
  city_name?: string;
  verification_status: VerificationStatus;
  last_active?: string;
  created_at: string;
  updated_at: string;
}

// Ballot Types
export enum ContestType {
  RACE = 'race',
  MEASURE = 'measure',
}

export interface Ballot {
  id: number;
  city_id: string;
  city_name: string;
  election_date: string;
  version: number;
  source_metadata?: Record<string, any>;
  is_published: boolean;
  contests?: Contest[];
  created_at: string;
  updated_at: string;
}

export interface Contest {
  id: number;
  ballot_id: number;
  type: ContestType;
  title: string;
  jurisdiction?: string;
  office?: string;
  seat_count?: number;
  description?: string;
  display_order: number;
  candidates?: Candidate[];
  measures?: Measure[];
  questions?: Question[];
  created_at: string;
  updated_at: string;
}

// Candidate Types
export enum CandidateStatus {
  PENDING = 'pending',
  VERIFIED = 'verified',
  ACTIVE = 'active',
  WITHDRAWN = 'withdrawn',
  DISQUALIFIED = 'disqualified',
}

export interface Candidate {
  id: number;
  contest_id: number;
  user_id?: number;
  name: string;
  filing_id?: string;
  email?: string;
  phone?: string;
  status: CandidateStatus;
  profile_fields?: Record<string, any>;
  photo_url?: string;
  website?: string;
  identity_verified: boolean;
  identity_verified_at?: string;
  display_order: number;
  video_answers?: VideoAnswer[];
  created_at: string;
  updated_at: string;
}

export interface Measure {
  id: number;
  contest_id: number;
  measure_number?: string;
  measure_text: string;
  summary?: string;
  fiscal_notes?: string;
  pro_statement?: string;
  con_statement?: string;
  pro_contacts?: any[];
  con_contacts?: any[];
  created_at: string;
  updated_at: string;
}

// Question Types
export enum QuestionStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  MERGED = 'merged',
  REMOVED = 'removed',
}

export interface Question {
  id: number;
  contest_id: number;
  author_id?: number;
  current_version_id?: number;
  question_text: string;
  issue_tags?: string[];
  status: QuestionStatus;
  cluster_id?: number;
  context?: string;
  upvotes: number;
  downvotes: number;
  rank_score: number;
  representation_metadata?: Record<string, any>;
  is_flagged: number;
  moderation_notes?: string;
  video_answers?: VideoAnswer[];
  created_at: string;
  updated_at: string;
}

export interface QuestionVersion {
  id: number;
  question_id: number;
  version_number: number;
  question_text: string;
  edit_author_id?: number;
  edit_reason?: string;
  diff_metadata?: Record<string, any>;
  created_at: string;
}

export interface Vote {
  id: number;
  user_id: number;
  question_id: number;
  value: number; // +1 or -1
  device_risk_score?: number;
  weight: number;
  metadata?: Record<string, any>;
  created_at: string;
  updated_at: string;
}

// Answer Types
export enum AnswerStatus {
  DRAFT = 'draft',
  PROCESSING = 'processing',
  PUBLISHED = 'published',
  WITHDRAWN = 'withdrawn',
}

export interface VideoAnswer {
  id: number;
  candidate_id: number;
  question_id: number;
  question_version_id?: number;
  video_asset_id: string;
  video_url?: string;
  duration: number;
  transcript_id?: string;
  transcript_text?: string;
  transcript_url?: string;
  captions_url?: string;
  provenance_hash?: string;
  authenticity_metadata?: Record<string, any>;
  status: AnswerStatus;
  position_summary?: string;
  rationale?: string;
  tradeoff_acknowledged?: string;
  implementation_plan?: string;
  measurement_criteria?: string;
  values_statement?: string;
  is_open_question: boolean;
  has_correction: boolean;
  correction_text?: string;
  candidate?: Candidate;
  question?: Question;
  claims?: Claim[];
  created_at: string;
  updated_at: string;
}

export interface Rebuttal {
  id: number;
  candidate_id: number;
  target_answer_id: number;
  target_claim_text: string;
  target_claim_timestamp?: number;
  video_asset_id: string;
  video_url?: string;
  duration: number;
  transcript_id?: string;
  transcript_text?: string;
  transcript_url?: string;
  status: AnswerStatus;
  created_at: string;
  updated_at: string;
}

export interface Claim {
  id: number;
  answer_id: number;
  claim_snippet: string;
  claim_timestamp?: number;
  sources?: Array<{
    url: string;
    title: string;
    description?: string;
  }>;
  is_verified: boolean;
  reviewer_notes?: string;
  created_at: string;
  updated_at: string;
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ApiError {
  detail: string;
  code?: string;
  field?: string;
}

// Auth Types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name?: string;
  city_id?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// Form Types
export interface QuestionSubmit {
  contest_id: number;
  question_text: string;
  issue_tags?: string[];
  context?: string;
}

export interface VideoAnswerSubmit {
  question_id: number;
  video_file: File;
  position_summary?: string;
  is_open_question?: boolean;
}

// LLM/AI Feature Types
export interface QuestionAnalysis {
  quality_score: number;
  is_appropriate: boolean;
  category: string;
  subcategory?: string;
  issues: string[];
  suggestions: string[];
  improved_version?: string;
}

export interface QuestionAnalysisResponse {
  analysis: QuestionAnalysis;
  success: boolean;
  message: string;
}

export interface DuplicateCheckResult {
  is_duplicate: boolean;
  similarity_score: number;
  matched_question_id?: number;
  explanation: string;
  success: boolean;
}

export interface SuggestedQuestionsResponse {
  questions: string[];
  success: boolean;
}

export interface LLMHealthResponse {
  status: 'healthy' | 'unhealthy';
  enabled?: boolean;
  model?: string;
  error?: string;
}

// Admin Panel Types

export enum AdminPermission {
  VIEW_DASHBOARD = 'view_dashboard',
  MODERATE_QUESTIONS = 'moderate_questions',
  MODERATE_CONTENT = 'moderate_content',
  MANAGE_USERS = 'manage_users',
  VIEW_ANALYTICS = 'view_analytics',
  MANAGE_CITY_CONFIG = 'manage_city_config',
  VIEW_AUDIT_LOG = 'view_audit_log',
  MANAGE_ELECTIONS = 'manage_elections',
  BULK_OPERATIONS = 'bulk_operations',
}

export interface AdminStats {
  total_users: number;
  active_users_24h: number;
  total_questions: number;
  pending_questions: number;
  flagged_content: number;
  total_answers: number;
  total_votes: number;
  engagement_rate: number;
}

export enum ReportStatus {
  PENDING = 'pending',
  REVIEWING = 'reviewing',
  RESOLVED = 'resolved',
  DISMISSED = 'dismissed',
}

export interface Report {
  id: number;
  reporter_id?: number;
  reported_user_id?: number;
  target_type?: 'question' | 'answer' | 'comment';
  target_id?: number;
  reason: string;
  description?: string;
  status: ReportStatus;
  resolution_notes?: string;
  resolved_by?: number;
  resolved_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ModerationQueueItem {
  id: number;
  type: 'question' | 'answer' | 'user_report';
  content: Question | VideoAnswer | Report;
  status: QuestionStatus | AnswerStatus | string;
  submitted_at: string;
  flagged_count?: number;
  priority: 'low' | 'medium' | 'high' | 'critical';
}

export interface UserActivity {
  user: User;
  questions_submitted: number;
  votes_cast: number;
  reports_filed: number;
  warnings: number;
  last_warning?: string;
  account_status: 'active' | 'warned' | 'suspended' | 'banned';
}

export interface AnalyticsData {
  daily_active_users: Array<{ date: string; count: number }>;
  question_submissions: Array<{ date: string; count: number }>;
  vote_activity: Array<{ date: string; count: number }>;
  top_topics: Array<{ tag: string; count: number }>;
  answer_coverage: {
    total_questions: number;
    answered_questions: number;
    coverage_percentage: number;
  };
  user_demographics: {
    by_city: Array<{ city: string; count: number }>;
    by_verification_status: Array<{ status: string; count: number }>;
  };
}

export interface ModerationRequest {
  action: 'approve' | 'reject' | 'merge' | 'flag' | 'remove';
  target_type: 'question' | 'answer' | 'user';
  target_ids: number[];
  reason?: string;
  merge_into_id?: number;
  notes?: string;
}

export interface UserModerationAction {
  user_id: number;
  action: 'warn' | 'suspend' | 'ban' | 'restore';
  duration_days?: number;
  reason: string;
  notes?: string;
}

export interface BulkOperationResult {
  success_count: number;
  failure_count: number;
  errors: Array<{ id: number; error: string }>;
}

export interface ElectionConfig {
  id?: number;
  city_id: string;
  election_date: string;
  election_name: string;
  registration_deadline?: string;
  early_voting_start?: string;
  early_voting_end?: string;
  question_deadline?: string;
  answer_deadline?: string;
  is_active: boolean;
}

export interface CitySettings {
  city_id: string;
  city_name: string;
  allow_question_submission: boolean;
  require_verification: boolean;
  moderation_mode: 'auto' | 'manual' | 'hybrid';
  min_vote_weight: number;
  allow_anonymous_questions: boolean;
  enable_ai_features: boolean;
  custom_branding?: {
    logo_url?: string;
    primary_color?: string;
    accent_color?: string;
  };
}

export interface AuditLog {
  id: number;
  event_type: string;
  actor_id?: number;
  target_type?: string;
  target_id?: number;
  event_data?: Record<string, any>;
  severity: 'info' | 'warning' | 'critical';
  city_scope?: string;
  created_at: string;
}
