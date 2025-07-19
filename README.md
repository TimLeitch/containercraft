# ContainerCraft

A modern web application for managing Minecraft modpack servers through Docker containers. Select modpacks from CurseForge, deploy servers instantly, and manage configurations through an intuitive GUI.

## Features

- 🎮 Browse and select modpacks from CurseForge
- 🐳 Automatic Docker container deployment
- ⚙️ Dynamic configuration management with intelligent UI controls
- 📱 Responsive web interface (desktop & mobile)
- 🖥️ Multiple server management
- 🎛️ RCON integration for server commands
- 💾 Saveable server configurations
- 🔄 Cross-platform compatibility (Windows/Mac/Linux)

## Prerequisites

- Docker Desktop installed and running
- Node.js 18+ 
- Python 3.9+

## Quick Start

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Project Structure

```
containercraft/
├── frontend/          # React + Vite frontend
├── backend/           # FastAPI backend
├── docker/            # Docker configurations
├── configs/           # Saved server configurations
└── docs/              # Documentation
```

## Development Workflow

- `main` - Production branch
- `dev` - Development integration branch  
- `feature/*` - Individual feature branches

## Tech Stack

- **Frontend**: React, Vite, Tailwind CSS
- **Backend**: Python, FastAPI
- **Database**: SQLite
- **Containerization**: Docker, Docker Compose
- **RCON**: Custom integration for server management

## Contributing

1. Create feature branch from `dev`
2. Make your changes
3. Submit PR to `dev` branch
4. After review, changes get merged to `main`

## License

MIT License - see LICENSE file for details