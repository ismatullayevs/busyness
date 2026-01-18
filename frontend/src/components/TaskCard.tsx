import type { Task } from '../types/task';

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onComplete: (task: Task) => void;
  onDelete: (task: Task) => void;
  isCompleted?: boolean;
}

function getPriorityLevel(score: number): 'low' | 'medium' | 'high' | 'critical' {
  if (score <= 3) return 'low';
  if (score <= 5) return 'medium';
  if (score <= 7) return 'high';
  return 'critical';
}

function formatDeadline(deadline: string): { text: string; urgency: string } {
  const now = new Date();
  const deadlineDate = new Date(deadline);
  const diffMs = deadlineDate.getTime() - now.getTime();
  const diffDays = diffMs / (1000 * 60 * 60 * 24);

  if (diffDays < 0) {
    return { text: 'Overdue!', urgency: 'urgent' };
  } else if (diffDays < 1) {
    const hours = Math.floor(diffMs / (1000 * 60 * 60));
    return { text: `${hours}h left`, urgency: 'urgent' };
  } else if (diffDays < 3) {
    return { text: `${Math.floor(diffDays)}d left`, urgency: 'soon' };
  } else {
    return { text: `${Math.floor(diffDays)}d left`, urgency: '' };
  }
}

export default function TaskCard({ task, onEdit, onComplete, onDelete, isCompleted }: TaskCardProps) {
  const priorityLevel = getPriorityLevel(task.priority_score);
  const priorityPercent = (task.priority_score / 10) * 100;
  
  const deadlineInfo = task.deadline ? formatDeadline(task.deadline) : null;

  return (
    <div className={`task-card ${isCompleted ? 'completed' : ''}`}>
      <div className="task-card-header">
        <div>
          <h3 className="task-title">{task.title}</h3>
        </div>
        {!isCompleted && (
          <div className="priority-indicator">
            <div className="priority-bar">
              <div
                className={`priority-bar-fill ${priorityLevel}`}
                style={{ width: `${priorityPercent}%` }}
              />
            </div>
            <span className={`priority-score ${priorityLevel}`}>
              {task.priority_score.toFixed(1)}
            </span>
          </div>
        )}
      </div>

      {task.description && (
        <p className="task-description">{task.description}</p>
      )}

      <div className="task-meta">
        <span className={`task-badge ${task.task_type}`}>
          {task.task_type === 'ending' ? '⏱️ Ending' : '♾️ Endless'}
        </span>
        {deadlineInfo && (
          <span className={`task-deadline ${deadlineInfo.urgency}`}>
            📅 {deadlineInfo.text}
          </span>
        )}
      </div>

      <div className="task-actions">
        {!isCompleted && (
          <>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => onEdit(task)}
            >
              ✏️ Edit
            </button>
            <button
              className="btn btn-success btn-sm"
              onClick={() => onComplete(task)}
            >
              ✓ {task.task_type === 'endless' ? 'Log Time' : 'Complete'}
            </button>
          </>
        )}
        <button
          className="btn btn-ghost btn-sm"
          onClick={() => onDelete(task)}
        >
          🗑️
        </button>
      </div>
    </div>
  );
}
