import type { Task } from '../types/task';
import TaskCard from './TaskCard';

interface TaskListProps {
  tasks: Task[];
  onEdit: (task: Task) => void;
  onComplete: (task: Task) => void;
  onDelete: (task: Task) => void;
  isCompleted?: boolean;
}

export default function TaskList({ tasks, onEdit, onComplete, onDelete, isCompleted }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <div className="empty-state">
        <div className="empty-state-icon">
          {isCompleted ? '🎉' : '📝'}
        </div>
        <h3 className="empty-state-title">
          {isCompleted ? 'No completed tasks yet' : 'No tasks yet'}
        </h3>
        <p className="empty-state-text">
          {isCompleted
            ? 'Tasks you complete will show up here'
            : 'Create your first task to get started with smart prioritization'}
        </p>
      </div>
    );
  }

  return (
    <div className="task-list">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onEdit={onEdit}
          onComplete={onComplete}
          onDelete={onDelete}
          isCompleted={isCompleted}
        />
      ))}
    </div>
  );
}
