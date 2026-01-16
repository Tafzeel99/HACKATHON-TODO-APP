---
name: task-decomposer
description: |
  Break down features into atomic, testable tasks with clear inputs, outputs, and acceptance criteria for implementation.
---

# Task Decomposer

Break down features into atomic, testable tasks with clear inputs, outputs, and acceptance criteria for implementation.

## When to Use This Skill
- Converting feature specs into implementation tasks
- User mentions "break down" or "what to build first"
- Planning sprint or development workflow
- Need task estimates or dependencies

## Procedure
1. **Identify deliverables**: What are the shippable units
2. **Map dependencies**: What must be built first
3. **Create atomic tasks**: Each task is independent, testable, mergeable
4. **Estimate effort**: T-shirt sizing or hours
5. **Assign priority**: Critical path vs nice-to-have

## Output Format
**Task List**:
- Task ID and title
- Description with acceptance criteria
- Dependencies (what must be done first)
- Effort estimate
- Implementation hints
- Test criteria

## Quality Criteria
- Tasks are <1 day of work (ideal: 2-4 hours)
- Each task has clear done state
- No task is blocked by multiple others
- Tasks can be tested independently
- Order follows logical build sequence

## Example
**Input**: "Break down the comment system feature into implementation tasks"

**Output**:

# Task Breakdown: Comment System

## Overview
Feature: Add comment system to blog posts with threading and moderation
**Total Estimate**: 5-7 days
**Sprint**: 2 weeks
**Team Size**: 2 developers

## Dependency Graph
```
Foundation Layer
├─ T1: Database schema ──→ T2: API endpoints
│                          ├─ T3: Comment CRUD
│                          ├─ T4: Threading logic
│                          └─ T5: Moderation API
│
└─ T6: Type definitions ──→ T7: UI components
                            ├─ T8: Comment form
                            ├─ T9: Comment list
                            ├─ T10: Reply UI
                            └─ T11: Edit/delete

Integration Layer
└─ T12: Real-time sync ──→ T13: Notifications ──→ T14: E2E tests
```

## Tasks (In Implementation Order)

---

### T1: Create Database Schema and Migrations
**Priority**: P0 (Blocker)
**Estimate**: 2 hours
**Dependencies**: None
**Assigned**: Backend developer

**Description**:
Create PostgreSQL schema for comments with support for threading, editing history, and moderation.

**Acceptance Criteria**:
- [ ] `comments` table created with all required fields
- [ ] `comment_edit_history` table for tracking edits
- [ ] `comment_moderation_log` table for admin actions
- [ ] Indexes on `post_id` and `parent_id` for query performance
- [ ] Foreign key constraints ensure referential integrity
- [ ] Migration runs successfully on dev database
- [ ] Rollback migration works correctly

**Implementation Details**:
```sql
-- See schema in feature spec
-- Key fields: id, post_id, author_id, parent_id, content,
--   created_at, edited_at, deleted_at, is_hidden
-- Constraints: content length (10-2000 chars)
-- Indexes: (post_id, created_at), (parent_id)
```

**Test Criteria**:
- Run migration on clean DB → succeeds
- Insert sample comments → succeeds
- Query comments by post → returns in correct order
- Rollback migration → removes tables cleanly

**File Location**: `backend/prisma/migrations/001_create_comments.sql`

---

### T2: Create tRPC Comment API Endpoints
**Priority**: P0 (Blocker)
**Estimate**: 3 hours
**Dependencies**: T1
**Assigned**: Backend developer

**Description**:
Create type-safe tRPC procedures for comment CRUD operations.

**Acceptance Criteria**:
- [ ] `comments.create` - Create new comment
- [ ] `comments.list` - Get comments for post
- [ ] `comments.update` - Edit own comment
- [ ] `comments.delete` - Soft delete own comment
- [ ] `comments.moderate` - Admin hide/delete (protected)
- [ ] Input validation with Zod schemas
- [ ] Error handling for all edge cases
- [ ] Rate limiting applied (5 comments/min)

