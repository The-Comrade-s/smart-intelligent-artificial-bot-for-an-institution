import { api } from "./api";

// --- Types ---
export interface UserRow {
  id: string;
  email: string;
  username: string;
  full_name: string;
  role: string;
  status: string;
  avatar_url: string | null;
}

export interface DashboardStats {
  total_students: number;
  active_users: number;
  total_conversations: number;
  todays_conversations: number;
  knowledge_articles: number;
  faqs: number;
  courses: number;
  lecturers: number;
  announcements: number;
  average_response_time_ms: number | null;
}

export interface TimeseriesPoint {
  date: string;
  count: number;
}

export interface ProviderUsagePoint {
  provider: string;
  count: number;
}

export interface AIProviderSetting {
  id: string;
  provider: string;
  is_active: boolean;
  is_enabled: boolean;
  temperature: number;
  max_tokens: number;
  streaming_enabled: boolean;
  system_prompt: string | null;
}

export interface Announcement {
  id: string;
  title: string;
  content: string;
  audience: string;
  priority: string;
  status: string;
  is_pinned: boolean;
  created_at: string;
}

export interface EventItem {
  id: string;
  title: string;
  description: string | null;
  venue: string | null;
  start_time: string;
  end_time: string | null;
  organizer: string | null;
}

export interface FeedbackItem {
  id: string;
  user_id: string | null;
  rating: number | null;
  category: string;
  comment: string | null;
  admin_response: string | null;
  created_at: string;
}

export interface FeedbackSummary {
  average_rating: number | null;
  total_feedback: number;
  positive_count: number;
  negative_count: number;
  bug_reports: number;
  suggestions: number;
}

export interface KnowledgeArticle {
  id: string;
  title: string;
  category: string;
  content: string;
  status: string;
  view_count: number;
  created_at: string;
}

export interface FAQ {
  id: string;
  category: string;
  question: string;
  answer: string;
  is_pinned: boolean;
  status: string;
}

export interface AuditLogEntry {
  id: string;
  user_id: string | null;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  ip_address: string | null;
  status: string;
  created_at: string;
}

export interface AppSetting {
  key: string;
  value: string | null;
  value_json: Record<string, unknown> | null;
  description: string | null;
}

// --- Dashboard / Analytics ---
export const getDashboardStats = () => api.get<DashboardStats>("/analytics/dashboard").then((r) => r.data);
export const getConversationsTimeseries = (days = 14) =>
  api.get<TimeseriesPoint[]>("/analytics/conversations-timeseries", { params: { days } }).then((r) => r.data);
export const getProviderUsage = () => api.get<ProviderUsagePoint[]>("/analytics/provider-usage").then((r) => r.data);
export const getUserGrowth = (days = 30) =>
  api.get<TimeseriesPoint[]>("/analytics/user-growth", { params: { days } }).then((r) => r.data);

// --- Users ---
export const listUsers = (params?: { role?: string; search?: string }) =>
  api.get<UserRow[]>("/users", { params }).then((r) => r.data);
export const updateUserStatus = (id: string, new_status: string) =>
  api.patch<UserRow>(`/users/${id}/status`, null, { params: { new_status } }).then((r) => r.data);
export const updateUserRole = (id: string, new_role: string) =>
  api.patch<UserRow>(`/users/${id}/role`, null, { params: { new_role } }).then((r) => r.data);
export const deleteUser = (id: string) => api.delete(`/users/${id}`);

// --- AI configuration ---
export const listAIProviders = () => api.get<AIProviderSetting[]>("/ai/providers").then((r) => r.data);
export const updateAIProvider = (provider: string, payload: Partial<AIProviderSetting>) =>
  api.patch<AIProviderSetting>(`/ai/providers/${provider}`, payload).then((r) => r.data);
export const activateAIProvider = (provider: string) =>
  api.post<AIProviderSetting>("/ai/providers/activate", { provider }).then((r) => r.data);

// --- Announcements ---
export const listAllAnnouncements = () => api.get<Announcement[]>("/announcements").then((r) => r.data);
export const createAnnouncement = (payload: Partial<Announcement>) =>
  api.post<Announcement>("/announcements", payload).then((r) => r.data);
export const deleteAnnouncement = (id: string) => api.delete(`/announcements/${id}`);

// --- Events ---
export const listEvents = () => api.get<EventItem[]>("/events").then((r) => r.data);
export const createEvent = (payload: Partial<EventItem>) => api.post<EventItem>("/events", payload).then((r) => r.data);
export const deleteEvent = (id: string) => api.delete(`/events/${id}`);

// --- Feedback ---
export const listFeedback = () => api.get<FeedbackItem[]>("/feedback").then((r) => r.data);
export const getFeedbackSummary = () => api.get<FeedbackSummary>("/feedback/summary").then((r) => r.data);
export const respondToFeedback = (id: string, admin_response: string) =>
  api.patch<FeedbackItem>(`/feedback/${id}/respond`, { admin_response }).then((r) => r.data);

// --- Knowledge base ---
export const listArticles = () => api.get<KnowledgeArticle[]>("/knowledge-base/articles").then((r) => r.data);
export const createArticle = (payload: Partial<KnowledgeArticle>) =>
  api.post<KnowledgeArticle>("/knowledge-base/articles", payload).then((r) => r.data);
export const deleteArticle = (id: string) => api.delete(`/knowledge-base/articles/${id}`);
export const listFAQs = () => api.get<FAQ[]>("/knowledge-base/faqs").then((r) => r.data);
export const createFAQ = (payload: Partial<FAQ>) => api.post<FAQ>("/knowledge-base/faqs", payload).then((r) => r.data);
export const deleteFAQ = (id: string) => api.delete(`/knowledge-base/faqs/${id}`);

// --- Settings ---
export const listSettings = () => api.get<AppSetting[]>("/settings").then((r) => r.data);
export const upsertSetting = (payload: AppSetting) => api.put<AppSetting>("/settings", payload).then((r) => r.data);

// --- Audit logs ---
export const listAuditLogs = (action?: string) =>
  api.get<AuditLogEntry[]>("/audit-logs", { params: action ? { action } : {} }).then((r) => r.data);
