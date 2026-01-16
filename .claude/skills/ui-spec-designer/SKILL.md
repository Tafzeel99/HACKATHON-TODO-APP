---
name: ui-spec-designer
description: |
  Create detailed UI specifications with component hierarchies, layouts, interactions, states, and design tokens.
---

# UI Spec Designer

Create detailed UI specifications with component hierarchies, layouts, interactions, states, and design tokens.

## When to Use This Skill
- Designing new pages or features
- User mentions "UI design" or "component specs"
- Need to translate mockups into implementation specs
- Planning component library structure

## Procedure
1. **Define page layout**: Grid, sections, responsive breakpoints
2. **Component hierarchy**: Parent-child relationships
3. **Interaction states**: Default, hover, active, disabled, loading, error
4. **Data binding**: What props/state each component needs
5. **Design tokens**: Colors, spacing, typography

## Output Format
**UI Specification**:
- Page layout and structure
- Component tree with props
- Interaction states and transitions
- Responsive behavior
- Accessibility requirements
- Design system tokens

## Quality Criteria
- Components are reusable and composable
- States cover all user scenarios
- Responsive design works across devices
- Accessibility standards met (WCAG 2.1 AA)
- Design tokens are consistent and scalable

## Example
**Input**: "Design UI spec for task detail page with real-time collaboration"

**Output**:

# UI Spec: Task Detail Page

## Page Layout
```
┌─────────────────────────────────────────────────────────────┐
│ Header: Logo | Navigation | User Profile                    │
├─────────────────────────────────────────────────────────────┤
│ Breadcrumb: Home > Project > Task                           │
├─────────────────────────────────────────────────────────────┤
│ Main Content Area                                           │
│ ┌─────────────────────────┬─────────────────────────────────┐│
│ │    Main Content         │        Sidebar                ││
│ │    (70%)               │        (30%)                  ││
│ │                         │                               ││
│ │  ┌───────────────────┐  │  ┌─────────────────────────┐  ││
│ │  │ Task Header       │  │  │ Metadata              │  ││
│ │  │                   │  │  │ Assignee, Due Date,   │  ││
│ │  │ Title             │  │  │ Status, Priority      │  ││
│ │  │ Description       │  │  │                       │  ││
│ │  │ Subtasks          │  │  ├─────────────────────────┤  ││
│ │  │ Comments          │  │  │ Activity Feed         │  ││
│ │  │ Activity Feed     │  │  │                       │  ││
│ │  └───────────────────┘  │  │                       │  ││
│ │                         │  │                       │  ││
│ └─────────────────────────┴─────────────────────────────────┘│
│ Footer: Copyright, Links                                    │
└─────────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. TaskHeader
**Purpose**: Title, description, and main actions

**Props**:
```typescript
interface TaskHeaderProps {
  title: string;
  description: string;
  isEditing: boolean;
  canEdit: boolean;
  onSave: (title: string, description: string) => void;
  onCancel: () => void;
  onEdit: () => void;
}
```

**Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  [Title]                              [Edit] [Menu]        │
├─────────────────────────────────────────────────────────────┤
│  [Description]                                              │
│  [Edit Description]                                         │
│  [Save] [Cancel]                                            │
└─────────────────────────────────────────────────────────────┘
```

**States**:
- **Default**: Title is text, menu collapsed
- **Editing**: Title is input field, auto-focus
- **Saving**: Loading spinner on title
- **Error**: Red border, error message below

**Interactions**:
- Click title → Edit mode
- Blur/Enter → Save
- Escape → Cancel edit
- Menu click → Dropdown with options

**Responsive**:
- Mobile: Stack title and actions vertically
- Actions become hamburger menu

### 2. DescriptionEditor
**Purpose**: Rich text editing for task description

**Props**:
```typescript
interface DescriptionEditorProps {
  content: string;
  onChange: (content: string) => void;
  readOnly?: boolean;
  placeholder?: string;
  mentions?: User[];
}
```

**Layout**:
```
┌────────────────────────────────────────┐
│  Description                      Edit │
├────────────────────────────────────────┤
│  [Rich text content]                   │
│  - Supports markdown                   │
│  - @mentions                           │
│  - Links                               │
│                                        │
│  Last edited by Alice, 2 hours ago     │
└────────────────────────────────────────┘
```

