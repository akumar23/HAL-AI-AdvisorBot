import type { ChatResponse, QuickRepliesResponse, FeedbackPayload, StatusResponse } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:5000';

class APIError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'APIError';
  }
}

async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      credentials: 'include', // Important for session cookies
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new APIError(response.status, `API Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
    throw new Error(`Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

export async function sendMessage(message: string): Promise<ChatResponse> {
  return fetchAPI<ChatResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify({ message }),
  });
}

export async function getQuickReplies(
  lastResponse: string = '',
  lastQuery: string = '',
  intent: string = ''
): Promise<QuickRepliesResponse> {
  return fetchAPI<QuickRepliesResponse>('/api/quick-replies', {
    method: 'POST',
    body: JSON.stringify({
      lastResponse,
      lastQuery,
      intent,
    }),
  });
}

export async function submitFeedback(feedback: FeedbackPayload): Promise<{ status: string }> {
  return fetchAPI<{ status: string }>('/api/feedback', {
    method: 'POST',
    body: JSON.stringify(feedback),
  });
}

export async function clearHistory(): Promise<{ status: string }> {
  return fetchAPI<{ status: string }>('/api/clear-history', {
    method: 'POST',
  });
}

export async function getStatus(): Promise<StatusResponse> {
  return fetchAPI<StatusResponse>('/api/status');
}
