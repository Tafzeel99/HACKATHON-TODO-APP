---
name: env-synchronizer
description: |
  Align and validate environment variables across frontend, backend, and deployment services with type safety.
---

# Environment Synchronizer

Align and validate environment variables across frontend, backend, and deployment services with type safety.

## When to Use This Skill
- User has mismatched env vars between services
- User mentions "config not working" or "env vars missing"
- User deploying to new environment
- User wants type-safe environment configuration

## Procedure
1. **Define shared config schema**: What vars each service needs
2. **Create env template**: Document all required variables
3. **Generate type-safe loaders**: Validate and parse env vars
4. **Sync across environments**: dev, staging, production
5. **Add validation**: Check for missing/invalid values on startup

## Output Format
**Configuration System**:
- Shared env schema (JSON/YAML)
- Type-safe env loaders per service
- Validation logic
- Example .env files

## Quality Criteria
- Type validation: Numbers are numbers, booleans are booleans
- Required vs optional clearly marked
- Default values where sensible
- Environment-specific overrides (dev vs prod)
- Fail fast on missing required vars

## Example
**Input**: "Sync environment variables between my React frontend and FastAPI backend"

**Output**:

**Shared Schema** (`config.schema.json`):
```json
{
  "shared": {
    "API_BASE_URL": {
      "type": "string",
      "required": true,
      "description": "Base URL for API calls"
    },
    "ENVIRONMENT": {
      "type": "enum",
      "values": ["development", "staging", "production"],
      "required": true
    }
  },
  "backend": {
    "DATABASE_URL": {
      "type": "string",
      "required": true,
      "description": "PostgreSQL connection string"
    },
    "JWT_SECRET": {
      "type": "string",
      "required": true,
      "sensitive": true
    },
    "CORS_ORIGINS": {
      "type": "array",
      "required": true,
      "description": "Allowed frontend origins"
    },
    "PORT": {
      "type": "number",
      "required": false,
      "default": 8000
    }
  },
  "frontend": {
    "VITE_API_URL": {
      "type": "string",
      "required": true,
      "description": "API endpoint for frontend"
    },
    "VITE_GOOGLE_ANALYTICS_ID": {
      "type": "string",
      "required": false
    }
  }
}
```

**Backend Loader** (`backend/config.py`):
```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Shared
    API_BASE_URL: str
    ENVIRONMENT: str

    # Backend specific
    DATABASE_URL: str
    JWT_SECRET: str
    CORS_ORIGINS: List[str]
    PORT: int = 8000

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Validate environment
        if self.ENVIRONMENT not in ["development", "staging", "production"]:
            raise ValueError(f"Invalid ENVIRONMENT: {self.ENVIRONMENT}")

settings = Settings()

# Usage
print(f"Starting on port {settings.PORT}")
```

**Frontend Loader** (`frontend/src/config.ts`):
```typescript
interface Config {
  apiUrl: string;
  environment: 'development' | 'staging' | 'production';
  googleAnalyticsId?: string;
}

function loadConfig(): Config {
  const apiUrl = import.meta.env.VITE_API_URL;
  const environment = import.meta.env.VITE_ENVIRONMENT || 'development';

  // Validate required vars
  if (!apiUrl) {
    throw new Error('VITE_API_URL is required');
  }

  if (!['development', 'staging', 'production'].includes(environment)) {
    throw new Error(`Invalid VITE_ENVIRONMENT: ${environment}`);
  }

  return {
    apiUrl,
    environment: environment as Config['environment'],
    googleAnalyticsId: import.meta.env.VITE_GOOGLE_ANALYTICS_ID
  };
}

export const config = loadConfig();

// Usage
console.log(`API: ${config.apiUrl}`);
```

**Environment Files**:

`.env.development`:
```bash
# Shared
ENVIRONMENT=development
API_BASE_URL=http://localhost:8000

# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/mydb_dev
JWT_SECRET=dev-secret-change-in-production
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
PORT=8000

# Frontend (Vite)
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

`.env.production`:
```bash
# Shared
ENVIRONMENT=production
API_BASE_URL=https://api.myapp.com