**States**:
- **Read-only**: No border, subtle background
- **Edit mode**: Border, toolbar visible
- **Empty**: Show placeholder
- **Saving**: Spinner in toolbar
- **Error**: Red border, error toast

**Toolbar** (Edit mode):
```
[B] [I] [U] [Link] [@] [•List] [1.List] [Code]
```

**Interactions**:
- Click anywhere → Enter edit mode
- @ trigger → Show user mention menu
- Auto-save on blur (debounced 500ms)
- Ctrl+B/I/U → Format shortcuts

**Accessibility**:
- `role="textbox"`
- `aria-label="Task description"`
- `aria-describedby="save-status"`

### 3. CommentSection
**Purpose**: Discussion and collaboration

**Props**:
```typescript
interface CommentSectionProps {
  comments: Comment[];
  onAddComment: (content: string) => void;
  canComment: boolean;
  currentUser: User;
}
```

**Layout**:
```
┌────────────────────────────────────────┐
│  Comments (12)                        │
├────────────────────────────────────────┤
│  [Comment 1]                          │
│  ┌──────────────────────────────────┐  │
│  │ [Avatar] [User] • 2h ago       │  │
│  │ Content of the comment...        │  │
│  │ [Like] [Reply] [...]           │  │
│  └──────────────────────────────────┘  │
│  [Comment 2]                          │
│  ┌──────────────────────────────────┐  │
│  │ ...                              │  │
│  └──────────────────────────────────┘  │
│  [Add Comment]                        │
│  ┌──────────────────────────────────┐  │
│  │ [Avatar] [Input] [Send]        │  │
│  └──────────────────────────────────┘  │
└────────────────────────────────────────┘
```

**States**:
- **Loading**: Skeleton for comments
- **Empty**: "No comments yet. Be the first!"
- **Posting**: Disable form, show spinner
- **Error**: Toast notification

**Real-time Behavior**:
- New comments appear with animation
- "Someone is typing..." indicator
- Optimistic updates (immediate show)
- Rollback on failure

### 4. SubtaskList
**Purpose**: Checklist of sub-items

**Props**:
```typescript
interface SubtaskListProps {
  subtasks: Subtask[];
  onToggle: (id: string) => void;
  onAdd: (title: string) => void;
  onDelete: (id: string) => void;
  canEdit: boolean;
}
```

**Layout**:
```
┌────────────────────────────────────────┐
│  Subtasks (2 of 5 completed)          │
├────────────────────────────────────────┤
│  [✓] Design mockups                   │
│  [✓] Review with team                 │
│  [ ] Implement frontend                │
│  [ ] Write tests                       │
│  [ ] Deploy to staging                 │
│  + Add subtask                         │
└────────────────────────────────────────┘
```

**States**:
- **Completed**: Strikethrough, gray text
- **Incomplete**: Normal text
- **Adding**: Input field appears
- **Deleting**: Fade out animation

**Interactions**:
- Click checkbox → Toggle complete
- Click "+ Add" → Show input
- Enter on input → Create subtask
- Hover → Show delete icon
- Drag → Reorder (future)

### 5. ActivityFeed
**Purpose**: Timeline of task changes

**Props**:
```typescript
interface ActivityFeedProps {
  activities: Activity[];
  limit?: number;
}

interface Activity {
  id: string;
  type: 'created' | 'updated' | 'commented' | 'assigned';
  actor: User;
  timestamp: Date;
  details: string;
}
```

**Layout**:
```
┌────────────────────────────────────────┐
│  Activity                             │
├────────────────────────────────────────┤
│  [Avatar] John updated status         │
│           2 hours ago                 │
│  [Avatar] Sarah commented             │
│           3 hours ago                 │
│  [Avatar] Mike assigned task          │
│           Yesterday                   │
└────────────────────────────────────────┘
```

**States**:
- **Loading**: Skeleton rows
- **Empty**: "No activity yet"
- **Limited**: Show "View more" button
- **Real-time**: New items animate in

**Timestamps**: (<24h: "2h ago", >24h: "Jan 15")

### 6. PresenceIndicator
**Purpose**: Show who's viewing the task

**Props**:
```typescript
interface PresenceIndicatorProps {
  viewers: User[];
  currentUser: User;
}
```

