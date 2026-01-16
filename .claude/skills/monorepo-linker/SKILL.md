---
name: monorepo-linker
description: |
  Configure monorepo with shared packages, workspace linking, and coordinated scripts for frontend and backend.
---

# Monorepo Linker

Configure monorepo with shared packages, workspace linking, and coordinated scripts for frontend and backend.

## When to Use This Skill
- User wants frontend and backend in single repository
- User mentions "share types between services"
- User needs coordinated development workflow
- User wants shared utilities or configs

## Procedure
1. **Choose monorepo tool**: npm workspaces, pnpm, yarn, turborepo, nx
2. **Setup workspace structure**: apps/ and packages/ directories
3. **Configure package linking**: Internal package references
4. **Create shared packages**: types, utils, configs
5. **Setup coordinated scripts**: dev, build, test across workspace

## Output Format
**Monorepo Structure**:
- Root package.json with workspaces
- Apps directory (frontend, backend)
- Packages directory (shared code)
- Build and dev scripts
- TypeScript project references

## Quality Criteria
- Fast dependency installation with workspace hoisting
- Hot reload works across packages
- Shared types stay in sync
- Single command to start all services
- Proper TypeScript path mapping
- Isolated builds per package

## Example
**Input**: "Setup monorepo with React frontend, FastAPI backend, and shared types"

**Output**:

**Directory Structure**:
```
my-app/
├── package.json              # Root workspace config
├── pnpm-workspace.yaml       # or yarn/npm workspaces
├── turbo.json                # Optional: Turborepo config
├── apps/
│   ├── frontend/             # React app
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   └── src/
│   └── backend/              # FastAPI backend
│       ├── pyproject.toml
│       ├── main.py
│       └── models/
├── packages/
│   ├── types/                # Shared TypeScript types
│   │   ├── package.json
│   │   └── src/
│   ├── ui/                   # Shared UI components
│   │   ├── package.json
│   │   └── src/
│   └── config/               # Shared configs (eslint, tsconfig)
│       ├── package.json
│       └── tsconfig.base.json
└── scripts/
    ├── dev.sh                # Start all services
    └── sync-types.py         # Sync Pydantic → TS
```

**Root package.json** (pnpm):
```json
{
  "name": "my-app-monorepo",
  "private": true,
  "scripts": {
    "dev": "concurrently \"npm:dev:*\"",
    "dev:frontend": "pnpm --filter frontend dev",
    "dev:backend": "pnpm --filter backend dev",
    "build": "turbo run build",
    "test": "turbo run test",
    "sync-types": "python scripts/sync-types.py",
    "lint": "turbo run lint",
    "type-check": "turbo run type-check"
  },
  "devDependencies": {
    "turbo": "^1.10.0",
    "concurrently": "^8.0.0"
  }
}
```

**pnpm-workspace.yaml**:
```yaml
packages:
  - 'apps/*'
  - 'packages/*'
```

**Frontend package.json**:
```json
{
  "name": "frontend",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "@my-app/types": "workspace:*",
    "@my-app/ui": "workspace:*"
  },
  "devDependencies": {
    "@my-app/config": "workspace:*",
    "vite": "^5.0.0"
  }
}
```

**Frontend vite.config.ts**:
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@my-app/types': path.resolve(__dirname, '../../packages/types/src'),
      '@my-app/ui': path.resolve(__dirname, '../../packages/ui/src')
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
```

**Shared Types Package** (`packages/types/package.json`):
```json
{
  "name": "@my-app/types",
  "version": "1.0.0",
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "exports": {
    ".": "./src/index.ts"
  }
}
```

**Shared Types** (`packages/types/src/index.ts`):
```typescript
// Auto-generated from backend Pydantic models
export interface User {
  id: string;
  email: string;
  name: string;
  created_at: string;
}

export interface Post {
  id: string;
  title: string;
  content: string;
  author_id: string;
  created_at: string;
}

export interface CreatePostRequest {
  title: string;
  content: string;
}

export interface ApiError {
  error_code: string;
  message: string;
  detail?: any;
}
```

**Backend Structure**:
```
apps/backend/
├── pyproject.toml
├── main.py
├── models/
│   ├── __init__.py
│   ├── user.py
│   └── post.py
└── scripts/
    └── generate_openapi.py
```

**Backend pyproject.toml**:
```toml
[project]
name = "backend"
version = "1.0.0"

[project.scripts]
dev = "uvicorn main:app --reload --port 8000"
generate-openapi = "python scripts/generate_openapi.py"
```

**Type Sync Script** (`scripts/sync-types.py`):
```python
#!/usr/bin/env python3
"""
Generate TypeScript types from Pydantic models
"""
import json
from pathlib import Path
from apps.backend.main import app

# Generate OpenAPI spec
openapi_spec = app.openapi()

# Write to temp file
openapi_path = Path("./temp/openapi.json")
openapi_path.parent.mkdir(exist_ok=True)
openapi_path.write_text(json.dumps(openapi_spec, indent=2))

# Convert to TypeScript using openapi-typescript
import subprocess
subprocess.run([
    "pnpm", "exec", "openapi-typescript",
    str(openapi_path),
    "-o", "packages/types/src/generated.ts"
])