**Implementation Details**:
```typescript
// backend/src/api/routers/comments.ts
export const commentsRouter = router({
  create: protectedProcedure
    .input(z.object({
      post_id: z.string().uuid(),
      content: z.string().min(10).max(2000),
      parent_id: z.string().uuid().optional()
    }))
    .mutation(async ({ ctx, input }) => {
      // Validate post exists
      // Check parent_id exists if provided
      // Create comment
      // Notify parent author if reply
      return comment;
    }),

  list: publicProcedure
    .input(z.object({
      post_id: z.string().uuid(),
      limit: z.number().min(1).max(100).default(50)
    }))
    .query(async ({ ctx, input }) => {
      // Fetch comments with replies (tree structure)
      // Filter out hidden (unless admin)
      // Order by created_at
      return { comments, total };
    })
});
```

**Test Criteria**:
- Call `create` → comment saved to DB
- Call `list` → returns comments in tree format
- Call `update` → edits own comment only
- Call `delete` as non-owner → throws 403
- Exceed rate limit → throws 429

**File Location**: `backend/src/api/routers/comments.ts`

---

### T3: Implement Comment Threading Logic
**Priority**: P1 (High)
**Estimate**: 2 hours
**Dependencies**: T2
**Assigned**: Backend developer

**Description**:
Build recursive query to fetch comments in tree structure with max depth of 3 levels.

**Acceptance Criteria**:
- [ ] Comments returned in nested format
- [ ] Max depth of 3 levels enforced
- [ ] Beyond level 3, replies appear at level 3
- [ ] Performance: <50ms for 100 comments
- [ ] Reply count accurate for each comment

**Implementation Details**:
```typescript
// Use recursive CTE or multiple queries
// Option 1: Recursive PostgreSQL query
WITH RECURSIVE comment_tree AS (
  -- Base: top-level comments
  SELECT *, 0 as depth, ARRAY[id] as path
  FROM comments WHERE parent_id IS NULL AND post_id = $1

  UNION ALL

  -- Recursive: replies (max depth 3)
  SELECT c.*, ct.depth + 1, ct.path || c.id
  FROM comments c
  JOIN comment_tree ct ON c.parent_id = ct.id
  WHERE ct.depth < 3
)
SELECT * FROM comment_tree ORDER BY path;

// Option 2: Fetch all, build tree in-memory (simpler)
```

**Test Criteria**:
- 1-level thread → returns correctly
- 3-level thread → all replies shown
- 5-level thread → levels 4-5 appear at level 3
- 100 comments → query <50ms

**File Location**: `backend/src/services/CommentService.ts`

---

### T4: Add Comment Edit Functionality
**Priority**: P1 (High)
**Estimate**: 2 hours
**Dependencies**: T2
**Assigned**: Backend developer

**Description**:
Allow users to edit their own comments within 15-minute window, tracking edit history.

**Acceptance Criteria**:
- [ ] Users can edit own comments only
- [ ] Edit allowed within 15 minutes of posting
- [ ] Previous content saved to `comment_edit_history`
- [ ] `edited_at` timestamp updated
- [ ] `(edited)` label visible on frontend
- [ ] Admins can view edit history

**Implementation Details**:
```typescript
async updateComment(id: string, newContent: string, userId: string) {
  const comment = await prisma.comment.findUnique({ where: { id } });

  // Authorization check
  if (comment.author_id !== userId) {
    throw new ForbiddenError('Not comment author');
  }

  // Time window check
  const now = new Date();
  const elapsed = now - comment.created_at;
  if (elapsed > 15 * 60 * 1000) {
    throw new ForbiddenError('Edit window expired');
  }

  // Save to history
  await prisma.commentEditHistory.create({
    data: {
      comment_id: id,
      previous_content: comment.content
    }
  });

  // Update comment
  return prisma.comment.update({
    where: { id },
    data: {
      content: newContent,
      edited_at: now
    }
  });
}
```

**Test Criteria**:
- Edit within 15min → succeeds
- Edit after 15min → throws error
- Edit someone else's → throws 403
- History logged correctly

**File Location**: `backend/src/services/CommentService.ts`

---

### T5: Implement Moderation System
**Priority**: P2 (Medium)
**Estimate**: 2 hours
**Dependencies**: T2
**Assigned**: Backend developer

