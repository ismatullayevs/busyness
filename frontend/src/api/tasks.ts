import type { Task, TaskCreate, TaskUpdate, TaskWithLogs, TaskLog, TaskLogCreate } from '../types/task';

const API_BASE = '/api/tasks';

function getAuthHeaders(): HeadersInit {
  const token = localStorage.getItem('token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (response.status === 401) {
    localStorage.removeItem('token');
    window.location.href = '/login';
    throw new Error('Unauthorized');
  }
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || 'An error occurred');
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json();
}

export async function getTasks(): Promise<Task[]> {
  const response = await fetch(API_BASE, {
    headers: getAuthHeaders(),
  });
  return handleResponse<Task[]>(response);
}

export async function getCompletedTasks(): Promise<Task[]> {
  const response = await fetch(`${API_BASE}/completed`, {
    headers: getAuthHeaders(),
  });
  return handleResponse<Task[]>(response);
}

export async function getTask(id: number): Promise<TaskWithLogs> {
  const response = await fetch(`${API_BASE}/${id}`, {
    headers: getAuthHeaders(),
  });
  return handleResponse<TaskWithLogs>(response);
}

export async function createTask(task: TaskCreate): Promise<Task> {
  const response = await fetch(API_BASE, {
    method: 'POST',
    headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(task),
  });
  return handleResponse<Task>(response);
}

export async function updateTask(id: number, task: TaskUpdate): Promise<Task> {
  const response = await fetch(`${API_BASE}/${id}`, {
    method: 'PUT',
    headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
    body: JSON.stringify(task),
  });
  return handleResponse<Task>(response);
}

export async function deleteTask(id: number): Promise<void> {
  const response = await fetch(`${API_BASE}/${id}`, {
    method: 'DELETE',
    headers: getAuthHeaders(),
  });
  return handleResponse<void>(response);
}

export async function completeTask(id: number, logData?: TaskLogCreate): Promise<Task> {
  const response = await fetch(`${API_BASE}/${id}/complete`, {
    method: 'POST',
    headers: { ...getAuthHeaders(), 'Content-Type': 'application/json' },
    body: logData ? JSON.stringify(logData) : undefined,
  });
  return handleResponse<Task>(response);
}

export async function getTaskLogs(id: number): Promise<TaskLog[]> {
  const response = await fetch(`${API_BASE}/${id}/logs`, {
    headers: getAuthHeaders(),
  });
  return handleResponse<TaskLog[]>(response);
}
