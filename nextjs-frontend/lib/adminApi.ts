import type {
  AdminAuthResponse,
  AdminLoginResponse,
  AdminOverviewStats,
  DailyUsage,
  FeedbackBreakdown,
  PopularTopic,
  CourseQuery,
  FeedbackInsight,
  AdminCourse,
  AdminAdvisor,
  AdminPolicy,
  AdminDeadline,
  AdminFeedback,
  AdminConversation,
  AdminConversationDetail,
  PaginatedResponse,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';

class AdminAPIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'AdminAPIError';
  }
}

async function fetchAdminAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}/api/admin${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new AdminAPIError(401, 'Unauthorized');
      }
      const data = await response.json().catch(() => ({}));
      throw new AdminAPIError(response.status, data.error || `API Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof AdminAPIError) {
      throw error;
    }
    throw new Error(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

// =============================================================================
// Authentication
// =============================================================================

export async function adminLogin(username: string, password: string): Promise<AdminLoginResponse> {
  return fetchAdminAPI<AdminLoginResponse>('/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
}

export async function adminLogout(): Promise<{ success: boolean }> {
  return fetchAdminAPI<{ success: boolean }>('/logout', {
    method: 'POST',
  });
}

export async function checkAdminAuth(): Promise<AdminAuthResponse> {
  return fetchAdminAPI<AdminAuthResponse>('/check-auth');
}

// =============================================================================
// Analytics
// =============================================================================

export async function getAnalyticsOverview(days: number = 30): Promise<AdminOverviewStats> {
  return fetchAdminAPI<AdminOverviewStats>(`/analytics/overview?days=${days}`);
}

export async function getDailyUsage(days: number = 30): Promise<DailyUsage[]> {
  return fetchAdminAPI<DailyUsage[]>(`/analytics/daily-usage?days=${days}`);
}

export async function getFeedbackBreakdown(days: number = 30): Promise<FeedbackBreakdown> {
  return fetchAdminAPI<FeedbackBreakdown>(`/analytics/feedback-breakdown?days=${days}`);
}

export async function getPopularTopics(days: number = 30): Promise<PopularTopic[]> {
  return fetchAdminAPI<PopularTopic[]>(`/analytics/popular-topics?days=${days}`);
}

export async function getCourseQueries(days: number = 30): Promise<CourseQuery[]> {
  return fetchAdminAPI<CourseQuery[]>(`/analytics/course-queries?days=${days}`);
}

export async function exportAnalytics(days: number = 30): Promise<Record<string, unknown>> {
  return fetchAdminAPI<Record<string, unknown>>(`/analytics/export?days=${days}`);
}

export async function getSessionDetail(sessionId: string): Promise<{
  session_id: string;
  message_count: number;
  conversation: Array<{ role: string; content: string; timestamp: string }>;
  feedback: Array<{ rating: string; query: string; comment: string; timestamp: string }>;
  start_time?: string;
  end_time?: string;
}> {
  return fetchAdminAPI(`/analytics/session/${sessionId}`);
}

// =============================================================================
// AI Feedback Analysis
// =============================================================================

export async function getFeedbackAnalysis(days: number = 30): Promise<FeedbackInsight> {
  return fetchAdminAPI<FeedbackInsight>(`/feedback-analysis?days=${days}`);
}

export async function getWeeklyReport(): Promise<Record<string, unknown>> {
  return fetchAdminAPI<Record<string, unknown>>('/feedback-analysis/weekly-report');
}

export async function getTopicSuggestions(topic: string): Promise<{ topic: string; suggestions: string[] }> {
  return fetchAdminAPI<{ topic: string; suggestions: string[] }>(`/feedback-analysis/suggestions/${topic}`);
}

// =============================================================================
// Courses CRUD
// =============================================================================

export async function getCourses(params?: {
  page?: number;
  per_page?: number;
  search?: string;
  department?: string;
}): Promise<PaginatedResponse<AdminCourse>> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set('page', params.page.toString());
  if (params?.per_page) searchParams.set('per_page', params.per_page.toString());
  if (params?.search) searchParams.set('search', params.search);
  if (params?.department) searchParams.set('department', params.department);
  
  const query = searchParams.toString();
  return fetchAdminAPI<PaginatedResponse<AdminCourse>>(`/courses${query ? `?${query}` : ''}`);
}

export async function getCourse(id: number): Promise<AdminCourse> {
  return fetchAdminAPI<AdminCourse>(`/courses/${id}`);
}

export async function createCourse(course: Partial<AdminCourse>): Promise<AdminCourse> {
  return fetchAdminAPI<AdminCourse>('/courses', {
    method: 'POST',
    body: JSON.stringify(course),
  });
}

export async function updateCourse(id: number, course: Partial<AdminCourse>): Promise<AdminCourse> {
  return fetchAdminAPI<AdminCourse>(`/courses/${id}`, {
    method: 'PUT',
    body: JSON.stringify(course),
  });
}

export async function deleteCourse(id: number): Promise<{ success: boolean }> {
  return fetchAdminAPI<{ success: boolean }>(`/courses/${id}`, {
    method: 'DELETE',
  });
}

// =============================================================================
// Advisors CRUD
// =============================================================================

export async function getAdvisors(): Promise<{ items: AdminAdvisor[] }> {
  return fetchAdminAPI<{ items: AdminAdvisor[] }>('/advisors');
}

export async function getAdvisor(id: number): Promise<AdminAdvisor> {
  return fetchAdminAPI<AdminAdvisor>(`/advisors/${id}`);
}

export async function createAdvisor(advisor: Partial<AdminAdvisor>): Promise<AdminAdvisor> {
  return fetchAdminAPI<AdminAdvisor>('/advisors', {
    method: 'POST',
    body: JSON.stringify(advisor),
  });
}

export async function updateAdvisor(id: number, advisor: Partial<AdminAdvisor>): Promise<AdminAdvisor> {
  return fetchAdminAPI<AdminAdvisor>(`/advisors/${id}`, {
    method: 'PUT',
    body: JSON.stringify(advisor),
  });
}

export async function deleteAdvisor(id: number): Promise<{ success: boolean }> {
  return fetchAdminAPI<{ success: boolean }>(`/advisors/${id}`, {
    method: 'DELETE',
  });
}

// =============================================================================
// Policies CRUD
// =============================================================================

export async function getPolicies(params?: {
  category?: string;
  search?: string;
}): Promise<{ items: AdminPolicy[]; categories: string[] }> {
  const searchParams = new URLSearchParams();
  if (params?.category) searchParams.set('category', params.category);
  if (params?.search) searchParams.set('search', params.search);
  
  const query = searchParams.toString();
  return fetchAdminAPI<{ items: AdminPolicy[]; categories: string[] }>(`/policies${query ? `?${query}` : ''}`);
}

export async function getPolicy(id: number): Promise<AdminPolicy> {
  return fetchAdminAPI<AdminPolicy>(`/policies/${id}`);
}

export async function createPolicy(policy: Partial<AdminPolicy>): Promise<AdminPolicy> {
  return fetchAdminAPI<AdminPolicy>('/policies', {
    method: 'POST',
    body: JSON.stringify(policy),
  });
}

export async function updatePolicy(id: number, policy: Partial<AdminPolicy>): Promise<AdminPolicy> {
  return fetchAdminAPI<AdminPolicy>(`/policies/${id}`, {
    method: 'PUT',
    body: JSON.stringify(policy),
  });
}

export async function deletePolicy(id: number): Promise<{ success: boolean }> {
  return fetchAdminAPI<{ success: boolean }>(`/policies/${id}`, {
    method: 'DELETE',
  });
}

// =============================================================================
// Deadlines CRUD
// =============================================================================

export async function getDeadlines(params?: {
  semester?: string;
  deadline_type?: string;
}): Promise<{ items: AdminDeadline[]; deadline_types: string[]; semesters: string[] }> {
  const searchParams = new URLSearchParams();
  if (params?.semester) searchParams.set('semester', params.semester);
  if (params?.deadline_type) searchParams.set('deadline_type', params.deadline_type);
  
  const query = searchParams.toString();
  return fetchAdminAPI<{ items: AdminDeadline[]; deadline_types: string[]; semesters: string[] }>(
    `/deadlines${query ? `?${query}` : ''}`
  );
}

export async function getDeadline(id: number): Promise<AdminDeadline> {
  return fetchAdminAPI<AdminDeadline>(`/deadlines/${id}`);
}

export async function createDeadline(deadline: Partial<AdminDeadline>): Promise<AdminDeadline> {
  return fetchAdminAPI<AdminDeadline>('/deadlines', {
    method: 'POST',
    body: JSON.stringify(deadline),
  });
}

export async function updateDeadline(id: number, deadline: Partial<AdminDeadline>): Promise<AdminDeadline> {
  return fetchAdminAPI<AdminDeadline>(`/deadlines/${id}`, {
    method: 'PUT',
    body: JSON.stringify(deadline),
  });
}

export async function deleteDeadline(id: number): Promise<{ success: boolean }> {
  return fetchAdminAPI<{ success: boolean }>(`/deadlines/${id}`, {
    method: 'DELETE',
  });
}

// =============================================================================
// Feedback (Read-only with delete)
// =============================================================================

export async function getFeedback(params?: {
  page?: number;
  per_page?: number;
  rating?: number;
}): Promise<PaginatedResponse<AdminFeedback>> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set('page', params.page.toString());
  if (params?.per_page) searchParams.set('per_page', params.per_page.toString());
  if (params?.rating) searchParams.set('rating', params.rating.toString());
  
  const query = searchParams.toString();
  return fetchAdminAPI<PaginatedResponse<AdminFeedback>>(`/feedback${query ? `?${query}` : ''}`);
}

export async function deleteFeedback(id: number): Promise<{ success: boolean }> {
  return fetchAdminAPI<{ success: boolean }>(`/feedback/${id}`, {
    method: 'DELETE',
  });
}

// =============================================================================
// Conversations (Read-only with delete)
// =============================================================================

export async function getConversations(params?: {
  page?: number;
  per_page?: number;
}): Promise<PaginatedResponse<AdminConversation>> {
  const searchParams = new URLSearchParams();
  if (params?.page) searchParams.set('page', params.page.toString());
  if (params?.per_page) searchParams.set('per_page', params.per_page.toString());
  
  const query = searchParams.toString();
  return fetchAdminAPI<PaginatedResponse<AdminConversation>>(`/conversations${query ? `?${query}` : ''}`);
}

export async function getConversation(sessionId: string): Promise<AdminConversationDetail> {
  return fetchAdminAPI<AdminConversationDetail>(`/conversations/${sessionId}`);
}

export async function deleteConversation(sessionId: string): Promise<{ success: boolean }> {
  return fetchAdminAPI<{ success: boolean }>(`/conversations/${sessionId}`, {
    method: 'DELETE',
  });
}

export { AdminAPIError };