**Description**:
Admin controls to hide or delete inappropriate comments with logging.

**Acceptance Criteria**:
- [ ] Only admins can moderate
- [ ] Hide action sets `is_hidden = true`
- [ ] Delete action sets `deleted_at`
- [ ] All actions logged with reason
- [ ] Hidden comments invisible to public
- [ ] Deleted comments show "[Deleted by moderator]"

**Implementation Details**:
```typescript
async moderateComment(
  id: string,
  action: 'hide' | 'delete',
  moderatorId: string,
  reason: string
) {
  // Check moderator role
  const moderator = await prisma.user.findUnique({
    where: { id: moderatorId }
  });
  if (moderator.role !== 'ADMIN') {
    throw new ForbiddenError('Not authorized');
  }

  // Log action
  await prisma.commentModerationLog.create({
    data: { comment_id: id, moderator_id: moderatorId, action, reason }
  });

  // Apply action
  if (action === 'hide') {
    return prisma.comment.update({
      where: { id },
      data: { is_hidden: true }
    });
  } else {
    return prisma.comment.update({
      where: { id },
      data: { deleted_at: new Date() }
    });
  }
}
```

**Test Criteria**:
- Admin hides comment → `is_hidden = true`, logged
- Admin deletes → `deleted_at` set, logged
- Non-admin attempts → throws 403
- Reason required → validation error if missing

**File Location**: `backend/src/services/ModerationService.ts`

---

### T6: Generate TypeScript Types from Backend
**Priority**: P0 (Blocker for frontend)
**Estimate**: 30 minutes
**Dependencies**: T1, T2
**Assigned**: Either developer

**Description**:
Auto-generate TypeScript interfaces from Prisma schema and tRPC routers for type safety.

**Acceptance Criteria**:
- [ ] `Comment` interface matches database schema
- [ ] tRPC client has full type inference
- [ ] Generated types placed in `packages/types/`
- [ ] Build script added to package.json
- [ ] Types regenerate on schema changes

**Implementation Details**:
```bash
# Generate from Prisma
npx prisma generate

# Generate from tRPC
# Types auto-inferred by tRPC client
```

**Test Criteria**:
- Import types in frontend → no errors
- Autocomplete works in IDE
- Type mismatches caught at compile time

**File Location**: `packages/types/src/comment.ts`

---

### T7: Create CommentForm Component
**Priority**: P0 (Blocker for UI)
**Estimate**: 3 hours
**Dependencies**: T6
**Assigned**: Frontend developer

**Description**:
Reusable form for creating and replying to comments with validation.

**Acceptance Criteria**:
- [ ] Textarea with character counter
- [ ] Min 10, max 2000 characters enforced
- [ ] Submit disabled until valid
- [ ] Loading state during submission
- [ ] Error handling with user-friendly messages
- [ ] Autofocus on mount
- [ ] Cancel button for replies

**Implementation Details**:
```typescript
// components/CommentForm.tsx
interface CommentFormProps {
  postId: string;
  parentId?: string;
  onSuccess?: () => void;
  onCancel?: () => void;
}

export function CommentForm({ postId, parentId, onSuccess, onCancel }: CommentFormProps) {
  const [content, setContent] = useState('');
  const createComment = api.comments.create.useMutation();

  const handleSubmit = async () => {
    await createComment.mutateAsync({ post_id: postId, content, parent_id: parentId });
    setContent('');
    onSuccess?.();
  };

  const isValid = content.length >= 10 && content.length <= 2000;

  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Write a comment..."
        maxLength={2000}
        autoFocus
      />
      <div>
        {2000 - content.length} characters remaining
      </div>
      <button type="submit" disabled={!isValid || createComment.isLoading}>
        {createComment.isLoading ? 'Posting...' : 'Post Comment'}
      </button>
      {onCancel && <button onClick={onCancel}>Cancel</button>}
    </form>
  );
}
```

**Test Criteria**:
- Type <10 chars → submit disabled
- Type 10 chars → submit enabled
- Click submit → comment created
- Network error → shows error toast

**File Location**: `frontend/src/components/CommentForm.tsx`

---

