---
name: implementation-guide
description: |
  Convert specifications into actionable Claude Code prompts with file-by-file instructions, code snippets, and validation steps.
---

# Implementation Guide

Convert specifications into actionable Claude Code prompts with file-by-file instructions, code snippets, and validation steps.

## When to Use This Skill
- Ready to start coding from specs
- User asks "how do I implement this?"
- Need step-by-step Claude Code prompts
- Converting tasks into executable commands

## Procedure
1. **Extract task details**: What to build, where, dependencies
2. **Generate file structure**: What files to create/modify
3. **Write Claude prompts**: Specific, actionable instructions
4. **Include validation**: How to verify it works
5. **Add troubleshooting**: Common issues and fixes

## Output Format
**Implementation Guide**:
- Task overview with context
- File-by-file implementation prompts
- Code snippets and examples
- Validation commands
- Troubleshooting tips

## Quality Criteria
- Prompts are copy-paste ready
- Each step is independently executable
- Files are referenced with exact paths
- Code examples are complete and correct
- Validation steps prove it works
- Dependencies are called out explicitly

## Example
**Input**: "Create implementation guide for Task T1: Database Schema"

**Output**:

# Implementation Guide: Comment System Database Schema (Task T1)

## Task Context
**Task ID**: T1
**Title**: Create Database Schema and Migrations
**Priority**: P0 (Blocker)
**Estimate**: 2 hours
**Dependencies**: None
**Assignee**: Backend developer

**Objective**: Create PostgreSQL schema for comments with threading support, edit history, and moderation logging using Prisma ORM.

---

## Prerequisites

Before starting, ensure:
- [ ] Prisma is installed in the project (`npm install prisma @prisma/client`)
- [ ] Database connection configured in `.env` (`DATABASE_URL`)
- [ ] PostgreSQL database is running and accessible

**Verify Setup**:
```bash
# Check Prisma is installed
npx prisma --version

# Test database connection
npx prisma db pull
```

---

## Implementation Steps

### Step 1: Update Prisma Schema

**Claude Code Prompt**:
```
Update the Prisma schema file to include the comments system models.

File: backend/prisma/schema.prisma

Add three new models:
1. Comment - Main comments table with threading support
2. CommentEditHistory - Track all edits to comments
3. CommentModerationLog - Log all moderation actions

Requirements:
- Comment should have: id (UUID), post_id (UUID), author_id (UUID), parent_id (UUID nullable),
  content (TEXT), created_at, edited_at (nullable), deleted_at (nullable), is_hidden (boolean), version (int)
- Content must be between 10 and 2000 characters
- Include indexes on (post_id, created_at) and (parent_id)
- Foreign keys: post_id → Post, author_id → User, parent_id → Comment (self-reference)
- CommentEditHistory: id, comment_id, previous_content, edited_at
- CommentModerationLog: id, comment_id, moderator_id, action, reason, created_at

Use Prisma syntax with proper relations and constraints.
```

**Expected Output** (`backend/prisma/schema.prisma`):
```prisma
// ... existing models ...

model Comment {
  id          String    @id @default(uuid())
  post_id     String
  author_id   String
  parent_id   String?
  content     String    @db.Text
  version     Int       @default(1)
  created_at  DateTime  @default(now())
  edited_at   DateTime?
  deleted_at  DateTime?
  is_hidden   Boolean   @default(false)

  // Relations
  post        Post      @relation(fields: [post_id], references: [id], onDelete: Cascade)
  author      User      @relation("AuthoredComments", fields: [author_id], references: [id], onDelete: Cascade)
  parent      Comment?  @relation("CommentReplies", fields: [parent_id], references: [id], onDelete: SetNull)

  // Self-referencing relation for replies
  replies     Comment[] @relation("CommentReplies")

  // Related records
  edit_history    CommentEditHistory[]
  moderation_logs CommentModerationLog[]

  // Indexes for performance
  @@index([post_id, created_at])
  @@index([parent_id])
  @@index([author_id])
}

model CommentEditHistory {
  id               String   @id @default(uuid())
  comment_id       String
  previous_content String   @db.Text
  edited_at        DateTime @default(now())

  comment Comment @relation(fields: [comment_id], references: [id], onDelete: Cascade)

  @@index([comment_id, edited_at])
}

model CommentModerationLog {
  id           String   @id @default(uuid())
  comment_id   String
  moderator_id String
  action       String   // 'hide', 'delete', 'approve'
  reason       String?  @db.Text
  created_at   DateTime @default(now())

  comment   Comment @relation(fields: [comment_id], references: [id], onDelete: Cascade)
  moderator User    @relation("ModeratorActions", fields: [moderator_id], references: [id], onDelete: Cascade)

  @@index([comment_id])
  @@index([moderator_id])
}

// Update User model to include comment relations
model User {
  // ... existing fields ...

  authored_comments Comment[]             @relation("AuthoredComments")
  moderation_actions CommentModerationLog[] @relation("ModeratorActions")
}

// Update Post model to include comments relation
model Post {
  // ... existing fields ...

  comments Comment[]
}
```

