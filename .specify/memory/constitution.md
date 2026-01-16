<!-- SYNC IMPACT REPORT
Version change: 1.3.0 → 2.0.0
Bump rationale: MAJOR - Complete restructuring with 5 core principles (previously 7),
extensive new sections for standards, constraints, success criteria, validation rules,
and decision hierarchy. This is a backward-incompatible governance change.

Modified principles:
- "Spec-First" → "Spec-Driven Development (SDD) - MANDATORY" (expanded)
- "Reusable Intelligence" → Merged into "AI-Native Architecture"
- "User-Centric" → Removed as standalone (incorporated into standards)
- "Security by Default" → Moved to "Security Standards" section
- "Clean Architecture" → Moved to "Production Quality"
- "Cloud-Native" → "Cloud-Native First"
- "AI-Assisted" → "AI-Native Architecture"

Added sections:
- Key Standards (Specification, Code Generation, Technology Stack, Architecture,
  Security, Database, API, Testing)
- Technical Constraints
- Workflow Constraints
- Submission Constraints
- Quality Constraints
- Success Criteria (Phase I-V + Bonus Points)
- Validation Rules (Automated Checks, Disqualification Triggers, Deduction Rules)
- Decision Hierarchy

Removed sections:
- Code Standards table (replaced with comprehensive Code Generation Standards)
- Security Checklist (replaced with comprehensive Security Standards)
- Phase 2 Success Metrics (replaced with all-phase Success Criteria)

Templates requiring updates:
- .specify/templates/plan-template.md ✅ updated
- .specify/templates/spec-template.md ✅ updated
- .specify/templates/tasks-template.md ✅ updated

Follow-up TODOs: none
-->

# Constitution - Evolution of Todo (AI-Native Cloud Application)

**Project**: Hackathon II - The Evolution of Todo
**Version**: 2.0.0
**Ratified**: 2026-01-13
**Last Amended**: 2026-01-16

---

## Core Principles

### 1. Spec-Driven Development (SDD) - MANDATORY

- All code MUST be generated via Claude Code only
- NO manual coding permitted under any circumstance
- Follow strict lifecycle: `Specify → Plan → Tasks → Implement`
- Every implementation MUST reference a Task ID
- Specifications MUST be refined until correct output achieved

### 2. AI-Native Architecture

- Engineer role: System Architect (not code writer)
- Claude Code as primary development tool
- AI agents (OpenAI Agents SDK, MCP) for intelligent features
- Agentic Dev Stack: AGENTS.md + Spec-KitPlus + Claude Code

### 3. Progressive Complexity

- Sequential phase completion mandatory (no skipping)
- Each phase builds on previous foundation
- Architecture progression: CLI → Web → AI Chatbot → K8s → Cloud-Native

### 4. Cloud-Native First

- Stateless design from Phase III onwards
- Containerization mandatory from Phase IV
- Event-driven architecture in Phase V
- Horizontal scalability consideration required

### 5. Production Quality

- Clean code principles enforced
- Security best practices mandatory
- Comprehensive error handling required
- Full documentation expected

---

## Key Standards

### Specification Standards

- Constitution file mandatory for all phases
- All specs in structured `/specs/` directory
- Format: Markdown with clear sections
- Required sections: User stories, Acceptance criteria, Constraints
- Spec-Kit Plus structure:
  ```
  .specify/
  specs/
    overview.md
    architecture.md
    features/*.md
    api/*.md
    database/*.md
    ui/*.md
  ```

### Code Generation Standards

- Source: Claude Code ONLY
- Documentation: All prompts and iterations tracked
- Language standards:
  - Python: PEP 8, type hints, docstrings
  - TypeScript: ESLint, TSDoc comments
  - SQL: Normalization, proper indexing
- NO manual edits to generated code

### Technology Stack Requirements

| Phase | Technologies |
|-------|--------------|
| **Phase I** | Python 3.13+, UV, Claude Code, Spec-Kit Plus |
| **Phase II** | Next.js 16+, FastAPI, SQLModel, Neon PostgreSQL, Better Auth |
| **Phase III** | OpenAI ChatKit, Agents SDK, MCP SDK, FastAPI, Neon DB |
| **Phase IV** | Docker, Minikube, Helm, kubectl-ai, kagent, Gordon |
| **Phase V** | Kafka (Redpanda/Strimzi), Dapr, AKS/GKE/OKE, GitHub Actions |

- NO technology substitutions without justification

### Architecture Standards

- **Structure**: Monorepo with `/frontend` and `/backend`
- **API Design**: RESTful with proper HTTP verbs and status codes
- **Stateless**: JWT tokens only, no server-side sessions
- **Event-Driven**: Kafka topics for async operations (Phase V)
- **Sidecar Pattern**: Dapr for cross-cutting concerns (Phase V)

### Security Standards

- **Authentication**: Better Auth + JWT (from Phase II)
- **Token Management**: 7-day max expiration
- **User Isolation**: Each user sees only their data
- **Secrets**: Environment variables only, never in code
- **Validation**: Backend validation mandatory (never trust client)
- **HTTPS**: Required in production

### Database Standards