### T8: Create CommentList Component
**Priority**: P0 (Blocker for UI)
**Estimate**: 4 hours
**Dependencies**: T6
**Assigned**: Frontend developer

**Description**:
Display comments in threaded tree format with loading and empty states.

**Acceptance Criteria**:
- [ ] Fetch comments on mount
- [ ] Display in tree structure (indent levels)
- [ ] Max 3 levels of indentation
- [ ] Loading skeleton while fetching
- [ ] Empty state: "No comments yet"
- [ ] Error state with retry button
- [ ] Pagination or infinite scroll

**Implementation Details**:
```typescript
// components/CommentList.tsx
export function CommentList({ postId }: { postId: string }) {
  const { data, isLoading, error } = api.comments.list.useQuery({ post_id: postId });

  if (isLoading) return <CommentSkeleton />;
  if (error) return <ErrorMessage onRetry={() => refetch()} />;
  if (!data.comments.length) return <EmptyState />;

  return (
    <div className="space-y-4">
      {data.comments.map(comment => (
        <CommentItem key={comment.id} comment={comment} depth={0} />
      ))}
    </div>
  );
}
```

**Test Criteria**:
- Load page → skeleton shown
- Comments load → rendered correctly
- Nested replies → indented properly
- No comments → empty state shown

**File Location**: `frontend/src/components/CommentList.tsx`

---

### T9: Create CommentItem Component
**Priority**: P0 (Blocker for UI)
**Estimate**: 3 hours
**Dependencies**: T6
**Assigned**: Frontend developer

**Description**:
Individual comment display with author, content, actions, and replies.

**Acceptance Criteria**:
- [ ] Shows author avatar and name
- [ ] Displays timestamp (relative: "2h ago")
- [ ] Content with proper text formatting
- [ ] Reply button (if <3 levels deep)
- [ ] Edit/Delete for own comments (within 15min)
- [ ] "(edited)" label if edited
- [ ] Recursively renders replies with indentation

**Implementation Details**:
```typescript
// components/CommentItem.tsx
interface CommentItemProps {
  comment: Comment;
  depth: number;
}

export function CommentItem({ comment, depth }: CommentItemProps) {
  const [showReplyForm, setShowReplyForm] = useState(false);
  const { user } = useAuth();
  const isOwner = user?.id === comment.author_id;
  const canEdit = isOwner && isWithin15Minutes(comment.created_at);
  const canReply = depth < 3;

  return (
    <div className="flex gap-3" style={{ marginLeft: `${depth * 24}px` }}>
      <Avatar src={comment.author.avatar} />
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <span className="font-medium">{comment.author.name}</span>
          <span className="text-gray-500">{formatTimestamp(comment.created_at)}</span>
          {comment.edited_at && <span className="text-gray-400">(edited)</span>}
        </div>
        <p className="mt-1">{comment.content}</p>
        <div className="flex gap-2 mt-2">
          {canReply && <button onClick={() => setShowReplyForm(true)}>Reply</button>}
          {canEdit && <button>Edit</button>}
          {isOwner && <button>Delete</button>}
        </div>
        {showReplyForm && (
          <CommentForm
            postId={comment.post_id}
            parentId={comment.id}
            onSuccess={() => setShowReplyForm(false)}
            onCancel={() => setShowReplyForm(false)}
          />
        )}
        {comment.replies?.map(reply => (
          <CommentItem key={reply.id} comment={reply} depth={depth + 1} />
        ))}
      </div>
    </div>
  );
}
```

**Test Criteria**:
- Render comment → shows all fields
- Click Reply → form appears
- Own comment → Edit/Delete visible
- Other's comment → no Edit/Delete

**File Location**: `frontend/src/components/CommentItem.tsx`

---

### T10: Add Edit Comment Functionality
**Priority**: P1 (High)
**Estimate**: 2 hours
**Dependencies**: T9
**Assigned**: Frontend developer

**Description**:
Inline editing of comments with auto-save and validation.

**Acceptance Criteria**:
- [ ] Click Edit → textarea replaces content
- [ ] Textarea pre-filled with current content
- [ ] Save button updates comment
- [ ] Cancel button reverts changes
- [ ] Character counter shown
- [ ] Optimistic update (immediate UI change)
- [ ] Error handling with rollback

