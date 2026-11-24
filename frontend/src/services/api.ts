import axios from 'axios';
import {
  User,
  Project,
  Document,
  Claim,
  Contradiction,
  ChatMessage,
  Conversation,
  KnowledgeGraphData,
  ResearchReport,
  DashboardSummary
} from '../types';

const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to inject JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authApi = {
  login: async (email: string, password: string): Promise<{ access_token: string; user: User }> => {
    const res = await api.post('/auth/login-json', { email, password });
    return res.data;
  },
  register: async (email: string, password: string, full_name?: string): Promise<{ access_token: string; user: User }> => {
    const res = await api.post('/auth/register', { email, password, full_name });
    return res.data;
  },
  getMe: async (): Promise<User> => {
    const res = await api.get('/auth/me');
    return res.data;
  },
};

// Projects API
export const projectsApi = {
  list: async (): Promise<Project[]> => {
    const res = await api.get('/projects');
    return res.data;
  },
  create: async (title: string, description?: string): Promise<Project> => {
    const res = await api.post('/projects', { title, description });
    return res.data;
  },
  get: async (id: string): Promise<Project> => {
    const res = await api.get(`/projects/${id}`);
    return res.data;
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`/projects/${id}`);
  },
};

// Documents API
export const documentsApi = {
  listByProject: async (projectId: string): Promise<Document[]> => {
    const res = await api.get(`/documents/project/${projectId}`);
    return res.data;
  },
  upload: async (projectId: string, file: File): Promise<Document> => {
    const formData = new FormData();
    formData.append('project_id', projectId);
    formData.append('file', file);
    const res = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return res.data;
  },
  get: async (id: string): Promise<Document> => {
    const res = await api.get(`/documents/${id}`);
    return res.data;
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`/documents/${id}`);
  },
  getDownloadUrl: (id: string): string => {
    return `${API_BASE}/documents/${id}/download`;
  },
};

// Claims & Evidence API
export const claimsApi = {
  listByProject: async (projectId: string, classification?: string): Promise<Claim[]> => {
    const params = classification ? { classification } : {};
    const res = await api.get(`/claims/project/${projectId}`, { params });
    return res.data;
  },
  listContradictions: async (projectId: string): Promise<Contradiction[]> => {
    const res = await api.get(`/claims/contradictions/${projectId}`);
    return res.data;
  },
};

// Chat & Grounded Assistant API
export const chatApi = {
  sendMessage: async (projectId: string, message: string, conversationId?: string): Promise<ChatMessage> => {
    const res = await api.post('/chat/message', {
      project_id: projectId,
      message,
      conversation_id: conversationId,
    });
    return res.data;
  },
  listConversations: async (projectId: string): Promise<Conversation[]> => {
    const res = await api.get(`/chat/conversations/project/${projectId}`);
    return res.data;
  },
  getConversation: async (id: string): Promise<Conversation> => {
    const res = await api.get(`/chat/conversations/${id}`);
    return res.data;
  },
};

// Knowledge Graph API
export const graphApi = {
  getProjectGraph: async (projectId: string): Promise<KnowledgeGraphData> => {
    const res = await api.get(`/graph/project/${projectId}`);
    return res.data;
  },
};

// Research Reports API
export const reportsApi = {
  generate: async (projectId: string, researchQuestion: string, title?: string): Promise<ResearchReport> => {
    const res = await api.post('/reports/generate', {
      project_id: projectId,
      research_question: researchQuestion,
      title,
    });
    return res.data;
  },
  listByProject: async (projectId: string): Promise<ResearchReport[]> => {
    const res = await api.get(`/reports/project/${projectId}`);
    return res.data;
  },
};

// Analytics API
export const analyticsApi = {
  getSummary: async (): Promise<DashboardSummary> => {
    const res = await api.get('/analytics/summary');
    return res.data;
  },
};

export default api;
