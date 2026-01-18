export type TaskType = 'ending' | 'endless';

export interface TaskLog {
  id: number;
  task_id: number;
  logged_at: string;
  duration_minutes: number;
}

export interface Task {
  id: number;
  title: string;
  description: string | null;
  task_type: TaskType;
  impact: number;
  effort: number;
  not_doing_hourly_rate: number;
  doing_hourly_rate: number | null;
  impact_set_to: number | null;
  deadline: string | null;
  created_at: string;
  last_updated: string;
  completed_at: string | null;
  priority_score: number;
}

export interface TaskWithLogs extends Task {
  logs: TaskLog[];
}

export interface TaskCreate {
  title: string;
  description?: string | null;
  task_type?: TaskType;
  impact?: number;
  effort?: number;
  not_doing_hourly_rate?: number;
  doing_hourly_rate?: number | null;
  impact_set_to?: number | null;
  deadline?: string | null;
}

export interface TaskUpdate {
  title?: string;
  description?: string | null;
  impact?: number;
  effort?: number;
  not_doing_hourly_rate?: number;
  doing_hourly_rate?: number | null;
  impact_set_to?: number | null;
  deadline?: string | null;
}

export interface TaskLogCreate {
  duration_minutes: number;
}
