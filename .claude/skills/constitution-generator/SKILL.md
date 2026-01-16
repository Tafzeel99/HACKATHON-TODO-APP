---
name: constitution-generator
description: |
  Create project principles, technical constraints, and decision-making frameworks that guide development choices.
---

# Constitution Generator

Create project principles, technical constraints, and decision-making frameworks that guide development choices.

## When to Use This Skill
- Starting a new project and need guiding principles
- User mentions "project guidelines" or "tech stack decisions"
- Team needs alignment on architectural choices
- User wants documented rationale for constraints

## Procedure
1. **Gather context**: Project goals, team size, timeline, domain
2. **Define core principles**: What matters most (speed, scale, simplicity)
3. **Set technical constraints**: Languages, frameworks, infrastructure limits
4. **Create decision framework**: How to choose between options
5. **Document exceptions**: When to break the rules

## Output Format
**Project Constitution**:
- Vision and goals
- Core principles (3-7 items)
- Technical constraints and rationale
- Decision-making framework
- Non-negotiables vs preferences

## Quality Criteria
- Principles are specific and actionable, not generic platitudes
- Constraints have clear reasoning
- Framework helps resolve real trade-offs
- Flexible enough to adapt, rigid enough to guide
- Covers both technical and product decisions

## Example
**Input**: "Create project constitution for a SaaS MVP with 2-person team, 3-month deadline"

**Output**:

# Project Constitution: TaskFlow SaaS MVP

## Vision
Build a task management SaaS that generates $10k MRR within 6 months of launch by focusing on team collaboration for remote workers.

## Core Principles

### 1. Ship Speed Over Perfection
**What it means**: Launch with core features in 3 months, iterate based on user feedback
**In practice**:
- Choose proven tech over cutting-edge
- Skip features that delay launch
- Technical debt is acceptable if it enables user validation
- Every feature must answer: "Does this block launch?"

### 2. Monolith Until It Hurts
**What it means**: Start with single codebase/database, split only when pain is real
**In practice**:
- No microservices until 100k+ users
- Shared database for all features
- Colocate frontend/backend in monorepo
- Exception: External services for non-core features (email, payments)

