"use client";

import { getToken, removeToken } from "@/lib/auth";
import type {
  Task,
  TaskCreate,
  TaskFilters,
  TaskListResponse,
  TagsResponse,
  TaskUpdate,
  TaskShare,
  TaskShareListResponse,
  Comment,
  CommentListResponse,
  Activity,
  ActivityListResponse,
  User,
  UserSearchResponse,
} from "@/types/task";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * API Error class for handling HTTP errors.
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Make an authenticated API request.
 */
async function fetchWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  // Handle 401 Unauthorized - redirect to login
  if (response.status === 401) {
    removeToken();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new ApiError("Unauthorized", 401, "UNAUTHORIZED");
  }

  // Handle other errors
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(
      error.detail || "Request failed",
      response.status,
      error.code
    );
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

/**
 * Task API functions.
 */
// Chat API URL (can be same as main API or separate Phase 3 backend)
const CHAT_API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL || API_URL;

/**
 * Chat request payload.
 */
export interface ChatRequest {
  message: string;
  conversation_id?: string;
}

/**
 * Tool call result.
 */
export interface ToolCall {
  tool: string;
  result?: Record<string, unknown>;
  error?: string;
}

/**
 * Chat response payload.
 */
export interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: ToolCall[];
}

/**
 * Conversation summary.
 */
export interface Conversation {
  id: string;
  user_id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Message in a conversation.
 */
export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant";
  content: string;
  tool_calls: ToolCall[] | null;
  created_at: string;
}

/**
 * Conversation with messages.
 */
export interface ConversationWithMessages extends Conversation {
  messages: Message[];
}

/**
 * Make an authenticated request to the Chat API.
 */