**Implementation Details**:
```typescript
const [isEditing, setIsEditing] = useState(false);
const [editContent, setEditContent] = useState(comment.content);
const updateComment = api.comments.update.useMutation();

const handleSave = async () => {
  await updateComment.mutateAsync({ id: comment.id, content: editContent });
  setIsEditing(false);
};

if (isEditing) {
  return (
    <div>
      <textarea value={editContent} onChange={(e) => setEditContent(e.target.value)} />
      <button onClick={handleSave}>Save</button>
      <button onClick={() => setIsEditing(false)}>Cancel</button>
    </div>
  );
}
```

**Test Criteria**:
- Click Edit → textarea shown
- Modify → Save → comment updated
- Network error → reverts to original
- Click Cancel → discards changes

**File Location**: `frontend/src/components/CommentItem.tsx` (edit mode)

---

### T11: Add Delete Comment Functionality
**Priority**: P1 (High)
**Estimate**: 1 hour
**Dependencies**: T9
**Assigned**: Frontend developer

**Description**:
Soft delete with confirmation modal.

**Acceptance Criteria**:
- [ ] Click Delete → confirmation modal appears
- [ ] Modal: "Are you sure? This cannot be undone"
- [ ] Confirm → deletes comment
- [ ] Cancel → closes modal
- [ ] Deleted comment shows "[Deleted by user]"
- [ ] Replies remain visible

**Implementation Details**:
```typescript
const deleteComment = api.comments.delete.useMutation();

const handleDelete = async () => {
  if (confirm('Are you sure? This cannot be undone.')) {
    await deleteComment.mutateAsync({ id: comment.id });
  }
};
```

**Test Criteria**:
- Click Delete → modal shown
- Confirm → comment deleted
- Cancel → modal closed, comment remains

**File Location**: `frontend/src/components/CommentItem.tsx` (delete action)

---

### T12: Add Real-time Comment Updates
**Priority**: P2 (Nice-to-have)
**Estimate**: 4 hours
**Dependencies**: T8, T9
**Assigned**: Full-stack developer

**Description**:
WebSocket integration so new comments appear without refresh.

**Acceptance Criteria**:
- [ ] New comments appear in real-time
- [ ] Edited comments update live
- [ ] Deleted comments removed live
- [ ] Smooth animations for new items
- [ ] "Someone is typing..." indicator (future)

**Implementation Details**:
```typescript
// Server
io.to(`post:${postId}`).emit('comment:created', comment);

// Client
useEffect(() => {
  socket.on('comment:created', (comment) => {
    queryClient.setQueryData(['comments', postId], (old) => ({
      ...old,
      comments: [...old.comments, comment]
    }));
  });

  return () => socket.off('comment:created');
}, []);
```

**Test Criteria**:
- User A posts → User B sees immediately
- User A edits → User B sees update
- Works across multiple tabs

**File Location**: `frontend/src/hooks/useCommentRealtime.ts`

---

### T13: Add Comment Notifications
**Priority**: P2 (Nice-to-have)
**Estimate**: 3 hours
**Dependencies**: T2, T12
**Assigned**: Backend developer

**Description**:
Email notifications when someone replies to your comment.

