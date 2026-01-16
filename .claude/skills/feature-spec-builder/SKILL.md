---
name: feature-spec-builder
description: |
  Create detailed feature specifications with user stories, acceptance criteria, edge cases, and success metrics.
---

# Feature Spec Builder

Create detailed feature specifications with user stories, acceptance criteria, edge cases, and success metrics.

## When to Use This Skill
- User wants to build a new feature
- User mentions "user story" or "requirements"
- Need to clarify feature scope before implementation
- Converting product ideas into engineering specs

## Procedure
1. **Define user need**: Who needs this and why
2. **Write user stories**: As [role], I want [action], so that [benefit]
3. **List acceptance criteria**: Specific, testable conditions
4. **Document edge cases**: Error states, boundary conditions
5. **Set success metrics**: How to measure if feature works

## Output Format
**Feature Specification**:
- Overview and user need
- User stories with acceptance criteria
- User flows (step-by-step)
- Edge cases and error handling
- API contracts (if applicable)
- Success metrics

## Quality Criteria
- User stories focus on value, not implementation
- Acceptance criteria are testable (pass/fail)
- Edge cases are comprehensive (unhappy paths)
- Flows are specific enough to implement
- Metrics are measurable and time-bound

## Example
**Input**: "Spec out a comment system for our blog posts"

**Output**:

# Feature Spec: Blog Post Comments

## Overview
Enable readers to discuss blog posts through threaded comments, increasing engagement and community building.

**Target Users**: Blog readers (authenticated and anonymous)
**Priority**: P1 (High)
**Estimated Effort**: 3-5 days
**Dependencies**: User authentication system

## User Need
**Problem**: Readers want to discuss posts but currently must use external platforms (Twitter, Discord), fragmenting conversations.

**Solution**: Built-in comment system with threading, notifications, and moderation controls.

**Success Looks Like**: 30% of blog visitors leave comments within first month of launch.

## User Stories

### Story 1: Post a Comment
**As a** logged-in reader
**I want to** comment on blog posts
**So that** I can share thoughts and ask questions

**Acceptance Criteria**:
- [ ] Comment form appears below blog post content
- [ ] Form has text input (min 10 chars, max 2000 chars)
- [ ] Submit button disabled until text meets requirements
- [ ] Comment appears immediately after submission
- [ ] User sees success message: "Comment posted"
- [ ] Comment includes author name, avatar, and timestamp
- [ ] Character count shows remaining characters

### Story 2: Reply to Comment (Threading)
**As a** reader
**I want to** reply to specific comments
**So that** I can have focused conversations

**Acceptance Criteria**:
- [ ] Each comment has "Reply" button
- [ ] Clicking Reply shows nested form under that comment
- [ ] Replies visually indented (max 3 levels deep)
- [ ] Reply references parent comment
- [ ] Parent author gets notification of reply
- [ ] Cancel button returns to main view

### Story 3: Edit Own Comment
**As a** comment author
**I want to** edit my comments
**So that** I can fix typos or clarify thoughts

**Acceptance Criteria**:
- [ ] "Edit" button visible only to comment author
- [ ] Edit window available for 15 minutes after posting
- [ ] Edit form pre-filled with current text
- [ ] Save button updates comment in place
- [ ] Comment shows "(edited)" label with timestamp
- [ ] Edit history stored (admin-visible only)

### Story 4: Delete Own Comment
**As a** comment author
**I want to** delete inappropriate comments
**So that** I can remove mistakes

**Acceptance Criteria**:
- [ ] "Delete" button visible only to comment author
- [ ] Confirmation modal: "Are you sure? This cannot be undone"
- [ ] Deleted comment shows "[Deleted by user]"
- [ ] Replies remain visible (preserves thread context)
- [ ] Author name replaced with "[Deleted]"

### Story 5: Moderate Comments (Admin)
**As a** blog admin
**I want to** moderate inappropriate comments
**So that** I maintain community standards

**Acceptance Criteria**:
- [ ] Admins see "Hide" and "Delete" on all comments
- [ ] Hidden comments invisible to public, visible to admins
- [ ] Delete removes comment completely
- [ ] Admin actions logged with timestamp + admin ID
- [ ] Bulk actions: select multiple → hide/delete
- [ ] Reason field required for moderation actions

## User Flows