async function fetchChatWithAuth<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${CHAT_API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    removeToken();
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
    throw new ApiError("Unauthorized", 401, "UNAUTHORIZED");
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(
      error.message || error.detail || "Request failed",
      response.status,
      error.code || error.error
    );
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

/**
 * Chat API functions.
 */
export const chatApi = {
  /**
   * Send a chat message and get AI response.
   */
  async sendMessage(userId: string, request: ChatRequest): Promise<ChatResponse> {
    return fetchChatWithAuth<ChatResponse>(`/api/${userId}/chat`, {
      method: "POST",
      body: JSON.stringify(request),
    });
  },

  /**
   * Get user's conversations.
   */
  async getConversations(userId: string, limit: number = 10): Promise<{ conversations: Conversation[] }> {
    return fetchChatWithAuth<{ conversations: Conversation[] }>(
      `/api/${userId}/conversations?limit=${limit}`
    );
  },

  /**
   * Get a specific conversation with messages.
   */
  async getConversation(
    userId: string,
    conversationId: string,
    limit: number = 50
  ): Promise<ConversationWithMessages> {
    return fetchChatWithAuth<ConversationWithMessages>(
      `/api/${userId}/conversations/${conversationId}?limit=${limit}`
    );
  },

  /**
   * Delete a conversation.
   */
  async deleteConversation(userId: string, conversationId: string): Promise<void> {
    return fetchChatWithAuth<void>(`/api/${userId}/conversations/${conversationId}`, {
      method: "DELETE",
    });
  },
};

/**
 * Task API functions.
 */
export const taskApi = {
  /**
   * Get all tasks for the current user with optional filtering.
   */
  async list(params?: Partial<TaskFilters>): Promise<TaskListResponse> {
    const searchParams = new URLSearchParams();
    if (params?.status) searchParams.set("status", params.status);
    if (params?.sort) searchParams.set("sort", params.sort);
    if (params?.order) searchParams.set("order", params.order);
    if (params?.priority && params.priority !== "all") {
      searchParams.set("priority", params.priority);
    }
    if (params?.tags && params.tags.length > 0) {
      searchParams.set("tags", params.tags.join(","));
    }
    if (params?.search) searchParams.set("search", params.search);
    if (params?.due_before) searchParams.set("due_before", params.due_before);
    if (params?.due_after) searchParams.set("due_after", params.due_after);
    if (params?.overdue_only) searchParams.set("overdue_only", "true");

    const queryString = searchParams.toString();
    const endpoint = `/api/tasks${queryString ? `?${queryString}` : ""}`;

    return fetchWithAuth<TaskListResponse>(endpoint);
  },

  /**
   * Get a single task by ID.
   */
  async get(id: string): Promise<Task> {
    return fetchWithAuth<Task>(`/api/tasks/${id}`);
  },

  /**
   * Create a new task.
   */
  async create(data: TaskCreate): Promise<Task> {
    return fetchWithAuth<Task>("/api/tasks", {
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  /**
   * Update an existing task.
   */
  async update(id: string, data: TaskUpdate): Promise<Task> {
    return fetchWithAuth<Task>(`/api/tasks/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  /**
   * Delete a task.
   */
  async delete(id: string): Promise<void> {
    return fetchWithAuth<void>(`/api/tasks/${id}`, {
      method: "DELETE",
    });
  },

  /**
   * Toggle task completion status.
   */
  async toggleComplete(id: string): Promise<Task> {
    return fetchWithAuth<Task>(`/api/tasks/${id}/complete`, {
      method: "PATCH",
    });
  },

  /**
   * Get all unique tags used by the current user.
   */
  async getTags(): Promise<TagsResponse> {
    return fetchWithAuth<TagsResponse>("/api/tasks/tags");
  },
};

/**
 * Share API functions for task collaboration.
 */
export const shareApi = {
  /**
   * Get all shares for a task.
   */
  async getShares(taskId: string): Promise<TaskShareListResponse> {
    return fetchWithAuth<TaskShareListResponse>(`/api/tasks/${taskId}/shares`);
  },

  /**
   * Share a task with another user.
   */
  async share(taskId: string, email: string, permission: "view" | "edit" = "view"): Promise<TaskShare> {
    return fetchWithAuth<TaskShare>(`/api/tasks/${taskId}/shares`, {
      method: "POST",
      body: JSON.stringify({ user_email: email, permission }),
    });
  },

  /**
   * Remove a share from a task.
   */
  async removeShare(taskId: string, shareId: string): Promise<void> {
    return fetchWithAuth<void>(`/api/tasks/${taskId}/shares/${shareId}`, {
      method: "DELETE",
    });
  },

  /**
   * Update share permission.
   */
  async updateShare(taskId: string, shareId: string, permission: "view" | "edit"): Promise<TaskShare> {
    return fetchWithAuth<TaskShare>(`/api/tasks/${taskId}/shares/${shareId}`, {
      method: "PATCH",
      body: JSON.stringify({ permission }),
    });
  },
};

/**
 * Comment API functions for task discussions.
 */
export const commentApi = {
  /**
   * Get all comments for a task.
   */
  async getComments(taskId: string): Promise<CommentListResponse> {
    return fetchWithAuth<CommentListResponse>(`/api/tasks/${taskId}/comments`);
  },

  /**
   * Create a new comment on a task.
   */
  async create(taskId: string, content: string, parentId?: string): Promise<Comment> {
    return fetchWithAuth<Comment>(`/api/tasks/${taskId}/comments`, {
      method: "POST",
      body: JSON.stringify({ content, parent_id: parentId }),
    });
  },

  /**
   * Update an existing comment.
   */
  async update(commentId: string, content: string): Promise<Comment> {
    return fetchWithAuth<Comment>(`/api/comments/${commentId}`, {
      method: "PATCH",
      body: JSON.stringify({ content }),
    });
  },

  /**
   * Delete a comment.
   */
  async delete(commentId: string): Promise<void> {
    return fetchWithAuth<void>(`/api/comments/${commentId}`, {
      method: "DELETE",
    });
  },
};

/**
 * Activity API functions for tracking task changes.
 */
export const activityApi = {
  /**
   * Get activity feed for the current user.
   */
  async getActivities(limit: number = 20, offset: number = 0): Promise<ActivityListResponse> {
    const params = new URLSearchParams({
      limit: limit.toString(),
      offset: offset.toString(),
    });
    return fetchWithAuth<ActivityListResponse>(`/api/activities?${params}`);
  },

  /**
   * Get activities for a specific task.
   */
  async getTaskActivities(taskId: string, limit: number = 20): Promise<ActivityListResponse> {
    return fetchWithAuth<ActivityListResponse>(`/api/tasks/${taskId}/activities?limit=${limit}`);
  },
};

/**
 * User API functions for user search and collaboration.
 */
export const userApi = {
  /**
   * Search for users by email or name.
   */
  async search(query: string, limit: number = 10): Promise<UserSearchResponse> {
    const params = new URLSearchParams({
      q: query,
      limit: limit.toString(),
    });
    return fetchWithAuth<UserSearchResponse>(`/api/users/search?${params}`);
  },
};
