---
name: spec-validator
description: |
  Validate specifications for completeness, consistency, and implementation-readiness. Identify gaps, conflicts, and ambiguities.
---

# Spec Validator

Validate specifications for completeness, consistency, and implementation-readiness. Identify gaps, conflicts, and ambiguities.

## When to Use This Skill
- Before starting implementation
- User asks "is this spec complete?"
- Reviewing feature requirements
- Preventing implementation blockers

## Procedure
1. **Completeness check**: Are all requirements covered?
2. **Consistency check**: Do specs contradict each other?
3. **Clarity check**: Are there ambiguities or gaps?
4. **Feasibility check**: Can this be built as specified?
5. **Testability check**: Can we verify it works?

## Output Format
**Validation Report**:
- Overall readiness score
- Missing requirements
- Inconsistencies found
- Ambiguities to clarify
- Implementation blockers
- Recommendations

## Quality Criteria
- Identifies all critical gaps
- Flags contradictions explicitly
- Suggests concrete fixes
- Prioritizes issues (blocker vs nice-to-fix)
- References specific sections
- Actionable recommendations

## Example
**Input**: "Validate the comment system specification before we start building"

**Output**:

# Specification Validation Report: Comment System

**Date**: January 15, 2026
**Validator**: AI Assistant
**Spec Version**: 1.0
**Overall Readiness**: 75% (Good, with gaps)

## Executive Summary

The comment system specification is **mostly implementation-ready** but has **5 critical gaps** and **3 inconsistencies** that must be resolved before development. The architecture is sound, but edge cases and security considerations need clarification.

**Recommendation**: Address critical issues (listed below) before sprint planning. Expect 1-2 days of spec refinement.

---

## Validation Checklist

### ✅ Complete & Clear
- [x] User stories with acceptance criteria
- [x] Database schema defined
- [x] API contracts specified
- [x] UI component breakdown
- [x] Technology choices justified
- [x] Task dependencies mapped
- [x] Effort estimates provided

### ⚠️ Issues Found
- [ ] Security considerations incomplete (see §3.1)
- [ ] Rate limiting strategy vague (see §3.2)
- [ ] Mobile responsiveness not specified (see §3.3)
- [ ] Error handling incomplete (see §3.4)
- [ ] Performance benchmarks missing (see §3.5)

---

## 1. Critical Gaps (Must Fix Before Development)

### 1.1 Missing: Rate Limiting Strategy Details
**Severity**: 🔴 Blocker
**Location**: Feature Spec → API Contracts

**Issue**:
Spec mentions "max 5 comments/minute" but doesn't define:
- Is this per-user or per-IP?
- How are limits enforced (Redis? Database?)
- What happens on rate limit (error code? retry-after header?)
- Does it apply to all endpoints or just `create`?

**Impact**: Without this, spam/abuse is unmitigated risk

**Recommendation**:
```yaml
Rate Limiting Strategy:
  Scope: Per authenticated user (by user_id)
  Storage: Redis with sliding window
  Limits:
    - create: 5 requests/minute, 50/hour
    - update: 10 requests/minute
    - delete: 10 requests/minute
  Response: HTTP 429 with Retry-After header
  Bypass: Admin role exempt from limits
```

---

### 1.2 Missing: XSS Prevention Strategy
**Severity**: 🔴 Blocker
**Location**: Feature Spec → Edge Cases

**Issue**:
Spec mentions "sanitize HTML, strip scripts" but doesn't specify:
- Which library? (DOMPurify? sanitize-html?)
- Where sanitization happens? (client? server? both?)
- What HTML tags are allowed? (links? bold? none?)
- How to handle markdown if supported?

**Impact**: Security vulnerability if not properly implemented

