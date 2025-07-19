# Development Practices

## Team Workflow
- **Git Strategy**: Feature branch workflow with regular commits
- **Branching**: `main` → `dev` → `feature/*` branches
- **Collaboration**: Multiple developers working simultaneously
- **Commit Frequency**: Commit early and often to avoid conflicts

## Coding Style Preferences
- **Approach**: Functional programming preferred over OOP when possible
- **UI Philosophy**: Simple, modern, clean interfaces
- **Development Style**: Mix of traditional (tab completion) and vibe coding
- **Testing**: Functional development over test-first approach

## Git Workflow Reminders
- Always create feature branches from `dev`: `git checkout -b feature/your-feature-name`
- Commit frequently with descriptive messages
- Pull latest `dev` changes before starting new features
- Merge feature branches to `dev` first, then `dev` to `main` for production
- Consider rebasing feature branches to keep history clean

## Code Organization Principles
- Keep components small and focused
- Prefer pure functions where possible
- Minimize side effects and state mutations
- Use async/await patterns consistently in backend
- Component composition over inheritance in React

## Development Flow Suggestions
- Start new features with: `git checkout dev && git pull && git checkout -b feature/feature-name`
- Regular commits: `git add . && git commit -m "descriptive message"`
- Before merging: `git checkout dev && git pull && git merge feature/feature-name`
- Deploy to production: `git checkout main && git merge dev`

## Cross-Platform Considerations
- Develop on macOS, target Windows/Mac/Linux
- Docker Desktop requirement for end users
- Test container deployment across platforms
- Use environment variables for platform-specific paths
## Sugg
ested Feature Branches
- `feature/curseforge-api` - CurseForge modpack browsing and selection
- `feature/docker-deployment` - Container creation and management
- `feature/config-ui` - Dynamic configuration interface (sliders, toggles, inputs)
- `feature/mod-configs` - Mod-specific configuration parsing and UI generation
- `feature/rcon-integration` - Server command interface and management

## Feature Branch Focus Areas
- **mod-configs**: Handle the logic for parsing different mod configuration formats, determining appropriate UI controls (slider vs toggle vs input), and mapping config values to UI components
- **config-ui**: Focus on the React components and UI logic for rendering dynamic forms
- **curseforge-api**: Integration with CurseForge API for modpack discovery
- **docker-deployment**: Container lifecycle management and server deployment
- **rcon-integration**: Real-time server communication and command execution