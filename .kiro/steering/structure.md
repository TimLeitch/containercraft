# Project Structure

## Root Directory Layout
```
containercraft/
├── frontend/          # React + Vite frontend application
├── backend/           # FastAPI backend application
├── docker/            # Docker configurations and templates
├── configs/           # Saved server configurations
├── docs/              # Project documentation
├── docker-compose.yml # Multi-service container orchestration
└── README.md          # Project overview and setup instructions
```

## Frontend Structure (`frontend/`)
- React application built with Vite
- Tailwind CSS for styling
- Component-based architecture
- Responsive design for desktop and mobile
- Axios for API communication with backend

## Backend Structure (`backend/`)
- FastAPI application with async support
- SQLAlchemy models for database operations
- Docker integration for container management
- RCON client for Minecraft server communication
- RESTful API endpoints for frontend consumption

## Configuration Management
- `configs/` directory stores saved server configurations
- Docker socket mounted for container lifecycle management
- Environment variables for service configuration
- SQLite database for persistent data storage

## Development Workflow
- **Branching Strategy**: 
  - `main` - Production branch
  - `dev` - Development integration branch
  - `feature/*` - Individual feature branches
- **Development**: Use Docker Compose for full-stack development
- **Testing**: Frontend linting with ESLint, backend testing with FastAPI test client

## Key Conventions
- Frontend uses ES modules and modern React patterns
- Backend follows FastAPI async/await patterns
- Docker containers for consistent development environment
- Volume mounts for hot reloading during development
- Separate Dockerfiles for frontend and backend services