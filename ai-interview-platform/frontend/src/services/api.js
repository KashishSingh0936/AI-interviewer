import axios from 'axios'
import { useAuthStore } from '../context/AuthContext'

const API_BASE_URL = '/api'

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const getApiErrorMessage = (error, fallbackMessage = 'Request failed') => {
  const detail = error?.response?.data?.detail

  if (Array.isArray(detail)) {
    // FastAPI validation errors are often returned as a detail array.
    return detail
      .map((item) => item?.msg || item?.message)
      .filter(Boolean)
      .join('; ') || fallbackMessage
  }

  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  if (error?.response?.status >= 500) {
    return 'Server error. Please try again in a moment.'
  }

  if (!error?.response) {
    return 'Unable to reach the server. Check your connection and try again.'
  }

  return fallbackMessage
}

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle response errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const requestUrl = error?.config?.url || ''
    const isAuthRequest = requestUrl.includes('/auth/login') || requestUrl.includes('/auth/register')

    if (error.response?.status === 401 && !isAuthRequest) {
      // Token expired or invalid
      useAuthStore.getState().logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  register: (data) => apiClient.post('/auth/register', data),
  login: (data) => apiClient.post('/auth/login', data),
  getMe: () => apiClient.get('/auth/me'),
}

// Interview API
export const interviewAPI = {
  createInterview: (data) => apiClient.post('/interviews', data),
  getInterviews: () => apiClient.get('/interviews'),
  getInterview: (id) => apiClient.get(`/interviews/${id}`),
  startInterview: (id) => apiClient.post(`/interviews/${id}/start`),
  getNextQuestion: (id) => apiClient.get(`/interviews/${id}/next-question`),
  submitAnswer: (id, data) => apiClient.post(`/interviews/${id}/answer`, data),
  completeInterview: (id) => apiClient.post(`/interviews/${id}/complete`),
  scheduleInterview: (data) => apiClient.post('/interviews/schedule', data),
}

// Domain API
export const domainAPI = {
  getDomains: () => apiClient.get('/domains'),
  getDomain: (id) => apiClient.get(`/domains/${id}`),
  createDomain: (data) => apiClient.post('/domains', data),
  getDomainRoles: (id) => apiClient.get(`/domains/${id}/roles`),
  createRole: (domainId, data) => apiClient.post(`/domains/${domainId}/roles`, data),
  initializeDomains: () => apiClient.post('/domains/init'),
}

export default apiClient