- **Normalization**: 3NF minimum
- **Indexing**: Foreign keys + frequently queried columns
- **Timestamps**: created_at, updated_at on all tables
- **Constraints**: Foreign keys, NOT NULL, UNIQUE enforced
- **Migrations**: Tracked and versioned

### API Standards

- **Base Path**: `/api/{user_id}/` for user resources
- **Methods**: GET (read), POST (create), PUT (update), DELETE (delete)
- **Auth Header**: `Authorization: Bearer <token>`
- **Errors**: Proper status codes (401, 403, 404, 500)
- **Rate Limiting**: 100 requests/minute per user

### Testing Standards

- **Coverage**: 70% minimum (Phase I-II), 80% minimum (Phase III-V)
- **Frameworks**: pytest (Python), Jest (TypeScript)
- **Types**: Unit, Integration, E2E tests required
- **Performance**: API < 200ms (95th percentile)

---

## Constraints

### Technical Constraints

- **Windows**: WSL 2 mandatory (Ubuntu 22.04)
- **Docker**: Version 4.53+ for Gordon
- **Node.js**: Version 18+ required
- **Python**: Version 3.13+ required
- **Free Tier Usage**: Neon DB, Vercel, Oracle Cloud (recommended)

### Workflow Constraints

- **Files Required**:
  - AGENTS.md at root
  - CLAUDE.md at root
  - constitution.md at `.specify/memory/`
  - Spec-Kit Plus structure
- **Git Commits**: Conventional Commits format
- **Branch Naming**: `phase-{number}/{feature-name}`

### Submission Constraints

- **Repository**: Public GitHub repo required
- **Demo Video**: Maximum 90 seconds (judges watch only first 90s)
- **Deployment**: URLs MUST be publicly accessible
- **Documentation**: README.md with full setup instructions
- **Timeline**:
  - Phase I: Dec 7, 2025
  - Phase II: Dec 14, 2025
  - Phase III: Dec 21, 2025
  - Phase IV: Jan 4, 2026
  - Phase V: Jan 18, 2026
- **Late Penalty**: 20% deduction per day

### Quality Constraints

- **Code Quality**:
  - No commented-out code
  - No console.log/print in production
  - No hard-coded values
  - Max function length: 50 lines
- **Documentation**:
  - README with setup, architecture, API docs
  - Environment variables documented
  - Deployment instructions included

---

## Success Criteria

### Phase I (100 points)

- [ ] In-memory Python console app functional
- [ ] All 5 Basic Level features working
- [ ] Constitution + specs present
- [ ] CLAUDE.md + README.md complete
- [ ] No manual coding evidence

### Phase II (150 points)

- [ ] Next.js frontend on Vercel
- [ ] FastAPI backend deployed
- [ ] Neon DB connected
- [ ] Better Auth + JWT working
- [ ] Monorepo structure
- [ ] 6 RESTful endpoints functional

### Phase III (200 points)

- [ ] OpenAI ChatKit UI integrated
- [ ] MCP server with 5 tools
- [ ] Natural language understanding
- [ ] Stateless architecture
- [ ] Conversation state in database
- [ ] 3 models: Task, Conversation, Message

### Phase IV (250 points)

- [ ] Dockerfiles for frontend/backend
- [ ] Helm charts created
- [ ] Deployed to Minikube
- [ ] kubectl-ai/kagent usage documented
- [ ] Gordon (Docker AI) evidence

### Phase V (300 points)

- [ ] All Advanced Level features
- [ ] Kafka deployed with 3 topics
- [ ] Dapr integrated (Pub/Sub, State, Jobs, Secrets)
- [ ] Cloud deployment (AKS/GKE/OKE)
- [ ] CI/CD pipeline functional
- [ ] Monitoring configured

### Bonus Points (+600)

- [ ] Reusable Intelligence (+200)
- [ ] Cloud-Native Blueprints (+200)
- [ ] Urdu language support (+100)
- [ ] Voice commands (+200)

---

## Validation Rules

### Automated Checks

- Linting: ESLint (frontend), Ruff (backend)
- Type checking: TypeScript, mypy
- Tests: All suites passing
- Security scan: No critical vulnerabilities

### Disqualification Triggers

- ❌ Manual coding detected
- ❌ Plagiarism found
- ❌ Missing Constitution/specs
- ❌ Phase skipping
- ❌ Late submission without arrangement

### Deduction Rules

- **50%+ deduction**: Non-functional deployment, critical bugs, security flaws
- **10-25% deduction**: Incomplete docs, missing tests, poor performance

---

## Decision Hierarchy

1. **Constitution** (this file) - Highest authority
2. **Specifications** - Requirements definition
3. **Plans** - Architecture and design decisions
4. **Tasks** - Implementation instructions
5. **Code** - Generated output (lowest authority)

---

## Governance

### Amendment Procedure

1. Propose amendment with rationale
2. Review against existing principles for conflicts
3. Update version per semantic versioning:
   - MAJOR: Backward-incompatible principle changes
   - MINOR: New sections or expanded guidance
   - PATCH: Clarifications, typos, refinements
4. Update Last Amended date
5. Propagate changes to dependent templates

### Compliance Review

- Before each phase submission
- After any architectural decision
- When introducing new technology
- When deviating from established patterns

---

**Total Maximum Points**: 1000 (base) + 600 (bonus) = 1600
