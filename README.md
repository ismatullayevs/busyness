# Busyness - Smart Prioritization Todo App

A full-stack todo application with intelligent task prioritization based on impact, time decay, and deadlines.

## Features

- **Smart Prioritization**: Tasks are automatically sorted by calculated priority scores
- **Two Task Types**:
  - **Ending Tasks**: One-time tasks that can be completed
  - **Endless Tasks**: Recurring tasks (like exercise) that track time spent
- **Deadline Support**: Priority increases as deadlines approach
- **Impact Tracking**: Dynamic impact scores based on time since last action

## Tech Stack

- **Frontend**: React with Vite
- **Backend**: FastAPI with SQLAlchemy
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Containerization**: Docker Compose with watch mode

## Getting Started

### Prerequisites

- Docker and Docker Compose

### Running the App

1. Clone and navigate to the project:
   ```bash
   cd prioritize
   ```

2. Copy environment file:
   ```bash
   cp .env.example .env
   ```

3. Start the application:
   ```bash
   docker compose up --watch
   ```

4. Access the app:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Development

The project uses Docker Compose watch mode for hot reloading:
- Backend changes in `./backend/app` sync automatically
- Frontend changes in `./frontend/src` sync automatically

### Running Tests

```bash
# Backend tests
docker compose exec backend pytest

# Or run locally
cd backend && uv run pytest
```

## Priority Calculation

```
priority_score = impact_per_hour * (1 + 1/days_before_deadline)

Where impact_per_hour:
- Ending tasks: base_impact + (hours_since_creation * not_doing_rate)
- Endless tasks: base_impact + (hours_since_done * not_doing_rate) - (recent_hours * doing_rate)

Constraints: 0 <= priority_score <= 10
```
