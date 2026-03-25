const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api';

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token');
}

async function apiFetch(url: string, options: RequestInit = {}) {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${url}`, { ...options, headers });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

// Auth
export async function login(email: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  });

  if (!res.ok) throw new Error('邮箱或密码错误');
  const data = await res.json();
  localStorage.setItem('token', data.access_token);
  return data;
}

export async function register(email: string, username: string, password: string) {
  return apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, username, password }),
  });
}

export async function getMe() {
  return apiFetch('/auth/me');
}

// Monitors
export async function getMonitors() {
  return apiFetch('/monitors');
}

export async function createMonitor(keyword: string, timeRange: string = '3m') {
  return apiFetch('/monitors', {
    method: 'POST',
    body: JSON.stringify({ keyword, time_range: timeRange }),
  });
}

export async function deleteMonitor(id: number) {
  return apiFetch(`/monitors/${id}`, { method: 'DELETE' });
}

// Analysis
export async function runAnalysis(keyword: string, timeRange: string = '3m') {
  return apiFetch('/analysis/run', {
    method: 'POST',
    body: JSON.stringify({ keyword, time_range: timeRange }),
  });
}

export async function checkTaskStatus(taskId: string) {
  return apiFetch(`/analysis/status/${taskId}`);
}

export async function getSnapshot(monitorId: number) {
  return apiFetch(`/analysis/snapshot/${monitorId}`);
}

// Reports
export async function generateReport(monitorId: number, reportType: string) {
  return apiFetch('/reports/generate', {
    method: 'POST',
    body: JSON.stringify({ monitor_id: monitorId, report_type: reportType }),
  });
}

export async function checkReportStatus(reportId: number) {
  return apiFetch(`/reports/status/${reportId}`);
}

export function getDownloadUrl(reportId: number): string {
  const token = getToken();
  return `${API_BASE}/reports/download/${reportId}?token=${token}`;
}

// Stripe
export async function createCheckoutSession() {
  return apiFetch('/payments/create-checkout', { method: 'POST' });
}

export async function getSubscriptionStatus() {
  return apiFetch('/payments/subscription');
}