### Flow 1: First-Time Commenter
1. User reads blog post
2. Scrolls to comment section
3. Sees login prompt: "Sign in to comment"
4. Clicks "Sign in with Google"
5. Redirects to Google OAuth
6. Returns to post (scroll position preserved)
7. Comment form now active
8. Types comment (sees character count)
9. Clicks "Post Comment"
10. Sees comment appear with success message
11. Receives email: "You commented on [Post Title]"

### Flow 2: Reply Notification
1. User A comments on post
2. User B replies to User A's comment
3. User A receives email: "User B replied to your comment"
4. User A clicks email link
5. Lands on post, scrolled to their comment
6. Reply is highlighted for 2 seconds
7. User A can reply back or dismiss

## API Contracts

### POST /api/comments
```typescript
Request:
{
  post_id: string;
  content: string;
  parent_id?: string; // null for top-level
}

Response (201):
{
  id: string;
  post_id: string;
  author_id: string;
  author_name: string;
  author_avatar: string;
  content: string;
  parent_id: string | null;
  created_at: string;
  edited_at: string | null;
  is_deleted: boolean;
}

Errors:
- 400: Content too short/long
- 401: Not authenticated
- 404: Post not found
- 429: Rate limit (max 5 comments/minute)
```

### GET /api/comments?post_id={id}
```typescript
Response (200):
{
  comments: Comment[];
  total: number;
  has_more: boolean;
}

// Comments returned in tree structure
interface Comment {
  id: string;
  content: string;
  author: { id: string; name: string; avatar: string; };
  created_at: string;
  replies: Comment[]; // Nested up to 3 levels
  reply_count: number;
  can_edit: boolean;
  can_delete: boolean;
}
```

### PATCH /api/comments/{id}
```typescript
Request:
{
  content: string;
}

Response (200):
{
  id: string;
  content: string;
  edited_at: string;
}

Errors:
- 403: Not comment author or edit window expired
- 404: Comment not found
```

## Edge Cases & Error Handling

### Input Validation
- **Empty comment**: Show error "Comment cannot be empty"
- **Too short (<10 chars)**: Disable submit, show "Minimum 10 characters"
- **Too long (>2000 chars)**: Block typing at limit, show "Maximum reached"
- **Only whitespace**: Treat as empty
- **XSS attempt**: Sanitize HTML, strip scripts
- **SQL injection**: Use parameterized queries

### Authentication
- **Not logged in**: Hide comment form, show "Sign in to comment"
- **Session expired**: Show "Session expired, please sign in again"
- **Banned user**: Show "You cannot comment at this time"

### Network Issues
- **Submit fails**: Show retry button, preserve text
- **Slow connection**: Show loading spinner, disable multiple submits
- **Offline**: Detect offline, show "You're offline" message

### Rate Limiting
- **5 comments in 1 minute**: Show "You're commenting too fast. Wait 30 seconds"
- **10 comments in 1 hour**: Show "Comment limit reached. Try again in 1 hour"

### Threading Depth
- **Reply to 3rd-level comment**: Button disabled, tooltip "Max reply depth reached"
- **Alternative**: Replies beyond level 3 appear at level 3

### Moderation
- **Comment flagged 3+ times**: Auto-hide, notify admin
- **Spam detected**: Auto-reject, log for review
- **Repeat offender**: Auto-ban after 3 violations

## Database Schema