**Layout**:
```
┌──────────────────────────────────────┐
│  👁️ Viewing now:                     │
│  [Avatar][Avatar][Avatar] +2 more    │
└──────────────────────────────────────┘
```

**Position**: Floating, bottom-right corner

**States**:
- **Solo**: Hide component
- **Multiple**: Show first 3 avatars + count
- **Hover**: Tooltip with names

**Real-time**:
- Join: Avatar fades in
- Leave: Avatar fades out after 30s
- Heartbeat every 15s

## Interaction States

### Button States
```
Default    → bg-blue-600, text-white
Hover      → bg-blue-700
Active     → bg-blue-800, scale-95
Disabled   → bg-gray-300, cursor-not-allowed
Loading    → bg-blue-600, spinner inside
```

### Input States
```
Default    → border-gray-300
Focus      → border-blue-500, ring-2 ring-blue-200
Error      → border-red-500, text-red-600
Disabled   → bg-gray-100, cursor-not-allowed
Success    → border-green-500
```

### Card States
```
Default    → border-gray-200, shadow-sm
Hover      → shadow-md (if clickable)
Active     → border-blue-500
Loading    → Skeleton placeholder
Error      → border-red-500, bg-red-50
```

## Design Tokens

### Colors
```css
/* Primary */
--color-primary-50:  #eff6ff;
--color-primary-500: #3b82f6;
--color-primary-600: #2563eb;

/* Semantic */
--color-success: #10b981;
--color-warning: #f59e0b;
--color-error:   #ef4444;
--color-info:    #3b82f6;

/* Neutral */
--color-gray-50:  #f9fafb;
--color-gray-100: #f3f4f6;
--color-gray-900: #111827;
```

### Typography
```css
--font-family: 'Inter', system-ui, sans-serif;

/* Sizes */
--text-xs:   0.75rem;  /* 12px */
--text-sm:   0.875rem; /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg:   1.125rem; /* 18px */
--text-xl:   1.25rem;  /* 20px */
--text-2xl:  1.5rem;   /* 24px */

/* Weights */
--font-normal:   400;
--font-medium:   500;
--font-semibold: 600;
--font-bold:     700;
```

### Spacing
```css
/* Scale: 4px base */
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
```

### Borders
```css
--border-radius-sm: 0.25rem;  /* 4px */
--border-radius-md: 0.375rem; /* 6px */
--border-radius-lg: 0.5rem;   /* 8px */
--border-radius-xl: 0.75rem;  /* 12px */

--border-width: 1px;
--border-width-thick: 2px;
```

### Shadows
```css
--shadow-sm:  0 1px 2px rgba(0, 0, 0, 0.05);
--shadow-md:  0 4px 6px rgba(0, 0, 0, 0.1);
--shadow-lg:  0 10px 15px rgba(0, 0, 0, 0.1);
--shadow-xl:  0 20px 25px rgba(0, 0, 0, 0.15);
```

## Responsive Breakpoints

```css
/* Mobile First */
--breakpoint-sm: 640px;   /* Tablet */
--breakpoint-md: 768px;   /* Small laptop */
--breakpoint-lg: 1024px;  /* Desktop */
--breakpoint-xl: 1280px;  /* Large desktop */
```

### Layout Changes

**Mobile (<640px)**:
- Single column layout
- Right sidebar moves below main content
- Action menu becomes hamburger
- Comments collapse by default

**Tablet (640px - 1024px)**:
- Two column but narrower gaps
- Sidebar 40% width
- Metadata cards stack

**Desktop (>1024px)**:
- Full two-column layout
- Sidebar 33% width
- All features visible

## Accessibility Requirements

### Keyboard Navigation
- Tab order: Header → Main → Sidebar → Footer
- Escape closes modals/dropdowns
- Enter/Space activates buttons
- Arrow keys navigate menus

### ARIA Labels
```html
<!-- Task Title -->
<input
  aria-label="Task title"
  aria-required="true"
  aria-invalid={hasError}
/>

<!-- Comments -->
<section aria-label="Comments">
  <ul role="list">
    <li role="article">
      <div role="region" aria-label="Comment by Alice">
        ...
      </div>
    </li>
  </ul>
</section>

<!-- Status Dropdown -->
<button
  aria-haspopup="listbox"
  aria-expanded={isOpen}
  aria-controls="status-menu"
>
  Status
</button>
```