**Recommendation**:
```typescript
Sanitization Rules:
  Library: DOMPurify (client + server)
  Allowed: Plain text only, no HTML
  Approach:
    1. Client: Strip all HTML before sending
    2. Server: Double-check, reject if HTML detected
    3. Display: Use textContent (not innerHTML)
  Markdown: Not supported in v1 (future consideration)
```

---

### 1.3 Missing: Concurrent Edit Handling
**Severity**: 🟡 High
**Location**: Feature Spec → Edge Cases

**Issue**:
What happens if two users try to edit the same comment simultaneously?
- First-write-wins? Last-write-wins?
- Optimistic locking? Version field?
- Show conflict warning to user?

**Current Spec Says**: Nothing

**Recommendation**:
```typescript
Conflict Resolution:
  Strategy: Optimistic locking with version field
  Database: Add `version INT DEFAULT 1` to comments table
  Flow:
    1. Client fetches comment with version=1
    2. User edits, submits with version=1
    3. Server checks: UPDATE WHERE id=X AND version=1
    4. If affected_rows=0 → version conflict
    5. Return 409 Conflict with latest version
    6. Client shows: "This comment was edited by someone else. Reload?"
```

---

### 1.4 Missing: Mobile Responsive Behavior
**Severity**: 🟡 High
**Location**: UI Spec → Responsive Breakpoints

**Issue**:
Spec defines breakpoints but not specific mobile behavior:
- How does threading work on mobile (limited width)?
- Do replies stack differently?
- Is there a "View replies" collapse/expand?
- How does the comment form work on small screens?

**Recommendation**:
```yaml
Mobile Behavior (<640px):
  Threading:
    - Max 2 visual indent levels (vs 3 on desktop)
    - Level 3+ shows "View N more replies" button
    - Tap to expand nested thread in modal/drawer
  Comment Form:
    - Textarea height: 80px (vs 120px desktop)
    - Character counter always visible
    - Submit button full-width
  Avatar Size: 32px (vs 40px desktop)
  Font Size: 14px (vs 16px desktop)
```

---

### 1.5 Missing: Deleted Comment Display Logic
**Severity**: 🟢 Medium
**Location**: Feature Spec → User Stories

**Issue**:
Spec says deleted comments show "[Deleted by user]" but doesn't specify:
- Is the entire comment removed or just content?
- Do we preserve thread structure?
- Can you reply to a deleted comment?
- Is author name removed?

**Current Behavior**: Contradictory statements in different sections

**Recommendation**:
```yaml
Deleted Comment Display:
  User-Deleted:
    Content: "[This comment was deleted by the author]"
    Author: Show original author name (preserve context)
    Timestamp: Preserved
    Replies: Remain visible (thread continuity)
    Actions: No Reply/Edit/Delete buttons

  Moderator-Deleted:
    Content: "[This comment was removed by a moderator]"
    Author: "[Removed]"
    Timestamp: Preserved
    Replies: Remain visible

  Tombstone Logic:
    - Keep record in DB (soft delete)
    - Show placeholder if has replies
    - Completely hide if no replies (reduce clutter)
```

---

## 2. Inconsistencies (Conflicts in Spec)

### 2.1 Edit Window Timeframe Conflict
**Severity**: 🟡 High
**Locations**:
- Feature Spec §Story 3: "15 minutes"
- Task Breakdown §T4: "15 minutes"
- Architecture Doc: Not mentioned

**Issue**: Consistent across most sections, but...

**In UI Spec**: Says "Edit button visible only to comment author"
**No time limit mentioned** in UI spec

**Resolution Needed**: Clarify if UI should:
- Hide Edit button after 15 minutes?
- Show Edit button but disable it?
- Show button, let API reject with error message?

**Recommendation**: Hide Edit button after 15 minutes (client-side check) + server validation

---

### 2.2 Character Limit Inconsistency
**Severity**: 🟢 Medium
**Locations**:
- Feature Spec: "min 10 chars, max 2000 chars"
- Database Schema: `CHECK (length(content) BETWEEN 10 AND 2000)`
- UI Spec: "Minimum 10 characters"