**Validation**:
```bash
# Check schema syntax
npx prisma format

# Validate schema
npx prisma validate
```

---

### Step 2: Generate and Apply Migration

**Claude Code Prompt**:
```
Generate a Prisma migration for the comments system schema changes.

Run these commands:
1. Generate migration with a descriptive name
2. Review the generated SQL
3. Apply migration to database

Migration name: "add_comments_system"

After migration, verify:
- All three tables created (comments, comment_edit_history, comment_moderation_log)
- Indexes exist
- Foreign key constraints work
- Check constraint on content length is applied
```

**Manual Commands**:
```bash
# Generate migration
npx prisma migrate dev --name add_comments_system

# This will:
# 1. Generate migration SQL in prisma/migrations/
# 2. Apply it to your database
# 3. Regenerate Prisma Client

# If you want to preview SQL without applying:
npx prisma migrate dev --create-only --name add_comments_system
```

**Expected Migration SQL** (`backend/prisma/migrations/XXXXXX_add_comments_system/migration.sql`):
```sql
-- CreateTable
CREATE TABLE "Comment" (
    "id" TEXT NOT NULL,
    "post_id" TEXT NOT NULL,
    "author_id" TEXT NOT NULL,
    "parent_id" TEXT,
    "content" TEXT NOT NULL,
    "version" INTEGER NOT NULL DEFAULT 1,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "edited_at" TIMESTAMP(3),
    "deleted_at" TIMESTAMP(3),
    "is_hidden" BOOLEAN NOT NULL DEFAULT false,

    CONSTRAINT "Comment_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CommentEditHistory" (
    "id" TEXT NOT NULL,
    "comment_id" TEXT NOT NULL,
    "previous_content" TEXT NOT NULL,
    "edited_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "CommentEditHistory_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CommentModerationLog" (
    "id" TEXT NOT NULL,
    "comment_id" TEXT NOT NULL,
    "moderator_id" TEXT NOT NULL,
    "action" TEXT NOT NULL,
    "reason" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "CommentModerationLog_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "Comment_post_id_created_at_idx" ON "Comment"("post_id", "created_at");

-- CreateIndex
CREATE INDEX "Comment_parent_id_idx" ON "Comment"("parent_id");

-- CreateIndex
CREATE INDEX "Comment_author_id_idx" ON "Comment"("author_id");

-- CreateIndex
CREATE INDEX "CommentEditHistory_comment_id_edited_at_idx" ON "CommentEditHistory"("comment_id", "edited_at");

-- CreateIndex
CREATE INDEX "CommentModerationLog_comment_id_idx" ON "CommentModerationLog"("comment_id");

-- CreateIndex
CREATE INDEX "CommentModerationLog_moderator_id_idx" ON "CommentModerationLog"("moderator_id");

-- AddForeignKey
ALTER TABLE "Comment" ADD CONSTRAINT "Comment_post_id_fkey" FOREIGN KEY ("post_id") REFERENCES "Post"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Comment" ADD CONSTRAINT "Comment_author_id_fkey" FOREIGN KEY ("author_id") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Comment" ADD CONSTRAINT "Comment_parent_id_fkey" FOREIGN KEY ("parent_id") REFERENCES "Comment"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CommentEditHistory" ADD CONSTRAINT "CommentEditHistory_comment_id_fkey" FOREIGN KEY ("comment_id") REFERENCES "Comment"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CommentModerationLog" ADD CONSTRAINT "CommentModerationLog_comment_id_fkey" FOREIGN KEY ("comment_id") REFERENCES "Comment"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CommentModerationLog" ADD CONSTRAINT "CommentModerationLog_moderator_id_fkey" FOREIGN KEY ("moderator_id") REFERENCES "User"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- Add check constraint for content length
ALTER TABLE "Comment" ADD CONSTRAINT "Comment_content_length_check"
  CHECK (LENGTH(content) >= 10 AND LENGTH(content) <= 2000);
```

