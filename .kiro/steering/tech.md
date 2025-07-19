# Technology Stack

## Architecture
- **Frontend**: React 18 with Vite build system
- **Backend**: Python FastAPI with async support
- **Database**: SQLite with SQLAlchemy ORM
- **Containerization**: Docker and Docker Compose
- **RCON**: Custom integration using mcrcon library

## Frontend Stack
- **Framework**: React 18.2.0
- **Build Tool**: Vite 4.5.0
- **Styling**: Tailwind CSS 3.3.5
- **Routing**: React Router DOM 6.18.0
- **HTTP Client**: Axios 1.6.0
- **Icons**: Lucide React 0.292.0
- **Linting**: ESLint with React plugins

## Backend Stack
- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0 with standard extras
- **ORM**: SQLAlchemy 2.0.23 with aiosqlite 0.19.0
- **Docker Integration**: docker-py 6.1.3
- **HTTP Client**: httpx 0.25.2
- **RCON**: mcrcon 0.7.0
- **Environment**: python-dotenv 1.0.0

## Development Commands

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
npm run build
npm run lint
npm run preview
```

### Docker Development
```bash
docker-compose up --build
docker-compose down
```

## Prerequisites
- Docker Desktop installed and running
- Node.js 18+
- Python 3.9+

## Environment Configuration
- Backend runs on port 8000
- Frontend runs on port 3000
- Database: SQLite file-based storage
- Docker socket access required for container management