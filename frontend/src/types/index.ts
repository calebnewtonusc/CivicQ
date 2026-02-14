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