**Validation**:
```bash
# Check migration status
npx prisma migrate status

# Connect to database and verify
npx prisma studio
# Navigate to Comment, CommentEditHistory, CommentModerationLog models
# Verify structure

# Or use psql:
psql $DATABASE_URL -c "\d comments"
psql $DATABASE_URL -c "\d comment_edit_history"
psql $DATABASE_URL -c "\d comment_moderation_log"
```

---

### Step 3: Create Seed Data (Optional for Testing)

**Claude Code Prompt**:
```
Create a seed script to populate the database with sample comments for testing.

File: backend/prisma/seed.ts

Create:
- 2 blog posts (if not exist)
- 3 users (if not exist)
- 5 top-level comments on post 1
- 3 replies to comment 1 (threading test)
- 1 edited comment (with edit history)
- 1 deleted comment
- 1 hidden comment (moderated)

Use realistic test data with proper timestamps.
```

**Expected Output** (`backend/prisma/seed.ts`):
```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient();

async function main() {
  console.log('🌱 Seeding database...');

  // Create test users
  const alice = await prisma.user.upsert({
    where: { email: 'alice@example.com' },
    update: {},
    create: {
      email: 'alice@example.com',
      name: 'Alice Chen',
      avatar_url: 'https://i.pravatar.cc/150?u=alice'
    }
  });

  const bob = await prisma.user.upsert({
    where: { email: 'bob@example.com' },
    update: {},
    create: {
      email: 'bob@example.com',
      name: 'Bob Smith',
      avatar_url: 'https://i.pravatar.cc/150?u=bob'
    }
  });

  const carol = await prisma.user.upsert({
    where: { email: 'carol@example.com' },
    update: {},
    create: {
      email: 'carol@example.com',
      name: 'Carol Davis',
      avatar_url: 'https://i.pravatar.cc/150?u=carol',
      role: 'ADMIN' // For moderation testing
    }
  });

  // Create test post
  const post = await prisma.post.upsert({
    where: { id: 'test-post-1' },
    update: {},
    create: {
      id: 'test-post-1',
      title: 'Getting Started with TypeScript',
      content: 'TypeScript is a typed superset of JavaScript...',
      author_id: alice.id,
      published: true
    }
  });

  // Top-level comments
  const comment1 = await prisma.comment.create({
    data: {
      post_id: post.id,
      author_id: alice.id,
      content: 'Great article! TypeScript has really improved our codebase quality.'
    }
  });

  const comment2 = await prisma.comment.create({
    data: {
      post_id: post.id,
      author_id: bob.id,
      content: 'I have a question about generics. Can you explain more?'
    }
  });

  // Nested replies (threading)
  const reply1 = await prisma.comment.create({
    data: {
      post_id: post.id,
      author_id: alice.id,
      parent_id: comment1.id,
      content: 'Thanks! Glad you found it helpful. What specific areas improved for you?'
    }
  });

  const reply2 = await prisma.comment.create({
    data: {
      post_id: post.id,
      author_id: bob.id,
      parent_id: reply1.id,
      content: 'Mainly catching type errors at compile time instead of runtime.'
    }
  });

  // Edited comment
  const editedComment = await prisma.comment.create({
    data: {
      post_id: post.id,
      author_id: alice.id,
      content: 'Updated: TypeScript 5.0 adds even more features!',
      edited_at: new Date(),
      version: 2
    }
  });

  await prisma.commentEditHistory.create({
    data: {
      comment_id: editedComment.id,
      previous_content: 'TypeScript 5.0 adds new features!',
      edited_at: new Date(Date.now() - 60000) // 1 min ago
    }
  });

  // Deleted comment
  await prisma.comment.create({
    data: {
      post_id: post.id,
      author_id: bob.id,
      content: '[This comment was deleted by the author]',
      deleted_at: new Date()
    }
  });

  // Hidden comment (moderated)
  const hiddenComment = await prisma.comment.create({
    data: {
      post_id: post.id,
      author_id: bob.id,
      content: 'This comment was inappropriate',
      is_hidden: true
    }
  });

  await prisma.commentModerationLog.create({
    data: {
      comment_id: hiddenComment.id,
      moderator_id: carol.id,
      action: 'hide',
      reason: 'Violated community guidelines'
    }
  });

  console.log('✅ Seed completed');
  console.log(`Created ${await prisma.comment.count()} comments`);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
```

**Run Seed**:
```bash
# Add to package.json if not present
# "prisma": { "seed": "ts-node prisma/seed.ts" }

# Run seed
npx prisma db seed
```