### 3. Build vs Buy: Default to Buy
**What it means**: Use managed services and SaaS tools aggressively
**In practice**:
- Auth: Use Clerk or Auth0 (don't build)
- Email: SendGrid or Postmark
- Payments: Stripe (not custom billing)
- Analytics: PostHog or Mixpanel
- Exception: Core task management logic (our competitive advantage)

### 4. Optimize for Developer Velocity
**What it means**: Choose tools that let 2 developers move fast
**In practice**:
- TypeScript full-stack (shared types, single language)
- Hot reload everywhere
- Automated testing only for critical paths
- Deploy previews on every PR
- Exception: Performance bottlenecks affecting user experience

### 5. Design for 1k Users, Plan for 100k
**What it means**: Architecture handles 1k concurrent users, with clear path to scale
**In practice**:
- Single server can handle initial load
- Database can scale vertically to 100k users
- Caching strategy defined but not implemented
- Document scaling plan in docs/SCALING.md

## Technical Constraints

### Stack (Non-Negotiable)
- **Frontend**: React + TypeScript + Vite
  - *Why*: Team expertise, fast reload, mature ecosystem
- **Backend**: Node.js + TypeScript + tRPC
  - *Why*: Type safety end-to-end, shared code with frontend
- **Database**: PostgreSQL + Prisma
  - *Why*: Relational data model, type-safe ORM, proven scale path
- **Hosting**: Vercel (frontend) + Railway (backend + DB)
  - *Why*: Zero-config deploys, preview environments, fair pricing

### Architecture Patterns
- **API Style**: tRPC (not REST or GraphQL)
  - *Why*: Type safety, no code generation, simpler than GraphQL
- **State Management**: Zustand (not Redux)
  - *Why*: Minimal boilerplate, TypeScript-first
- **Styling**: Tailwind CSS (not CSS-in-JS)
  - *Why*: Fast iteration, no runtime cost, great DX
- **Testing**: Vitest + Playwright (not Jest + Cypress)
  - *Why*: Faster, better TypeScript support

### What We're NOT Using
- ❌ Microservices
- ❌ GraphQL (overkill for MVP)
- ❌ NoSQL databases (our data is relational)
- ❌ Custom design system (use shadcn/ui)
- ❌ Mobile apps (web-first, PWA later)

## Decision-Making Framework

### When choosing between options, ask:
1. **Does it delay launch?** → Pick faster option
2. **Does it prevent future scaling?** → Document trade-off, proceed anyway
3. **Does team have experience?** → Favor familiarity over novelty
4. **Is it reversible?** → If yes, just decide and move on
5. **Will users care?** → If no, pick simplest option

### Examples

**Q: Should we add real-time collaboration now?**
- Delays launch? **Yes** (complex WebSocket infrastructure)
- Users care? **Maybe** (not validated)
- Decision: ❌ **Skip for MVP**, add after launch if users request

**Q: Should we use Prisma or raw SQL?**
- Delays launch? **No** (Prisma speeds up development)
- Team experience? **Yes** (both know Prisma)
- Decision: ✅ **Use Prisma**, raw SQL only for performance bottlenecks

**Q: Server-side rendering or client-side?**
- SEO matters? **Yes** (marketing site)
- Performance matters? **Yes** (perceived speed)
- Decision: ✅ **SSR for marketing, CSR for app**

## Non-Negotiables vs Preferences

### Non-Negotiables (Must Have)
- ✅ Type safety across entire stack
- ✅ Automated deployments
- ✅ Auth handled by third-party service
- ✅ Database backups daily
- ✅ Error tracking (Sentry)
- ✅ User data privacy compliance (GDPR ready)

### Strong Preferences (Default Choice)
- Prefer server components over client components
- Prefer functional over class components
- Prefer composition over inheritance
- Prefer explicit over implicit
- Prefer boring over exciting technology

### Flexible (Decide Case-by-Case)
- Testing coverage percentage
- When to optimize performance
- When to refactor vs rewrite
- When to add monitoring

## When to Break the Rules

### Valid Exceptions
1. **Security Issue**: Any principle can be broken to fix security vulnerability
2. **Legal Requirement**: Compliance needs override technical preferences
3. **Customer Emergency**: Urgent customer needs may require deviating from principles
4. **Market Change**: Major market shifts may require different approach

### Rule-Breaking Process
1. **Document**: Why current approach doesn't work
2. **Propose**: Alternative solution that still achieves goal
3. **Review**: Get team consensus on deviation
4. **Time-box**: Set review date to reassess

## Review Schedule
- **Monthly**: Quick check if principles still align with business goals
- **Quarterly**: Deep dive to update constitution as needed
- **After major events**: Post-mortem after launches, incidents, pivots

## Team Alignment
This constitution represents agreements made by the team on [DATE]. Everyone should:
- **Reference** this document when making technical decisions
- **Update** it when team consensus changes
- **Teach** new team members about these principles
- **Challenge** decisions that violate these principles

---

*Last Updated: [DATE]*
*Approved by: [TEAM MEMBERS]*

## Template for Different Project Types

### Enterprise Project Constitution
```
# Project Constitution: [PROJECT NAME] for [CLIENT]

## Vision
Build enterprise solution that meets [BUSINESS GOALS] with [SECURITY/COMPLIANCE REQUIREMENTS].

## Core Principles
1. Security First: All decisions prioritize security and compliance
2. Integration Ready: Must work with existing enterprise systems
3. Scalability: Handle enterprise-scale loads and data volumes
4. Supportability: Easy to maintain and troubleshoot in enterprise environments
5. Standards Compliant: Follow industry standards and protocols

## Technical Constraints
- Stack: [SPECIFIC ENTERPRISE TECHNOLOGIES]
- Architecture: [SPECIFIC PATTERNS]
- Integration: [SPECIFIC APIs/PROTOCOLS]
```

### Startup MVP Constitution
```
# Project Constitution: [PRODUCT NAME] MVP

## Vision
Validate [CORE HYPOTHESIS] with real users in [TIMEFRAME] by building [MINIMUM VIABLE PRODUCT].

## Core Principles
1. Market Speed: Get to market faster than perfect
2. Learn Fast: Optimize for learning from user feedback
3. Pay Later: Defer technical decisions that don't block learning
4. Focus: Single-minded focus on core value proposition
5. Iterate: Build to throw away and rebuild based on learnings
```

### Platform/Infrastructure Constitution
```
# Project Constitution: [PLATFORM NAME]

## Vision
Build reliable, scalable infrastructure that supports [NUMBER] of services and [SCALE] of users.

## Core Principles
1. Reliability: System uptime and stability are paramount
2. Performance: Optimized for speed and efficiency
3. Observability: Everything is monitored and measurable
4. Scalability: Designed to grow without major rewrites
5. Self-Service: Easy for other teams to use and deploy
```

## Best Practices
1. **Be Specific**: Avoid vague principles like "high quality"
2. **Include Trade-offs**: Show what you're giving up for each choice
3. **Keep it Short**: 1-2 pages max for easy reference
4. **Make it Actionable**: Each principle should guide decisions
5. **Review Regularly**: Update as project evolves
6. **Get Buy-in**: Team must agree and commit to principles
7. **Link to Business**: Connect technical decisions to business goals

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Current project structure, existing decisions, legacy constraints |
| **Conversation** | User's specific project goals, team dynamics, timeline, risk tolerance |
| **Skill References** | Industry best practices, company standards, team preferences |
| **User Guidelines** | Organizational policies, compliance requirements, technical standards |