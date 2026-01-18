import { useState, useEffect, useCallback } from 'react';
import type { Task } from '../types/task';
import { getCompletedTasks, deleteTask } from '../api/tasks';
import TaskList from '../components/TaskList';

export default function Completed() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const loadTasks = useCallback(async () => {
    try {
      const data = await getCompletedTasks();
      setTasks(data);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleDeleteTask = async (task: Task) => {
    if (!confirm(`Delete "${task.title}" permanently?`)) return;
    try {
      await deleteTask(task.id);
      await loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    }
  };

  if (isLoading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <>
      <div className="page-header">
        <div>
          <h1 className="page-title">Completed Tasks</h1>
          <p className="page-subtitle">
            {tasks.length} completed task{tasks.length !== 1 ? 's' : ''}
          </p>
        </div>
      </div>

      {error && (
        <div className="text-danger mb-lg">{error}</div>
      )}

      <TaskList
        tasks={tasks}
        onEdit={() => {}}
        onComplete={() => {}}
        onDelete={handleDeleteTask}
        isCompleted
      />
    </>
  );
}
