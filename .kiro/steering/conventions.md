# Code Conventions

## Naming Conventions
- **React Components**: PascalCase (`ModpackSelector`, `ServerDashboard`)
- **Functions**: camelCase (`deployServer`, `parseModConfig`)
- **Files**: kebab-case (`modpack-selector.jsx`, `server-deployment.py`)
- **API Endpoints**: snake_case (`/api/modpacks`, `/api/servers/{server_id}/config`)
- **Database Tables**: snake_case (`modpack_configs`, `server_instances`)

## File Organization
- **Components**: `frontend/src/components/`
- **Pages**: `frontend/src/pages/`
- **API Routes**: `backend/routes/`
- **Models**: `backend/models/`
- **Utils**: `backend/utils/` and `frontend/src/utils/`

## Git Commit Messages
- `feat: add modpack selection interface`
- `fix: resolve docker container startup issue`
- `refactor: simplify config parsing logic`
- `docs: update API documentation`

## API Response Format
```json
{
  "success": true,
  "data": {},
  "message": "Optional message",
  "errors": []
}
```