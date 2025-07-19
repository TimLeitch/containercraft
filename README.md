# ContainerCraft

A modern web application for managing Minecraft modpack servers through Docker containers. Browse and select modpacks from CurseForge, deploy servers instantly, and manage configurations through an intuitive GUI.

## Features

- 🎮 **Modpack Discovery**: Browse and select modpacks from CurseForge API
- 🐳 **One-Click Deployment**: Automatic Docker container deployment with intelligent configuration
- ⚙️ **Smart Configuration**: Dynamic UI controls (sliders, toggles, dropdowns) based on config types
- 📱 **Responsive Design**: Modern web interface optimized for desktop and mobile
- 🖥️ **Multi-Server Management**: Run and manage multiple modpack servers simultaneously
- 🎛️ **RCON Integration**: Execute server commands remotely with built-in terminal
- 💾 **Configuration Templates**: Save and reuse server configurations across deployments
- 🔄 **Cross-Platform**: Compatible with Windows, macOS, and Linux via Docker

## Architecture

ContainerCraft uses a modern full-stack architecture:

- **Frontend**: React 18 with Vite, Tailwind CSS, and React Router
- **Backend**: FastAPI with async support and SQLAlchemy ORM
- **Database**: SQLite for lightweight, file-based storage
- **Containerization**: Docker for Minecraft server isolation and management
- **API Integration**: CurseForge API for modpack discovery and metadata

## Prerequisites

- **Docker Desktop** installed and running
- **Node.js 18+** for frontend development
- **Python 3.9+** for backend development

## Quick Start

### Option 1: Docker Compose (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd containercraft

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

### Option 2: Manual Development Setup

#### Backend Setup
```bash
cd backend

# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python database.py init

# Start development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
containercraft/
├── frontend/                    # React + Vite frontend application
│   ├── src/
│   │   ├── components/         # Reusable React components
│   │   ├── pages/             # Page-level components
│   │   └── utils/             # Frontend utilities
│   ├── package.json           # Frontend dependencies
│   └── vite.config.js         # Vite configuration
├── backend/                     # FastAPI backend application
│   ├── models/                # SQLAlchemy database models
│   │   ├── base.py           # Database base configuration
│   │   ├── server.py         # Server instance models
│   │   └── configuration.py  # Configuration models
│   ├── services/              # Business logic services
│   │   └── modpack_service.py # CurseForge API integration
│   ├── routes/                # API endpoint definitions
│   ├── database.py            # Database initialization
│   ├── migrations.py          # Database migration system
│   └── requirements.txt       # Backend dependencies
├── .kiro/                      # Kiro AI assistant configuration
│   ├── specs/                 # Project specifications
│   └── steering/              # Development guidelines
├── docker-compose.yml          # Multi-service orchestration
└── README.md                   # This file
```

## Technology Stack

### Frontend Dependencies
- **React** 18.2.0 - UI framework
- **Vite** 4.5.0 - Build tool and dev server
- **Tailwind CSS** 3.3.5 - Utility-first CSS framework
- **React Router DOM** 6.18.0 - Client-side routing
- **Axios** 1.6.0 - HTTP client for API communication
- **Lucide React** 0.292.0 - Icon library

### Backend Dependencies
- **FastAPI** 0.104.1 - Modern Python web framework
- **Uvicorn** 0.24.0 - ASGI server
- **Pydantic** >=2.8.0 - Data validation and serialization
- **SQLAlchemy** 2.0.23 - SQL toolkit and ORM
- **aiosqlite** 0.19.0 - Async SQLite driver
- **docker** 6.1.3 - Docker Python SDK
- **httpx** 0.25.2 - Async HTTP client
- **mcrcon** 0.7.0 - Minecraft RCON client
- **python-dotenv** 1.0.0 - Environment variable management

## Development Workflow

### Git Strategy
- **`main`** - Production-ready code
- **`dev`** - Development integration branch
- **`feature/*`** - Individual feature branches

### Development Commands

#### Backend Development
```bash
cd backend

# Run tests
python -m pytest

# Run specific test file
python test_models.py

# Database operations
python database.py init     # Initialize database
python database.py reset    # Reset database
python database.py check    # Check database status
python database.py info     # Show database info

# Migration management
python migrations.py up     # Apply pending migrations
python migrations.py down   # Rollback migrations
python migrations.py status # Show migration status
```

#### Frontend Development
```bash
cd frontend

# Development server
npm run dev

# Linting
npm run lint

# Build for production
npm run build

# Preview production build
npm run preview
```

### Feature Development Process
1. Create feature branch from `dev`: `git checkout -b feature/your-feature-name`
2. Implement changes with frequent commits
3. Test thoroughly (backend tests, frontend linting)
4. Submit PR to `dev` branch
5. After review and approval, merge to `dev`
6. Deploy to production by merging `dev` to `main`

## API Documentation

The backend provides a RESTful API with the following main endpoints:

- **`/api/v1/modpacks/`** - CurseForge modpack operations
- **`/api/v1/servers/`** - Server lifecycle management
- **`/api/v1/configs/`** - Configuration template management
- **`/api/v1/rcon/`** - Server command execution

API documentation is available at `http://localhost:8000/docs` when running the backend.

## Database Schema

The application uses SQLite with three main models:

- **ServerInstance** - Represents deployed Minecraft servers
- **ConfigurationTemplate** - Saved server configurations for reuse
- **ConfigurationEntry** - Individual configuration key-value pairs with UI metadata

## Docker Integration

ContainerCraft manages Minecraft servers through Docker containers:

- Each server runs in an isolated container
- Automatic port allocation and network configuration
- Volume mounting for persistent world data
- Container lifecycle management (start, stop, remove)
- Resource monitoring and cleanup

## Contributing

We welcome contributions! Please follow these guidelines:

1. **Code Style**: Follow the conventions in `.kiro/steering/conventions.md`
2. **Testing**: Ensure all tests pass before submitting PRs
3. **Documentation**: Update documentation for new features
4. **Commits**: Use descriptive commit messages following conventional commits

### Suggested Feature Areas
- **CurseForge Integration** - Enhanced modpack browsing and filtering
- **Configuration UI** - Dynamic form generation and validation
- **Docker Management** - Advanced container orchestration
- **RCON Integration** - Real-time server communication
- **Mobile Optimization** - Touch-friendly interface improvements

## Troubleshooting

### Common Issues

**Docker Permission Errors**
- Ensure Docker Desktop is running
- On Linux, add user to docker group: `sudo usermod -aG docker $USER`

**Port Conflicts**
- Default ports: Frontend (3000), Backend (8000)
- Change ports in docker-compose.yml if needed

**Database Issues**
- Reset database: `python backend/database.py reset`
- Check database status: `python backend/database.py check`

## License

MIT License - see LICENSE file for details

## Support

For questions, issues, or contributions, please refer to the project's issue tracker or documentation in the `.kiro/specs/` directory.