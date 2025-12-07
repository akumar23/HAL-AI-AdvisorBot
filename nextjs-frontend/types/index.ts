export interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  confidence?: number;
  confidenceLevel?: 'high' | 'medium' | 'low';
  intent?: string;
  escalate?: boolean;
  escalationReason?: string;
  courseCards?: CourseCard[];
  resolvedQuery?: string;
}

export interface CourseCard {
  code: string;
  name: string;
  units?: number;
  description?: string;
  prerequisites?: string;
  prerequisites_cmpe?: string;
  prerequisites_se?: string;
  department?: string;
}

export interface ChatResponse {
  response: string;
  confidence?: number;
  confidence_level?: 'high' | 'medium' | 'low';
  sources?: Array<{
    type: string;
    content: string;
    metadata?: Record<string, unknown>;
  }>;
  model?: string;
  provider?: string;
  low_confidence?: boolean;
  intent?: string;
  escalate?: boolean;
  escalate_to_human?: boolean;
  escalation_message?: string;
  escalation_reason?: string;
  course_cards?: CourseCard[];
  resolved_query?: string;
}

export interface QuickRepliesResponse {
  suggestions: string[];
}

export interface FeedbackPayload {
  rating: 1 | 2; // 1 = thumbs down, 2 = thumbs up
  query: string;
  response: string;
  comment?: string;
  intent?: string;
  confidence?: number;
  escalated_to_human?: boolean;
  response_time_ms?: number;
}

export interface StatusResponse {
  status: string;
  provider: string;
  model: string;
  session_id: string;
}

// =============================================================================
// Admin Types
// =============================================================================

export interface AdminAuthResponse {
  authenticated: boolean;
  user?: string;
}

export interface AdminLoginResponse {
  success: boolean;
  message: string;
  user?: string;
  error?: string;
}

export interface AdminOverviewStats {
  period_days: number;
  total_sessions: number;
  total_messages: number;
  user_messages: number;
  total_feedback: number;
  positive_feedback: number;
  negative_feedback: number;
  satisfaction_rate: number;
  avg_messages_per_session: number;
}

export interface DailyUsage {
  date: string;
  sessions: number;
  messages: number;
}

export interface FeedbackBreakdown {
  positive: number;
  negative: number;
  recent_issues: Array<{
    date: string;
    query: string;
    comment: string;
  }>;
}

export interface PopularTopic {
  topic: string;
  count: number;
  percentage: number;
}

export interface CourseQuery {
  code: string;
  name: string;
  count: number;
}

export interface FeedbackInsight {
  summary: string;
  themes: string[];
  recommendations: string[];
  sample_issues: Array<{
    query?: string;
    comment?: string;
    date?: string;
  }>;
  analyzed_count: number;
  analysis_date: string;
}

export interface AdminCourse {
  id: number;
  code: string;
  name: string;
  description?: string;
  prerequisites?: string;
  prerequisites_cmpe?: string;
  prerequisites_se?: string;
  units?: number;
  department?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AdminAdvisor {
  id: number;
  name: string;
  email?: string;
  booking_url?: string;
  last_name_start: string;
  last_name_end: string;
  department?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AdminPolicy {
  id: number;
  category: string;
  question: string;
  answer: string;
  keywords?: string;
  url?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AdminDeadline {
  id: number;
  semester: string;
  deadline_type: string;
  date: string;
  description?: string;
  url?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AdminFeedback {
  id: number;
  session_id?: string;
  user_query: string;
  bot_response: string;
  rating: number;
  comment?: string;
  created_at?: string;
}

export interface AdminConversation {
  session_id: string;
  message_count: number;
  last_message?: string;
}

export interface AdminConversationDetail {
  session_id: string;
  messages: Array<{
    id: number;
    role: string;
    content: string;
    created_at?: string;
  }>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}
