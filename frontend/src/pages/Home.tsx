import { useState, useEffect, useCallback } from 'react';
import type { Task, TaskCreate, TaskUpdate } from '../types/task';
import { getTasks, createTask, updateTask, deleteTask, completeTask } from '../api/tasks';
import TaskList from '../components/TaskList';
import TaskForm from '../components/TaskForm';
import CompleteDialog from '../components/CompleteDialog';

export default function Home() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Modal states
  const [showForm, setShowForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [completingTask, setCompletingTask] = useState<Task | null>(null);

  const loadTasks = useCallback(async () => {
    try {
      const data = await getTasks();
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

  const handleCreateTask = async (data: TaskCreate | TaskUpdate) => {
    await createTask(data as TaskCreate);
    setShowForm(false);
    await loadTasks();
  };

  const handleUpdateTask = async (data: TaskCreate | TaskUpdate) => {
    if (!editingTask) return;
    await updateTask(editingTask.id, data as TaskUpdate);
    setEditingTask(null);
    await loadTasks();
  };

  const handleDeleteTask = async (task: Task) => {
    if (!confirm(`Delete "${task.title}"?`)) return;
    try {
      await deleteTask(task.id);
      await loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    }
  };

  const handleComplete = (task: Task) => {
    if (task.task_type === 'endless') {
      // Show dialog for endless tasks
      setCompletingTask(task);
    } else {
      // Directly complete ending tasks
      handleCompleteEndingTask(task);
    }
  };

  const handleCompleteEndingTask = async (task: Task) => {
    try {
      await completeTask(task.id);
      await loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete task');
    }
  };

  const handleLogTime = async (durationMinutes: number) => {
    if (!completingTask) return;
    await completeTask(completingTask.id, { duration_minutes: durationMinutes });
    setCompletingTask(null);
    await loadTasks();
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
          <h1 className="page-title">Active Tasks</h1>
          <p className="page-subtitle">
            {tasks.length} task{tasks.length !== 1 ? 's' : ''} · Sorted by priority
          </p>
        </div>
        <button className="btn btn-primary btn-lg" onClick={() => setShowForm(true)}>
          + New Task
        </button>
      </div>

      {error && (
        <div className="text-danger mb-lg">{error}</div>
      )}

      <TaskList
        tasks={tasks}
        onEdit={setEditingTask}
        onComplete={handleComplete}
        onDelete={handleDeleteTask}
      />

      {showForm && (
        <TaskForm
          onSubmit={handleCreateTask}
          onCancel={() => setShowForm(false)}
        />
      )}

      {editingTask && (
        <TaskForm
          task={editingTask}
          onSubmit={handleUpdateTask}
          onCancel={() => setEditingTask(null)}
        />
      )}

      {completingTask && (
        <CompleteDialog
          task={completingTask}
          onConfirm={handleLogTime}
          onCancel={() => setCompletingTask(null)}
        />
      )}
    </>
  );
}