# Backend
DATABASE_URL=${DATABASE_URL}  # Set in hosting provider
JWT_SECRET=${JWT_SECRET}      # Set in hosting provider
CORS_ORIGINS=https://myapp.com,https://www.myapp.com
PORT=8000

# Frontend
VITE_API_URL=https://api.myapp.com
VITE_ENVIRONMENT=production
VITE_GOOGLE_ANALYTICS_ID=G-XXXXXXXXXX
```

**Validation Script** (`scripts/validate-env.sh`):
```bash
#!/bin/bash

echo "🔍 Validating environment variables..."

# Check backend
cd backend
python -c "from config import settings; print('✅ Backend config valid')" || exit 1

# Check frontend
cd ../frontend
npm run validate:env || exit 1

echo "✅ All environment variables valid"
```

**package.json** (frontend):
```json
{
  "scripts": {
    "validate:env": "ts-node scripts/validate-env.ts"
  }
}
```

## Configuration Schema Generator

### Schema Parser
```python
# config_schema.py
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import json
import yaml

@dataclass
class EnvVarDefinition:
    type: str
    required: bool
    description: str
    default: Optional[Any] = None
    values: Optional[List[str]] = None
    sensitive: bool = False

class ConfigSchema:
    def __init__(self, schema_path: str):
        with open(schema_path, 'r') as f:
            self.schema_data = json.load(f)

    def get_service_vars(self, service: str) -> Dict[str, EnvVarDefinition]:
        """Get environment variables for a specific service"""
        service_vars = self.schema_data.get(service, {})
        result = {}

        for var_name, var_config in service_vars.items():
            result[var_name] = EnvVarDefinition(
                type=var_config['type'],
                required=var_config.get('required', False),
                description=var_config.get('description', ''),
                default=var_config.get('default'),
                values=var_config.get('values'),
                sensitive=var_config.get('sensitive', False)
            )

        return result

    def validate_environment(self, service: str, env_dict: Dict[str, str]) -> List[str]:
        """Validate environment variables against schema"""
        service_vars = self.get_service_vars(service)
        errors = []

        for var_name, var_def in service_vars.items():
            value = env_dict.get(var_name)

            if var_def.required and not value:
                errors.append(f"Missing required environment variable: {var_name}")

            if value and var_def.type == 'number':
                try:
                    int(value)
                except ValueError:
                    errors.append(f"Invalid number for {var_name}: {value}")

            if value and var_def.type == 'boolean':
                if value.lower() not in ['true', 'false', '1', '0']:
                    errors.append(f"Invalid boolean for {var_name}: {value}")

            if value and var_def.type == 'enum' and var_def.values:
                if value not in var_def.values:
                    errors.append(f"Invalid value for {var_name}: {value}. Must be one of {var_def.values}")

        return errors
```

## Type-Safe Loaders

### Python Config Loader
```python
# config_loader.py
import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, ValidationError
from config_schema import ConfigSchema

class ConfigLoader:
    def __init__(self, schema_path: str):
        self.schema = ConfigSchema(schema_path)

    def load_service_config(self, service: str) -> Dict[str, Any]:
        """Load and validate configuration for a service"""
        service_vars = self.schema.get_service_vars(service)
        config = {}

        for var_name, var_def in service_vars.items():
            value = os.getenv(var_name)

            if var_def.required and value is None:
                if var_def.default is not None:
                    value = str(var_def.default)
                else:
                    raise ValueError(f"Missing required environment variable: {var_name}")

            if value is not None:
                # Convert to appropriate type
                config[var_name] = self._convert_type(value, var_def.type)
            else:
                config[var_name] = var_def.default

        # Validate final config
        errors = self.schema.validate_environment(service, config)
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")

        return config

    def _convert_type(self, value: str, var_type: str) -> Any:
        """Convert string value to appropriate type"""
        if var_type == 'string':
            return value
        elif var_type == 'number':
            return int(value)
        elif var_type == 'boolean':
            return value.lower() in ['true', '1', 'yes', 'on']
        elif var_type == 'array':
            return [item.strip() for item in value.split(',')]
        else:
            return value

# Usage
loader = ConfigLoader('config.schema.json')
backend_config = loader.load_service_config('backend')
```

### TypeScript Config Loader
```typescript
// config/loader.ts
interface SchemaVar {
  type: string;
  required: boolean;
  description: string;
  default?: any;
  values?: string[];
  sensitive?: boolean;
}