```sql
CREATE TABLE comments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  post_id UUID NOT NULL REFERENCES posts(id),
  author_id UUID NOT NULL REFERENCES users(id),
  parent_id UUID REFERENCES comments(id),
  content TEXT NOT NULL CHECK (length(content) BETWEEN 10 AND 2000),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  edited_at TIMESTAMPTZ,
  deleted_at TIMESTAMPTZ,
  is_hidden BOOLEAN DEFAULT false,

  INDEX idx_comments_post_id (post_id),
  INDEX idx_comments_parent_id (parent_id),
  INDEX idx_comments_created_at (created_at DESC)
);

CREATE TABLE comment_edit_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  comment_id UUID NOT NULL REFERENCES comments(id),
  previous_content TEXT NOT NULL,
  edited_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE comment_moderation_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  comment_id UUID NOT NULL REFERENCES comments(id),
  moderator_id UUID NOT NULL REFERENCES users(id),
  action TEXT NOT NULL, -- 'hide', 'delete', 'approve'
  reason TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## UI Components

### Components to Build
1. **CommentList**: Display all comments with threading
2. **CommentItem**: Single comment with author, content, actions
3. **CommentForm**: Text input with submit/cancel
4. **CommentActions**: Edit, Delete, Reply buttons
5. **ModerationPanel**: Admin controls (hide/delete/approve)

### Design Tokens
- Font: System font stack
- Max width: 800px
- Indent per level: 24px
- Avatar size: 40px
- Spacing: 16px between comments

## Success Metrics

### Launch Metrics (Week 1)
- [ ] 20% of readers scroll to comment section
- [ ] 10% of readers post at least one comment
- [ ] Average 3 comments per post
- [ ] <2% spam/inappropriate comments

### Growth Metrics (Month 1)
- [ ] 30% of readers engage with comments
- [ ] 50% of commenters return to reply
- [ ] Average thread depth of 2.5 levels
- [ ] <5 second load time for 100 comments

### Quality Metrics (Ongoing)
- [ ] <1% comments flagged as spam
- [ ] >90% comments remain unmoderated
- [ ] <5% of comments edited
- [ ] <2% of comments deleted

## Open Questions
- [ ] Should we support markdown in comments?
- [ ] Do we need comment voting (upvote/downvote)?
- [ ] Should we show "Top Comments" vs chronological?
- [ ] Email digest of new comments for post authors?

## Out of Scope (Future Iterations)
- ❌ @mentions of other users
- ❌ Image uploads in comments
- ❌ Comment reactions (emoji)
- ❌ Sort by controversial/top/new
- ❌ Subscribe to comment threads

## Feature Specification Templates

### E-commerce Feature Spec
```
# Feature Spec: [FEATURE NAME]

## Overview
Enable [TARGET USERS] to [ACHIEVE GOAL] through [SOLUTION DESCRIPTION].

**Target Users**: [SPECIFIC USER GROUPS]
**Priority**: [P0/P1/P2/P3]
**Estimated Effort**: [TIME ESTIMATE]
**Dependencies**: [OTHER FEATURES/SERVICES]

## User Need
**Problem**: [USER PROBLEM TO SOLVE]
**Solution**: [HOW FEATURE SOLVES PROBLEM]
**Success Looks Like**: [MEASURABLE OUTCOME]

## User Stories
[Follow same format as example above]

## User Flows
[Detailed step-by-step flows]

## API Contracts
[Request/response schemas]

## Edge Cases & Error Handling
[Comprehensive error scenarios]

## Success Metrics
[Measurable outcomes]

## Out of Scope
[Future iterations/features not in current scope]
```

### Dashboard Feature Spec
```
# Feature Spec: [DASHBOARD COMPONENT]

## Overview
Enable [USER ROLE] to [MONITOR/OBSERVE] [DATA/METRICS] through [VISUALIZATION TYPE].

## User Need
**Problem**: [DATA VISIBILITY ISSUE]
**Solution**: [HOW DASHBOARD SOLVES ISSUE]
**Success Looks Like**: [MEASURABLE OUTCOME]

## User Stories
[As [ROLE], I want to [ACTION], so that [BENEFIT]]

## Data Requirements
- **Data Sources**: [LIST OF DATA SOURCES]
- **Update Frequency**: [REAL TIME/HOURLY/DAILY]
- **Retention**: [TIME PERIOD FOR DATA STORAGE]

## Visual Elements
- **Charts**: [CHART TYPES NEEDED]
- **Metrics**: [SPECIFIC METRICS TO DISPLAY]
- **Filters**: [FILTER OPTIONS AVAILABLE]
- **Export**: [EXPORT CAPABILITIES]

## Performance Requirements
- **Load Time**: [MAXIMUM LOAD TIME]
- **Data Refresh**: [FREQUENCY OF DATA UPDATES]
- **Concurrent Users**: [EXPECTED NUMBER OF SIMULTANEOUS USERS]
```

## Best Practices
1. **User-focused**: Always start with user needs, not technical implementation
2. **Testable criteria**: Write acceptance criteria that can be verified
3. **Think through edge cases**: Consider error states and boundary conditions
4. **Include success metrics**: Define how to measure feature success
5. **Keep it concise**: Focus on what matters most
6. **Iterate**: Update spec as understanding improves
7. **Get feedback**: Share with team before implementation
8. **Link to business goals**: Connect features to business objectives

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing features, user models, authentication system, database schema |
| **Conversation** | User's specific feature requirements, business goals, timeline, success metrics |
| **Skill References** | User story patterns, acceptance criteria formats, API design best practices |
| **User Guidelines** | Project-specific requirements, design system, security policies, compliance needs |