**Acceptance Criteria**:
- [ ] Email sent when reply posted
- [ ] Email includes reply content
- [ ] Link to specific comment (with #anchor)
- [ ] Unsubscribe option
- [ ] Batch multiple replies (max 1 email/hour)

**Implementation Details**:
Use SendGrid or similar service.

**Test Criteria**:
- Reply to comment → parent author gets email
- Multiple replies → batched into single email
- Click link → navigates to comment

**File Location**: `backend/src/services/NotificationService.ts`

---

### T14: Write E2E Tests
**Priority**: P1 (High)
**Estimate**: 4 hours
**Dependencies**: All above
**Assigned**: QA or developer

**Description**:
Playwright tests for complete comment workflows.

**Acceptance Criteria**:
- [ ] Test: Create top-level comment
- [ ] Test: Reply to comment (threading)
- [ ] Test: Edit own comment
- [ ] Test: Delete own comment
- [ ] Test: Validation errors (too short/long)
- [ ] Test: Rate limiting

**Implementation Details**:
```typescript
// tests/e2e/comments.spec.ts
test('create and reply to comment', async ({ page }) => {
  await page.goto('/posts/test-post-id');

  // Create comment
  await page.fill('[data-testid="comment-input"]', 'This is a test comment');
  await page.click('[data-testid="submit-comment"]');
  await expect(page.locator('text=This is a test comment')).toBeVisible();

  // Reply
  await page.click('[data-testid="reply-button"]');
  await page.fill('[data-testid="reply-input"]', 'This is a reply');
  await page.click('[data-testid="submit-reply"]');
  await expect(page.locator('text=This is a reply')).toBeVisible();
});
```

**Test Criteria**:
- All tests pass in CI
- Coverage >80% for comment features

**File Location**: `tests/e2e/comments.spec.ts`

---

## Summary

**Total Tasks**: 14
**Critical Path**: T1 → T2 → T6 → T7,T8,T9 → T10,T11
**Total Effort**: 32.5 hours
**Sprint Capacity**: 2 developers × 8 hours/day × 5 days = 80 hours
**Buffer**: 40% for unknowns = 13 hours
**Risk Level**: Medium (some real-time complexity)

## Task Templates

### Backend Task Template
```
### Task ID: [TITLE]
**Priority**: [P0/P1/P2]
**Estimate**: [X hours]
**Dependencies**: [Previous tasks]
**Assigned**: [Developer]

**Description**:
[One sentence description of what this task accomplishes]

**Acceptance Criteria**:
- [ ] [Specific, testable outcome]
- [ ] [Another outcome]
- [ ] [Error handling or edge case]

**Implementation Details**:
[Code snippets, architectural decisions, important considerations]

**Test Criteria**:
[How to verify this task is complete]

**File Location**: [Where files will be created/modified]
```

### Frontend Task Template
```
### Task ID: [TITLE]
**Priority**: [P0/P1/P2]
**Estimate**: [X hours]
**Dependencies**: [Previous tasks]
**Assigned**: [Developer]

**Description**:
[What component/functionality is being built]

**Acceptance Criteria**:
- [ ] [Visual/interaction requirement]
- [ ] [State management requirement]
- [ ] [Accessibility requirement]
- [ ] [Error state handling]

**Implementation Details**:
[Component structure, props interface, hooks to use]

**Test Criteria**:
[Unit test scenarios, integration test scenarios]

**File Location**: [Component file path]
```

## Estimation Guidelines

### T-Shirt Sizes
- **XS** (1-2 hours): Simple component, bug fix
- **S** (2-4 hours): Small feature, simple API endpoint
- **M** (4-8 hours): Medium feature, multiple components
- **L** (8-16 hours): Complex feature, multiple dependencies
- **XL** (16+ hours): Large feature, should be broken down

### Dependency Rules
1. **Database before API**: Schema must exist before endpoints
2. **API before UI**: Types must be available before components
3. **Foundation before features**: Authentication, routing, etc.
4. **Simple before complex**: Basic CRUD before advanced features

## Sprint Planning Tips

### Task Selection
- Start with P0 tasks (blockers)
- Group related tasks by developer expertise
- Balance backend and frontend work
- Include testing tasks in sprint

### Risk Mitigation
- Add buffer time for unknowns (20-30%)
- Identify spike tasks for research
- Plan for integration complexity
- Consider external dependencies

## Best Practices
1. **Atomic Tasks**: Each task should be mergeable independently
2. **Clear Acceptance**: Criteria must be objectively verifiable
3. **Logical Dependencies**: Follow natural build sequence
4. **Balanced Estimates**: Account for complexity and unknowns
5. **Test-Driven**: Include testing in task breakdown
6. **Documentation**: Update relevant docs as part of tasks
7. **Review Ready**: Tasks should be clear enough for peer review

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Current architecture, existing patterns, dependency management |
| **Conversation** | User's specific feature requirements, timeline constraints, team capacity |
| **Skill References** | Task decomposition patterns, estimation techniques, sprint planning best practices |
| **User Guidelines** | Project-specific conventions, coding standards, deployment requirements |