import { useState } from 'react';
import type { Task } from '../types/task';

interface CompleteDialogProps {
  task: Task;
  onConfirm: (durationMinutes: number) => Promise<void>;
  onCancel: () => void;
}

export default function CompleteDialog({ task, onConfirm, onCancel }: CompleteDialogProps) {
  const [hours, setHours] = useState(1);
  const [minutes, setMinutes] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const totalMinutes = hours * 60 + minutes;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (totalMinutes <= 0) {
      setError('Please enter a valid duration');
      return;
    }

    setError('');
    setIsSubmitting(true);

    try {
      await onConfirm(totalMinutes);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">Log Time</h2>
          <button className="modal-close btn btn-ghost" onClick={onCancel}>
            ✕
          </button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            <p className="text-secondary mb-lg">
              How much time did you spend on <strong>"{task.title}"</strong>?
            </p>

            {error && (
              <div className="text-danger mb-md">{error}</div>
            )}

            <div className="form-row">
              <div className="form-group">
                <label className="form-label">Hours</label>
                <input
                  type="number"
                  className="form-input"
                  min="0"
                  max="24"
                  value={hours}
                  onChange={(e) => setHours(Math.max(0, parseInt(e.target.value) || 0))}
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label className="form-label">Minutes</label>
                <input
                  type="number"
                  className="form-input"
                  min="0"
                  max="59"
                  value={minutes}
                  onChange={(e) => setMinutes(Math.max(0, Math.min(59, parseInt(e.target.value) || 0)))}
                />
              </div>
            </div>

            <p className="text-muted text-center">
              Total: <strong>{totalMinutes}</strong> minutes
            </p>
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
              className="btn btn-success"
              disabled={isSubmitting || totalMinutes <= 0}
            >
              {isSubmitting ? 'Logging...' : 'Log Time'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