**Issue**: All consistent at 2000 except...

**Task T7 (CommentForm)**: Says `maxLength={2000}` but validation is `content.length <= 2000`

**Problem**: Off-by-one? Is 2000 inclusive or exclusive?

**Resolution**: Confirm that **2000 is inclusive** (user can type exactly 2000 chars)

---

### 2.3 Moderation Action Naming
**Severity**: 🟢 Low
**Locations**: Multiple

**Issue**: Inconsistent terminology:
- Feature Spec: "Hide" and "Delete"
- Database schema: `is_hidden` boolean and `deleted_at` timestamp
- API endpoint: `moderate` action takes `'hide' | 'delete'`
- UI Spec: "Remove" button

**Confusion**: Does "Delete" mean soft delete or hard delete?

**Recommendation**: Standardize terminology:
- "Hide" → `is_hidden = true` (reversible, admin-only visibility)
- "Soft Delete" → `deleted_at = NOW()` (shows "[Removed]", irreversible)
- "Hard Delete" → Not supported in v1 (data retention policy)

---

## 3. Ambiguities (Needs Clarification)

### 3.1 Notification Preferences
**Severity**: 🟡 High

**Ambiguity**: Spec says "User A receives email when User B replies"

**Questions**:
- Can users opt out of notifications?
- Is there a notification settings page?
- Do we notify on ALL replies or just direct replies?
- What about reply-to-reply (grandchild comments)?

**Recommendation**: Defer to v2 OR implement basic "email on reply" with unsubscribe link in footer

---

### 3.2 "Viewing Now" Presence Timeout
**Severity**: 🟢 Medium

**Ambiguity**: UI Spec says "Viewers disappear after 30s of inactivity"

**Questions**:
- 30s since last heartbeat? Last page interaction? Last comment view?
- What if tab is backgrounded?
- Does scrolling count as activity?
- Mobile: Does screen lock affect this?

**Recommendation**:
```yaml
Presence Logic:
  Heartbeat: Every 15s while page active
  Timeout: 30s after last heartbeat
  Tab Visibility: Pause heartbeat when tab hidden
  Activity: Any page interaction resets timer
```

---

### 3.3 Comment Ordering
**Severity**: 🟢 Medium

**Ambiguity**: Spec says "Order by created_at" but doesn't specify:
- Ascending or descending?
- Newest first or oldest first?
- Does threading affect order?

**Recommendation**:
```yaml
Comment Ordering:
  Top-Level: Oldest first (chronological discussion)
  Replies: Oldest first (conversation flow)
  Future: Add "Sort by: Newest | Oldest | Top" dropdown
```

---

### 3.4 Subtask vs Comment Relationship
**Severity**: 🟢 Low

**Ambiguity**: UI Spec shows both "Subtasks" and "Comments" sections

**Questions**:
- Are these separate features or related?
- Can you comment on a subtask?
- Are subtasks in the same database as comments?

**Clarification Needed**: This seems like it's mixing two separate features. Confirm scope.

---

## 4. Missing Non-Functional Requirements

### 4.1 Performance Benchmarks
**Current State**: Architecture doc mentions "<50ms for 100 comments"

**Missing**:
- Target P95 latency for API endpoints
- Frontend render time targets
- Time-to-interactive budget
- Database query performance SLOs

**Recommendation**:
```yaml
Performance Targets:
  API Endpoints:
    - comments.list: <100ms (P95)
    - comments.create: <200ms (P95)
    - comments.update: <150ms (P95)

  Frontend:
    - Initial render: <1s
    - Comment submission: <500ms perceived (optimistic UI)
    - Scroll performance: 60 FPS with 500+ comments

  Database:
    - Fetch 100 comments: <50ms
    - Insert comment: <20ms
    - Threading query: <80ms
```

---

### 4.2 Accessibility Standards
**Current State**: UI Spec mentions ARIA labels