**Validation**:
```bash
# View seeded data
npx prisma studio

# Or query directly
npx ts-node -e "
  import { PrismaClient } from '@prisma/client';
  const prisma = new PrismaClient();
  prisma.comment.findMany({ include: { author: true, replies: true } })
    .then(console.log)
    .finally(() => prisma.\$disconnect());
"
```

---

### Step 4: Test Database Operations

**Claude Code Prompt**:
```
Create a test file to validate all database operations work correctly.

File: backend/tests/comment-db.test.ts

Test scenarios:
1. Create top-level comment
2. Create nested reply (threading)
3. Prevent replies deeper than 3 levels
4. Content length validation (10-2000 chars)
5. Cascade delete (delete post → comments deleted)
6. Edit history tracking
7. Moderation logging

Use Jest or Vitest with Prisma test environment.
```

**Expected Output** (`backend/tests/comment-db.test.ts`):
```typescript
import { PrismaClient } from '@prisma/client';
import { beforeEach, afterEach, describe, it, expect } from 'vitest';

const prisma = new PrismaClient();

describe('Comment Database Operations', () => {
  let testUserId: string;
  let testPostId: string;

  beforeEach(async () => {
    // Create test user and post
    const user = await prisma.user.create({
      data: {
        email: `test-${Date.now()}@example.com`,
        name: 'Test User'
      }
    });
    testUserId = user.id;

    const post = await prisma.post.create({
      data: {
        title: 'Test Post',
        content: 'Test content',
        author_id: testUserId
      }
    });
    testPostId = post.id;
  });

  afterEach(async () => {
    // Cleanup
    await prisma.comment.deleteMany();
    await prisma.post.deleteMany();
    await prisma.user.deleteMany();
  });

  it('should create a top-level comment', async () => {
    const comment = await prisma.comment.create({
      data: {
        post_id: testPostId,
        author_id: testUserId,
        content: 'This is a test comment with enough characters'
      }
    });

    expect(comment.id).toBeDefined();
    expect(comment.parent_id).toBeNull();
    expect(comment.version).toBe(1);
  });

  it('should create nested replies', async () => {
    const parent = await prisma.comment.create({
      data: {
        post_id: testPostId,
        author_id: testUserId,
        content: 'Parent comment with sufficient length'
      }
    });

    const reply = await prisma.comment.create({
      data: {
        post_id: testPostId,
        author_id: testUserId,
        parent_id: parent.id,
        content: 'Reply with sufficient character count'
      }
    });

    expect(reply.parent_id).toBe(parent.id);
  });

  it('should enforce content length constraints', async () => {
    // Too short
    await expect(
      prisma.comment.create({
        data: {
          post_id: testPostId,
          author_id: testUserId,
          content: 'Short' // Only 5 chars
        }
      })
    ).rejects.toThrow();

    // Too long
    const longContent = 'a'.repeat(2001);
    await expect(
      prisma.comment.create({
        data: {
          post_id: testPostId,
          author_id: testUserId,
          content: longContent
        }
      })
    ).rejects.toThrow();
  });

  it('should track edit history', async () => {
    const comment = await prisma.comment.create({
      data: {
        post_id: testPostId,
        author_id: testUserId,
        content: 'Original content that meets minimum length'
      }
    });

    // Update comment and log history
    await prisma.commentEditHistory.create({
      data: {
        comment_id: comment.id,
        previous_content: comment.content
      }
    });

    await prisma.comment.update({
      where: { id: comment.id },
      data: {
        content: 'Updated content that also meets length requirement',
        edited_at: new Date(),
        version: { increment: 1 }
      }
    });

    const history = await prisma.commentEditHistory.findMany({
      where: { comment_id: comment.id }
    });

    expect(history).toHaveLength(1);
    expect(history[0].previous_content).toBe('Original content that meets minimum length');
  });

  it('should cascade delete comments when post is deleted', async () => {
    await prisma.comment.create({
      data: {
        post_id: testPostId,
        author_id: testUserId,
        content: 'Comment that will be deleted with post'
      }
    });

    await prisma.post.delete({ where: { id: testPostId } });

    const comments = await prisma.comment.findMany({
      where: { post_id: testPostId }
    });

    expect(comments).toHaveLength(0);
  });
});
```

**Run Tests**:
```bash
# Run all tests
npm test

# Run specific test file
npm test comment-db.test.ts

# Run with coverage
npm test -- --coverage
```

---

## Validation Checklist

After completing all steps, verify:

