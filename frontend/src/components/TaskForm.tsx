import { useState, useEffect } from 'react';
import type { Task, TaskCreate, TaskUpdate, TaskType } from '../types/task';

interface TaskFormProps {
  task?: Task | null;
  onSubmit: (data: TaskCreate | TaskUpdate) => Promise<void>;
  onCancel: () => void;
}

type CompletionMode = 'rate' | 'set_to';

export default function TaskForm({ task, onSubmit, onCancel }: TaskFormProps) {
  const isEditing = !!task;
  
  const [title, setTitle] = useState(task?.title || '');
  const [description, setDescription] = useState(task?.description || '');
  const [taskType, setTaskType] = useState<TaskType>(task?.task_type || 'ending');
  const [impact, setImpact] = useState(task?.impact?.toString() || '5');
  const [effort, setEffort] = useState(task?.effort?.toString() || '1');
  const [notDoingRate, setNotDoingRate] = useState(task?.not_doing_hourly_rate?.toString() || '0.1');
  const [doingRate, setDoingRate] = useState(task?.doing_hourly_rate?.toString() || '0.1');
  const [impactSetTo, setImpactSetTo] = useState(task?.impact_set_to?.toString() || '0');
  const [completionMode, setCompletionMode] = useState<CompletionMode>(
    task?.impact_set_to !== null && task?.impact_set_to !== undefined ? 'set_to' : 'rate'
  );
  const [deadline, setDeadline] = useState(
    task?.deadline ? new Date(task.deadline).toISOString().slice(0, 16) : ''
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  // Reset form when task changes
  useEffect(() => {
    if (task) {
      setTitle(task.title);
      setDescription(task.description || '');
      setTaskType(task.task_type);
      setImpact(task.impact?.toString() || '5');
      setEffort(task.effort?.toString() || '1');
      setNotDoingRate(task.not_doing_hourly_rate?.toString() || '0.1');
      setDoingRate(task.doing_hourly_rate?.toString() || '0.1');
      setImpactSetTo(task.impact_set_to?.toString() || '0');
      setCompletionMode(task.impact_set_to !== null && task.impact_set_to !== undefined ? 'set_to' : 'rate');
      setDeadline(task.deadline ? new Date(task.deadline).toISOString().slice(0, 16) : '');
    }
  }, [task]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);

    try {
      const impactValue = parseFloat(impact) || 5;
      const effortValue = parseFloat(effort) || 1;
      const notDoingRateValue = parseFloat(notDoingRate) || 0.1;
      const doingRateValue = parseFloat(doingRate) || 0.1;
      const impactSetToValue = parseFloat(impactSetTo) || 0;

      const isEndless = isEditing ? task?.task_type === 'endless' : taskType === 'endless';
      
      const data: TaskCreate | TaskUpdate = isEditing
        ? {
            title,
            description: description || null,
            impact: impactValue,
            effort: effortValue,
            not_doing_hourly_rate: notDoingRateValue,
            doing_hourly_rate: isEndless && completionMode === 'rate' ? doingRateValue : null,
            impact_set_to: isEndless && completionMode === 'set_to' ? impactSetToValue : null,
            deadline: deadline ? new Date(deadline).toISOString() : null,
          }
        : {
            title,
            description: description || null,
            task_type: taskType,
            impact: impactValue,
            effort: effortValue,
            not_doing_hourly_rate: notDoingRateValue,
            doing_hourly_rate: taskType === 'endless' && completionMode === 'rate' ? doingRateValue : null,
            impact_set_to: taskType === 'endless' && completionMode === 'set_to' ? impactSetToValue : null,
            deadline: deadline ? new Date(deadline).toISOString() : null,
          };

      await onSubmit(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Calculate daily rates for display
  const notDoingDailyRate = ((parseFloat(notDoingRate) || 0) * 24).toFixed(1);
  const doingDailyRate = ((parseFloat(doingRate) || 0) * 24).toFixed(1);
  const isEndless = isEditing ? task?.task_type === 'endless' : taskType === 'endless';

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">{isEditing ? 'Edit Task' : 'New Task'}</h2>
          <button className="modal-close btn btn-ghost" onClick={onCancel}>
            ✕
          </button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && (
              <div className="text-danger mb-md">{error}</div>
            )}
            
            <div className="form-group">
              <label className="form-label">Title *</label>
              <input
                type="text"
                className="form-input"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="What needs to be done?"
                required
                autoFocus
              />
            </div>

            <div className="form-group">
              <label className="form-label">Description</label>
              <textarea
                className="form-textarea"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Add more details..."
              />
            </div>

            {!isEditing && (
              <div className="form-group">
                <label className="form-label">Task Type</label>
                <select
                  className="form-select"
                  value={taskType}
                  onChange={(e) => setTaskType(e.target.value as TaskType)}
                >
                  <option value="ending">⏱️ Ending Task - Can be completed</option>
                  <option value="endless">♾️ Endless Task - Track time spent</option>
                </select>
                <p className="form-hint">
                  {taskType === 'ending'
                    ? 'One-time tasks that you can mark as complete'
                    : 'Recurring tasks like exercise - log time spent instead of completing'}
                </p>
              </div>
            )}

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Current Impact (0-10)</label>
                <input
                  type="number"
                  className="form-input"
                  value={impact}
                  onChange={(e) => setImpact(e.target.value)}
                  min="0"
                  max="10"
                  step="0.1"
                />
                <p className="form-hint">How important is this task right now?</p>
              </div>

              <div className="form-group">
                <label className="form-label">Effort (hours)</label>
                <input
                  type="number"
                  className="form-input"
                  value={effort}
                  onChange={(e) => setEffort(e.target.value)}
                  min="0.1"
                  step="0.1"
                />
                <p className="form-hint">Hours to accomplish this task</p>
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">
                Not-Doing Rate (impact/hour)
                <span className="text-muted"> = {notDoingDailyRate}/day</span>
              </label>
              <input
                type="number"
                className="form-input"
                value={notDoingRate}
                onChange={(e) => setNotDoingRate(e.target.value)}
                min="0"
                step="0.01"
              />
              <p className="form-hint">How much impact increases per hour of not doing this task</p>
            </div>

            {isEndless && (
              <div className="form-group">
                <label className="form-label">When task is done:</label>
                <div className="form-row" style={{ marginBottom: 'var(--spacing-sm)' }}>
                  <label className="flex gap-sm" style={{ cursor: 'pointer' }}>
                    <input
                      type="radio"
                      name="completionMode"
                      checked={completionMode === 'rate'}
                      onChange={() => setCompletionMode('rate')}
                    />
                    Decrease by rate
                  </label>
                  <label className="flex gap-sm" style={{ cursor: 'pointer' }}>
                    <input
                      type="radio"
                      name="completionMode"
                      checked={completionMode === 'set_to'}
                      onChange={() => setCompletionMode('set_to')}
                    />
                    Set to fixed value
                  </label>
                </div>

                {completionMode === 'rate' ? (
                  <div>
                    <label className="form-label">
                      Doing Rate (impact/hour)
                      <span className="text-muted"> = {doingDailyRate}/day</span>
                    </label>
                    <input
                      type="number"
                      className="form-input"
                      value={doingRate}
                      onChange={(e) => setDoingRate(e.target.value)}
                      min="0"
                      step="0.01"
                    />
                    <p className="form-hint">Impact decrease per hour of doing this task</p>
                  </div>
                ) : (
                  <div>
                    <label className="form-label">Set Impact To (0-10)</label>
                    <input
                      type="number"
                      className="form-input"
                      value={impactSetTo}
                      onChange={(e) => setImpactSetTo(e.target.value)}
                      min="0"
                      max="10"
                      step="0.1"
                    />
                    <p className="form-hint">Impact will be set to this value when you log activity</p>
                  </div>
                )}
              </div>
            )}

            <div className="form-group">
              <label className="form-label">Deadline (optional)</label>
              <input
                type="datetime-local"
                className="form-input"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
              />
              <p className="form-hint">Tasks with closer deadlines get higher priority</p>
            </div>
          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting || !title.trim()}
            >
              {isSubmitting ? 'Saving...' : isEditing ? 'Save Changes' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