**Missing**:
- WCAG conformance level (A, AA, AAA?)
- Screen reader testing requirements
- Keyboard navigation specifics
- Color contrast ratios

**Recommendation**: Target **WCAG 2.1 Level AA** compliance

---

### 4.3 Monitoring & Observability
**Missing**:
- What metrics to track?
- Error logging strategy?
- Performance monitoring?
- User analytics?

**Recommendation**:
```yaml
Monitoring:
  Error Tracking: Sentry (backend + frontend)
  Metrics:
    - Comment creation rate
    - Edit/delete frequency
    - Moderation actions
    - Response times (P50, P95, P99)
  Logs: Structured JSON with request IDs
  Alerts:
    - API error rate >1%
    - Response time P95 >500ms
    - Database connection pool exhaustion
```

---

## 5. Implementation Risks

### 5.1 Threading Complexity
**Risk Level**: 🟡 Medium

**Issue**: Recursive queries and nested UI can be complex

**Mitigation**:
- Start with non-recursive approach (fetch all, build tree in memory)
- Add pagination early (don't load 1000+ comments at once)
- Consider "Load more replies" for deep threads

---

### 5.2 Real-Time Sync Edge Cases
**Risk Level**: 🟡 Medium

**Issue**: WebSocket disconnections, missed events, duplicate updates

**Mitigation**:
- Implement reconnection logic with exponential backoff
- Use event IDs to deduplicate
- Fallback to polling if WebSocket fails
- Don't make real-time critical for v1 (nice-to-have)

---

### 5.3 Moderation Scalability
**Risk Level**: 🟢 Low (for initial launch)

**Issue**: Manual moderation doesn't scale

**Future Consideration**:
- Auto-flagging based on user reports
- ML-based spam detection
- Automated profanity filtering
- Delegate moderation to trusted users

---

## 6. Testing Gaps

### 6.1 Load Testing Not Specified
**Missing**: How will we validate performance under load?

**Recommendation**:
```yaml
Load Testing Plan:
  Tool: k6 or Artillery
  Scenarios:
    - 100 concurrent users reading comments
    - 50 concurrent users posting comments
    - 10 concurrent users posting to same thread
  Success Criteria:
    - Zero errors at 100 concurrent users
    - <500ms response time at P95
    - Database CPU <70%
```

---

### 6.2 Security Testing Not Specified
**Missing**:
- Penetration testing
- SQL injection attempts
- XSS payload testing
- CSRF protection validation

**Recommendation**: Add security test suite with known attack vectors

---

## 7. Dependencies & Assumptions

### 7.1 Unvalidated Assumptions
Spec assumes the following without validation:

1. **Auth system exists** - Is it ready? What's the user model?
2. **Email service configured** - SendGrid account? Templates ready?
3. **Redis available** - Infrastructure provisioned? Cluster or single-node?
4. **WebSocket infrastructure** - Socket.io server scaled? Load balancer config?

**Recommendation**: Validate these dependencies before sprint start

---

## 8. Documentation Completeness

### ✅ Well-Documented
- [x] API contracts with request/response examples
- [x] Database schema with indexes
- [x] Component hierarchy
- [x] User flows

### ⚠️ Missing Documentation
- [ ] Error code catalog (standardized error codes)
- [ ] Deployment runbook (how to deploy comments feature)
- [ ] Rollback plan (how to disable if bugs found)
- [ ] Migration guide (existing users? data migration?)

---

## 9. Recommendations Summary

### Must Fix Before Development (Blockers)
1. ✅ Define rate limiting implementation details
2. ✅ Specify XSS prevention strategy with library choice
3. ✅ Resolve edit window UI behavior inconsistency
4. ✅ Clarify concurrent edit conflict resolution
5. ✅ Define mobile responsive threading behavior

### Should Fix Before Launch (High Priority)
6. ⚠️ Specify deleted comment display logic completely
7. ⚠️ Add performance benchmarks and targets
8. ⚠️ Clarify notification preferences and opt-out
9. ⚠️ Standardize moderation terminology

### Nice to Have (Post-MVP)
10. 💡 Add comment sorting options (newest/oldest/top)
11. 💡 Consider pagination strategy for large threads
12. 💡 Plan for moderation scaling

---

## 10. Final Verdict

**Implementation Readiness**: 75% → Can reach 95% with 1-2 days of spec refinement

**Recommended Actions**:
1. **Day 1**: Address all 🔴 Blocker issues (§1.1, 1.2, 1.3)
2. **Day 2**: Resolve inconsistencies (§2.1, 2.2) and add performance targets (§4.1)
3. **Ongoing**: Clarify ambiguities as they arise during development

---

## Validation Framework

### 1. Completeness Checklist
```
Core Requirements:
□ User stories with clear acceptance criteria
□ API contracts (request/response schemas)
□ Database schema with relationships
□ UI component specifications
□ Error handling strategies
□ Security considerations
□ Performance requirements
□ Monitoring and logging strategy

Advanced Requirements:
□ Load testing plan
□ Disaster recovery plan
□ Rollback procedures
□ Migration strategy
□ Dependency validation
□ Integration points defined
□ External service contracts
```

### 2. Consistency Checker
```
Cross-Reference Validation:
□ Database schema matches API contracts
□ API contracts match UI component props
□ User stories align with technical implementation
□ Frontend and backend types match
□ Error codes are consistent across services
□ Naming conventions are uniform
□ Business logic is coherent across components
□ Security requirements are consistent
```

### 3. Feasibility Assessment
```
Technical Feasibility:
□ All required technologies are available
□ Performance targets are achievable
□ Security requirements are implementable
□ Integration points are technically viable
□ Resource requirements are reasonable
□ Timeline is realistic given complexity
□ Team skills match requirements
□ Infrastructure can support requirements
```

### 4. Risk Assessment Matrix
```
Risk Categories:
🔴 Critical: Blocks development or causes security issues
🟡 High: May cause delays or performance problems
🟢 Medium: Could cause minor issues
🔵 Low: Minor improvement opportunities

Impact vs Probability:
High Impact + High Probability = Address immediately
High Impact + Low Probability = Plan mitigation
Low Impact + High Probability = Address during development
Low Impact + Low Probability = Consider for later
```

## Best Practices

### 1. Validation Process
1. **Read the entire spec** before starting validation
2. **Create a mental model** of the system
3. **Check each section** against the overall architecture
4. **Look for cross-section consistency**
5. **Identify missing non-functional requirements**
6. **Assess implementation feasibility**
7. **Prioritize issues** by impact and urgency
8. **Provide concrete solutions**, not just problems

### 2. Reporting Style
- **Be specific**: Reference exact sections and line numbers
- **Be constructive**: Offer solutions, not just criticism
- **Be prioritized**: Distinguish between blockers and nice-to-haves
- **Be actionable**: Give clear next steps
- **Be evidence-based**: Point to specific inconsistencies
- **Be comprehensive**: Cover all validation aspects

### 3. Common Issues to Look For
- **Circular dependencies** in requirements
- **Undefined terms** or ambiguous language
- **Missing error states** and edge cases
- **Inconsistent naming** across sections
- **Unrealistic performance targets**
- **Security gaps** in authentication/authorization
- **Missing rollback strategies**
- **Undefined integration points**
- **Unvalidated assumptions** about external services
- **Insufficient testability** of requirements

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing architecture patterns, validation tools, previous spec reviews |
| **Conversation** | User's specific validation needs, critical requirements, timeline constraints |
| **Skill References** | Specification best practices, validation frameworks, common pitfalls |
| **User Guidelines** | Project-specific validation standards, compliance requirements, quality gates |