- [ ] **Schema Valid**: `npx prisma validate` passes
- [ ] **Migration Applied**: Tables exist in database
- [ ] **Indexes Created**: Check `\d comments` shows indexes
- [ ] **Foreign Keys Work**: Can reference User, Post, Comment tables
- [ ] **Check Constraints**: Content length enforced (10-2000)
- [ ] **Seed Data Loads**: `npx prisma db seed` succeeds
- [ ] **Prisma Studio**: Can view/edit comments in UI
- [ ] **Tests Pass**: All database operation tests green

---

## Troubleshooting

### Issue: Migration fails with "relation already exists"
**Solution**:
```bash
# Reset database (⚠️ destroys data)
npx prisma migrate reset

# Or create new migration
npx prisma migrate dev --name fix_schema
```

### Issue: Constraint violation on content length
**Problem**: Existing data doesn't meet 10-2000 char requirement

**Solution**:
```sql
-- Find violating records
SELECT id, LENGTH(content) as len
FROM comments
WHERE LENGTH(content) < 10 OR LENGTH(content) > 2000;

-- Fix or delete them before adding constraint
```

### Issue: Foreign key constraint fails
**Problem**: Referenced user/post doesn't exist

**Solution**:
```bash
# Ensure Post and User models exist in schema
# Run migrations in correct order
npx prisma migrate deploy
```

### Issue: Prisma Client not updated
**Problem**: Types don't match schema

**Solution**:
```bash
# Regenerate Prisma Client
npx prisma generate

# Restart TypeScript server in IDE
```

---

## Next Steps

After T1 is complete:
1. ✅ Commit and push schema changes
2. ✅ Update API documentation with new models
3. ➡️ **Proceed to T2**: Create tRPC API endpoints
4. ➡️ **Proceed to T6**: Generate TypeScript types for frontend

---

## Time Tracking

**Estimated**: 2 hours
**Actual**: [Fill in after completion]

---

## Best Practices

### 1. File Organization
- Keep related files together in logical directories
- Use consistent naming conventions
- Group related functionality in the same modules

### 2. Code Quality
- Write type-safe code with proper TypeScript interfaces
- Include comprehensive error handling
- Add meaningful comments for complex logic
- Follow established patterns in the codebase

### 3. Validation
- Always test database constraints and relationships
- Validate foreign key constraints work properly
- Test edge cases and error conditions
- Verify performance with realistic data volumes

### 4. Documentation
- Update API documentation after changes
- Add inline comments for complex business logic
- Document any non-obvious implementation decisions
- Keep README files updated with new features

### 5. Testing
- Write unit tests for all business logic
- Test both happy path and error cases
- Include integration tests for database operations
- Test performance under expected load

## Implementation Template

### For New Features

Use this template to create implementation guides for new features:

```
# Implementation Guide: [FEATURE NAME] ([TASK ID])

## Task Context
**Task ID**: [TASK ID]
**Title**: [TASK TITLE]
**Priority**: [P0/P1/P2/P3]
**Estimate**: [TIME ESTIMATE]
**Dependencies**: [ANY DEPENDENCIES]
**Assignee**: [ASSIGNEE]

**Objective**: [ONE SENTENCE DESCRIPTION OF WHAT TO BUILD]

---

## Prerequisites

Before starting, ensure:
- [ ] [PREREQUISITE 1]
- [ ] [PREREQUISITE 2]
- [ ] [PREREQUISITE 3]

**Verify Setup**:
```bash
[VERIFICATION COMMANDS]
```

---

## Implementation Steps

### Step 1: [STEP NAME]

**Claude Code Prompt**:
```
[PROMPT CONTENT]
```

**Expected Output** (`[FILE PATH]`):
```[LANGUAGE]
[CODE EXAMPLE]
```

**Validation**:
```bash
[VALIDATION COMMANDS]
```

---

## Validation Checklist

After completing all steps, verify:

- [ ] [CHECKPOINT 1]
- [ ] [CHECKPOINT 2]
- [ ] [CHECKPOINT 3]

---

## Troubleshooting

### Issue: [COMMON ISSUE]
**Solution**:
```bash
[SOLUTION COMMANDS]
```

---

## Next Steps

After [TASK ID] is complete:
1. ✅ [NEXT STEP 1]
2. ✅ [NEXT STEP 2]
3. ➡️ **Proceed to [NEXT TASK]**: [DESCRIPTION]
```

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing patterns, architecture, testing frameworks, dependency management |
| **Conversation** | User's specific implementation requirements, timeline constraints, team preferences |
| **Skill References** | Implementation best practices, framework-specific patterns, testing strategies |
| **User Guidelines** | Project-specific coding standards, deployment requirements, security policies |