print("✅ Types synced successfully")
```

**Turborepo Config** (`turbo.json`):
```json
{
  "$schema": "https://turbo.build/schema.json",
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", "build/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {
      "dependsOn": ["^build"]
    },
    "type-check": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["^build"]
    }
  }
}
```

**Root TypeScript Config** (`packages/config/tsconfig.base.json`):
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM"],
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "paths": {
      "@my-app/types": ["../../packages/types/src"],
      "@my-app/ui": ["../../packages/ui/src"]
    }
  }
}
```

**Frontend tsconfig.json**:
```json
{
  "extends": "@my-app/config/tsconfig.base.json",
  "compilerOptions": {
    "baseUrl": ".",
    "outDir": "./dist"
  },
  "include": ["src"]
}
```

**Development Script** (`scripts/dev.sh`):
```bash
#!/bin/bash

echo "🚀 Starting monorepo development..."

# Start backend
cd apps/backend
python -m uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ../frontend
pnpm dev &
FRONTEND_PID=$!

# Cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
```

## Alternative Monorepo Tools

### Yarn Workspaces
```json
// package.json
{
  "name": "my-app-monorepo",
  "private": true,
  "workspaces": [
    "apps/*",
    "packages/*"
  ],
  "scripts": {
    "dev": "yarn workspaces foreach -pv --topological-dev run dev",
    "build": "yarn workspaces foreach -p run build"
  }
}
```

### Nx Configuration
```json
// nx.json
{
  "targetDefaults": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["{projectRoot}/dist"]
    },
    "test": {
      "dependsOn": ["^build"]
    }
  },
  "namedInputs": {
    "default": ["{projectRoot}/**/*", "sharedGlobals"],
    "sharedGlobals": []
  }
}
```

## Python Monorepo Setup

### Poetry Workspaces
```toml
# pyproject.toml (root)
[tool.poetry]
name = "my-app-monorepo"
version = "0.1.0"
packages = []

[tool.poetry.dependencies]
python = "^3.9"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.group.dev.dependencies]
poetry-plugin-workspace = "^1.0"
```

### Python Package Structure
```
apps/backend/
├── pyproject.toml
├── src/
│   └── my_app/
│       ├── __init__.py
│       ├── api/
│       └── models/
└── tests/

packages/python-utils/
├── pyproject.toml
├── src/
│   └── my_utils/
│       ├── __init__.py
│       └── helpers.py
└── tests/
```

## TypeScript Project References

### tsconfig.json with References
```json
{
  "references": [
    { "path": "../packages/types" },
    { "path": "../packages/config" }
  ],
  "files": [],
  "include": [],
  "compilerOptions": {
    "composite": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  }
}
```

## Shared Configuration Packages

### ESLint Config Package
```json
// packages/eslint-config/package.json
{
  "name": "@my-app/eslint-config",
  "version": "1.0.0",
  "main": "index.js",
  "dependencies": {
    "@typescript-eslint/eslint-plugin": "^6.0.0",
    "@typescript-eslint/parser": "^6.0.0",
    "eslint-plugin-react-hooks": "^4.6.0"
  }
}
```

### Prettier Config Package
```json
// packages/prettier-config/package.json
{
  "name": "@my-app/prettier-config",
  "version": "1.0.0",
  "main": "index.js",
  "peerDependencies": {
    "prettier": "^3.0.0"
  }
}
```

## Deployment Strategies

### Docker Multi-Stage Build
```dockerfile
# Dockerfile
FROM node:18-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install --frozen-lockfile

FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

FROM node:18-alpine AS runner
WORKDIR /app
COPY --from=builder /app/apps/frontend/dist ./frontend-dist
COPY --from=builder /app/apps/backend ./backend
EXPOSE 3000 8000
CMD ["concurrently", "npm:prod:*"]
```

## Performance Optimization

### Turbo Cache Configuration
```json
// .turbo/config.json
{
  "apiUrl": "https://api.turbo.build",
  "loginUrl": "https://vercel.com/dashboard/turborepo",
  "teamId": "your-team-id",
  "cache": {
    "dir": ".turbo/cache"
  }
}
```

### Selective Dependency Building
```json
// turbo.json (with selective builds)
{
  "pipeline": {
    "build": {
      "dependsOn": ["^build"],
      "inputs": ["src/**"],
      "outputs": ["dist/**"]
    }
  }
}
```

## Best Practices
1. **Fast installs**: Use pnpm or Yarn for workspace hoisting
2. **Type safety**: Share types across services
3. **Isolated builds**: Each package builds independently
4. **Coordinated dev**: Single command for all services
5. **Version management**: Consistent dependency versions
6. **CI/CD**: Optimized builds with caching
7. **Code sharing**: Reusable utilities and components
8. **Clear boundaries**: Well-defined package responsibilities

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Current project structure, existing packages, dependency management tools |
| **Conversation** | User's specific monorepo requirements, preferred tools, team workflow |
| **Skill References** | Monorepo best practices, workspace tool comparisons, performance optimization |
| **User Guidelines** | Project-specific naming conventions, deployment requirements, security policies |