interface Schema {
  [service: string]: {
    [varName: string]: SchemaVar;
  };
}

export class ConfigLoader {
  private schema: Schema;

  constructor(schemaPath: string) {
    // In real implementation, load schema from file
    this.schema = this.loadSchema(schemaPath);
  }

  loadServiceConfig(service: string): Record<string, any> {
    const serviceVars = this.schema[service] || {};
    const config: Record<string, any> = {};

    for (const [varName, varDef] of Object.entries(serviceVars)) {
      const value = process.env[varName] || varDef.default;

      if (varDef.required && value === undefined) {
        throw new Error(`Missing required environment variable: ${varName}`);
      }

      if (value !== undefined) {
        config[varName] = this.convertType(value, varDef.type);
      } else {
        config[varName] = varDef.default;
      }
    }

    return config;
  }

  private convertType(value: string, type: string): any {
    switch (type) {
      case 'string':
        return value;
      case 'number':
        return parseInt(value, 10);
      case 'boolean':
        return ['true', '1', 'yes', 'on'].includes(value.toLowerCase());
      case 'array':
        return value.split(',').map(item => item.trim());
      default:
        return value;
    }
  }

  private loadSchema(path: string): Schema {
    // Implementation would load schema from file
    return {} as Schema;
  }
}
```

## Environment Validation

### Validation Utilities
```bash
# scripts/validate-environment.sh
#!/bin/bash

set -e

CONFIG_SCHEMA="config.schema.json"

echo "🔍 Validating environment configuration..."

# Validate schema structure
if [[ ! -f "$CONFIG_SCHEMA" ]]; then
  echo "❌ Config schema not found: $CONFIG_SCHEMA"
  exit 1
fi

# Check for required environment variables based on schema
required_vars=($(jq -r '.backend | to_entries[] | select(.value.required == true) | .key' "$CONFIG_SCHEMA"))

missing_vars=()
for var in "${required_vars[@]}"; do
  if [[ -z "${!var}" ]]; then
    missing_vars+=("$var")
  fi
done

if [[ ${#missing_vars[@]} -gt 0 ]]; then
  echo "❌ Missing required environment variables:"
  printf '%s\n' "${missing_vars[@]}"
  exit 1
fi

echo "✅ Environment configuration is valid"
```

### Docker Environment Setup
```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy environment validation script
COPY scripts/validate-environment.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/validate-environment.sh

# Copy schema
COPY config.schema.json .

# Validate environment at container start
CMD ["sh", "-c", "validate-environment.sh && npm start"]
```

## Cross-Environment Sync

### Environment Template Generator
```python
# generate_env_templates.py
from config_schema import ConfigSchema
import os

def generate_env_templates(schema_path: str, output_dir: str):
    """Generate .env templates for different environments"""
    schema = ConfigSchema(schema_path)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Generate templates for each service
    for service in ['backend', 'frontend', 'shared']:
        service_vars = schema.get_service_vars(service)

        template_content = f"# {service.title()} Environment Variables\n\n"
        for var_name, var_def in service_vars.items():
            template_content += f"# {var_def.description}\n"
            if var_def.required:
                template_content += f"# Required: {var_name}="
            else:
                template_content += f"# Optional: [{var_def.default}] {var_name}="
            template_content += "\n\n"

        # Write template
        template_file = os.path.join(output_dir, f".env.{service}.template")
        with open(template_file, 'w') as f:
            f.write(template_content)

        print(f"Generated template: {template_file}")

# Usage
generate_env_templates('config.schema.json', './environments')
```

## Best Practices
1. **Schema first**: Define config schema before implementation
2. **Type safety**: Validate types at runtime
3. **Fail fast**: Stop if required variables are missing
4. **Environment separation**: Different values per environment
5. **Security**: Mark sensitive variables separately
6. **Documentation**: Include descriptions for all variables
7. **Validation**: Check values at startup

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing environment variables, configuration patterns, deployment setup |
| **Conversation** | User's specific environment requirements, service architecture, security needs |
| **Skill References** | Environment management best practices, framework-specific config patterns |
| **User Guidelines** | Project-specific naming conventions, security requirements, deployment targets |