### Screen Reader
- Live region for new comments
- Status announcements for actions
- Progress indicators for loading

### Focus Management
- Visible focus ring (2px blue)
- Focus trap in modals
- Return focus after modal close

## Animation & Transitions

### Micro-interactions
```css
/* Hover effects */
.button:hover {
  transform: translateY(-1px);
  transition: transform 150ms ease;
}

/* Loading */
.spinner {
  animation: spin 1s linear infinite;
}

/* Toast notifications */
.toast-enter {
  animation: slideIn 200ms ease-out;
}
```

### Page Transitions
- Fade in: 200ms
- Slide up: 300ms cubic-bezier
- Skeleton → Content: Crossfade 150ms

## Error States

### Network Error
```
┌────────────────────────────────────┐
│  ⚠️ Failed to load task            │
│  Please check your connection       │
│  [Retry] [Go Back]                 │
└────────────────────────────────────┘
```

**Retry Behavior**:
- Exponential backoff (1s, 2s, 4s...)
- Maximum 3 attempts
- Fallback to cached data if available

### Validation Errors
```
┌────────────────────────────────────┐
│  ❌ Title is required              │
│  Please enter a task title         │
└────────────────────────────────────┘
```

**Error Display**:
- Inline with field
- Red border
- Icon indicator
- Clear error message

## Component Library Structure

### Base Components
```
components/
├── primitives/
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Select.tsx
│   ├── Checkbox.tsx
│   └── Avatar.tsx
├── layout/
│   ├── Container.tsx
│   ├── Grid.tsx
│   ├── Card.tsx
│   └── Modal.tsx
└── composites/
    ├── Form/
    ├── Table/
    ├── Dropdown/
    └── Tabs/
```

### Task-Specific Components
```
features/task/
├── components/
│   ├── TaskHeader/
│   ├── DescriptionEditor/
│   ├── CommentSection/
│   ├── SubtaskList/
│   └── ActivityFeed/
├── hooks/
│   ├── useTask.ts
│   ├── useComments.ts
│   └── useRealtime.ts
└── types/
    └── task.ts
```

## Data Flow

### Prop Drilling vs Context
- **Props**: Direct parent-child communication
- **Context**: Global state (user, theme, real-time connection)
- **Redux/Zustand**: Complex state (editing, errors, presence)

### State Management
```
TaskDetailPage
├── task (from API)
├── isEditing (local)
├── comments (from real-time)
├── presence (from WebSocket)
└── formErrors (local)
```

## Performance Considerations

### Rendering
- Virtualize long comment lists
- Debounce input fields
- Memoize components with React.memo
- Lazy load images/avatars

### Loading States
- Skeleton screens for initial load
- Optimistic updates for user actions
- Smart caching (React Query)
- Progressive enhancement

## Testing Requirements

### Component Tests
- Render with different props
- Simulate user interactions
- Test accessibility attributes
- Verify error states

### Integration Tests
- Form submission flows
- Real-time updates
- Error handling
- Responsive behavior

## Implementation Checklist
- [ ] All components have TypeScript interfaces
- [ ] Responsive design verified at all breakpoints
- [ ] Accessibility attributes implemented
- [ ] Error states handled for each component
- [ ] Loading states for async operations
- [ ] Keyboard navigation tested
- [ ] Animations work across browsers
- [ ] Design tokens applied consistently
- [ ] Real-time updates working properly
- [ ] Performance optimized

## Best Practices
1. **Component Atomicity**: Build from small, reusable primitives
2. **State Colocation**: Keep state as close to usage as possible
3. **Progressive Enhancement**: Core functionality works without JS
4. **Performance First**: Optimize for perceived performance
5. **Accessibility by Default**: Include ARIA from the start
6. **Consistent Design Language**: Use design tokens consistently
7. **Testability**: Design components for easy testing
8. **Documentation**: Comment complex interactions

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing component library, design system, accessibility patterns |
| **Conversation** | User's specific UI requirements, design preferences, accessibility needs |
| **Skill References** | Component patterns, accessibility standards, responsive design best practices |
| **User Guidelines** | Project-specific design tokens, branding requirements, performance constraints |