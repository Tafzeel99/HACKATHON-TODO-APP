---
name: responsive-layout-designer
description: |
  Creates mobile-first responsive layouts using Tailwind CSS. Designs adaptive grid systems,
  flexible containers, and breakpoint-specific styling for optimal viewing across all devices
  (mobile, tablet, desktop). Implements modern layout patterns with proper spacing and alignment.
---

# Responsive Layout Designer

Creates mobile-first responsive layouts with Tailwind CSS.

## What This Skill Does
- Designs mobile-first layouts (320px → 1920px)
- Creates responsive grid systems (CSS Grid, Flexbox)
- Implements Tailwind breakpoints (sm, md, lg, xl, 2xl)
- Builds adaptive navigation patterns
- Creates flexible containers and spacing
- Implements responsive typography
- Designs card grids that adapt to screen size
- Handles responsive images and media

## What This Skill Does NOT Do
- Create animations (use animation-composer)
- Build specific components (use shadcn-component-builder)
- Handle form logic (use form-wizard)
- Write API calls (use api-client-generator)

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | Existing layouts, Tailwind config, current breakpoint usage |
| **Conversation** | Layout requirements, supported devices, content hierarchy |
| **Skill References** | Tailwind responsive utilities, modern layout patterns |
| **User Guidelines** | Design mockups, brand spacing guidelines |

## Required Clarifications

Ask about USER'S requirements:

1. **Layout Type**: "What layout do you need (dashboard, list view, grid, sidebar)?"
2. **Breakpoints**: "Which devices are primary (mobile, tablet, desktop)?"
3. **Content Density**: "How should content adapt (stack, side-by-side, hide)?"

## Tailwind Breakpoints
```css
/* Default Tailwind breakpoints */
sm: 640px   /* Small tablets, large phones */
md: 768px   /* Tablets */
lg: 1024px  /* Laptops, desktops */
xl: 1280px  /* Large desktops */
2xl: 1536px /* Extra large screens */
```

**Mobile-First Approach:**
```tsx
// Styles apply mobile-first, then override at larger breakpoints
<div className="w-full md:w-1/2 lg:w-1/3">
  {/*
    Mobile (default): full width (w-full)
    Tablet (md): half width (md:w-1/2)
    Desktop (lg): one-third width (lg:w-1/3)
  */}
</div>
```

## Layout Patterns

### 1. Container Pattern
```tsx
// components/container.tsx
import { cn } from "@/lib/utils"

interface ContainerProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode
}

export function Container({ children, className, ...props }: ContainerProps) {
  return (
    <div
      className={cn(
        "mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8",
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}
```

**Usage:**
```tsx
<Container>
  <h1>Page content within centered container</h1>
</Container>
```

### 2. Responsive Grid Layout
```tsx
// Task list grid - 1 column on mobile, 2 on tablet, 3 on desktop
<div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
  {tasks.map((task) => (
    <TaskCard key={task.id} task={task} />
  ))}
</div>

// Auto-fit grid (automatically adjusts columns based on min-width)
<div className="grid grid-cols-[repeat(auto-fit,minmax(300px,1fr))] gap-4">
  {items.map((item) => (
    <ItemCard key={item.id} item={item} />
  ))}
</div>
```

### 3. Sidebar Layout (Two-Column)
```tsx
// app/dashboard/layout.tsx
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar - hidden on mobile, visible on desktop */}
      <aside className="hidden w-64 border-r bg-gray-50 lg:block">
        <div className="sticky top-0 p-4">
          <nav>
            {/* Navigation items */}
          </nav>
        </div>
      </aside>

      {/* Main content */}
      <main className="flex-1">
        <div className="mx-auto max-w-7xl p-4 sm:p-6 lg:p-8">
          {children}
        </div>
      </main>
    </div>
  )
}
```

### 4. Mobile Navigation (Hamburger Menu)
```tsx
"use client"

import { useState } from "react"
import { Menu, X } from "lucide-react"
import { Button } from "@/components/ui/button"

export function MobileNav() {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {/* Mobile menu button */}
      <div className="lg:hidden">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsOpen(!isOpen)}
        >
          {isOpen ? <X /> : <Menu />}
        </Button>
      </div>

      {/* Mobile menu overlay */}
      {isOpen && (
        <div className="fixed inset-0 z-50 bg-background lg:hidden">
          <div className="container flex h-full flex-col py-6">
            <div className="flex items-center justify-between">
              <span className="text-lg font-bold">Menu</span>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsOpen(false)}
              >
                <X />
              </Button>
            </div>
            <nav className="mt-8 flex flex-col space-y-4">
              {/* Navigation links */}
            </nav>
          </div>
        </div>
      )}

      {/* Desktop navigation - always visible */}
      <nav className="hidden lg:flex lg:gap-6">
        {/* Desktop nav items */}
      </nav>
    </>
  )
}
```

### 5. Responsive Card Grid
```tsx
// components/task-grid.tsx
interface TaskGridProps {
  tasks: Task[]
}

export function TaskGrid({ tasks }: TaskGridProps) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
      {tasks.map((task) => (
        <Card key={task.id} className="flex flex-col">
          <CardHeader>
            <CardTitle className="line-clamp-2 text-base">
              {task.title}
            </CardTitle>
          </CardHeader>
          <CardContent className="flex-1">
            <p className="line-clamp-3 text-sm text-muted-foreground">
              {task.description}
            </p>
          </CardContent>
          <CardFooter>
            <Button className="w-full" size="sm">
              View Details
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  )
}
```

### 6. Responsive Header
```tsx
// components/header.tsx
export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center sm:h-16">
        {/* Logo */}
        <div className="mr-4 flex">
          <a className="flex items-center space-x-2" href="/">
            <span className="text-lg font-bold sm:text-xl">TodoApp</span>
          </a>
        </div>

        {/* Desktop Navigation */}
        <nav className="ml-auto hidden items-center space-x-6 md:flex">
          <a href="/tasks">Tasks</a>
          <a href="/projects">Projects</a>
          <a href="/settings">Settings</a>
        </nav>

        {/* Mobile Menu Button */}
        <div className="ml-auto md:hidden">
          <MobileNav />
        </div>
      </div>
    </header>
  )
}
```

### 7. Flex Layout (Horizontal/Vertical Stack)
```tsx
// Responsive flex direction
<div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
  <div>
    <h1 className="text-2xl font-bold md:text-3xl lg:text-4xl xl:text-5xl">
      Tasks
    </h1>
    <p className="text-sm text-muted-foreground md:text-base">
      Manage your todo items
    </p>
  </div>
  <Button className="w-full md:w-auto">Add Task</Button>
</div>
```

### 8. Responsive Typography
```tsx
// Headings scale with screen size
<h1 className="text-2xl font-bold sm:text-3xl lg:text-4xl xl:text-5xl">
  Welcome to TodoApp
</h1>

<p className="text-sm sm:text-base lg:text-lg">
  Responsive paragraph text
</p>

// Line clamping
<p className="line-clamp-2 sm:line-clamp-3 lg:line-clamp-none">
  This text truncates on mobile/tablet, shows full on desktop
</p>
```

### 9. Responsive Spacing
```tsx
// Padding adapts to screen size
<div className="p-4 sm:p-6 lg:p-8">
  {/* Mobile: 16px, Tablet: 24px, Desktop: 32px */}
</div>

// Gap between items
<div className="flex flex-col gap-2 sm:gap-4 lg:gap-6">
  {/* Mobile: 8px, Tablet: 16px, Desktop: 24px */}
</div>
```

### 10. Responsive Images
```tsx
import Image from "next/image"

// Responsive image with aspect ratio
<div className="relative aspect-video w-full overflow-hidden rounded-lg">
  <Image
    src="/task-image.jpg"
    alt="Task illustration"
    fill
    className="object-cover"
    sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
  />
</div>

// Responsive avatar
<Image
  src="/avatar.jpg"
  alt="User"
  width={32}
  height={32}
  className="h-8 w-8 rounded-full sm:h-10 sm:w-10 lg:h-12 lg:w-12"
/>
```

## Complete Page Layout Example
```tsx
// app/tasks/page.tsx
import { Container } from "@/components/container"
import { Header } from "@/components/header"
import { TaskGrid } from "@/components/task-grid"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Plus, Search } from "lucide-react"

export default function TasksPage() {
  return (
    <>
      <Header />

      <Container className="py-6 sm:py-8 lg:py-12">
        {/* Page Header */}
        <div className="mb-6 flex flex-col gap-4 sm:mb-8 md:flex-row md:items-center md:justify-between lg:mb-12">
          <div>
            <h1 className="text-2xl font-bold sm:text-3xl lg:text-4xl">
              My Tasks
            </h1>
            <p className="mt-1 text-sm text-muted-foreground sm:text-base">
              Manage your todo items efficiently
            </p>
          </div>
          <Button className="w-full md:w-auto">
            <Plus className="mr-2 h-4 w-4" />
            Add Task
          </Button>
        </div>

        {/* Search & Filters */}
        <div className="mb-6 flex flex-col gap-3 sm:mb-8 sm:flex-row">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="Search tasks..."
              className="pl-10"
            />
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="flex-1 sm:flex-none">
              All
            </Button>
            <Button variant="outline" className="flex-1 sm:flex-none">
              Active
            </Button>
            <Button variant="outline" className="flex-1 sm:flex-none">
              Completed
            </Button>
          </div>
        </div>

        {/* Task Grid */}
        <TaskGrid tasks={tasks} />
      </Container>
    </>
  )
}
```

## Responsive Utilities Cheat Sheet
```tsx
// Display
className="hidden sm:block"        // Hide on mobile, show on tablet+
className="block sm:hidden"        // Show on mobile, hide on tablet+

// Flexbox
className="flex-col md:flex-row"   // Stack on mobile, horizontal on desktop

// Grid Columns
className="grid-cols-1 sm:grid-cols-2 lg:grid-cols-3"

// Width
className="w-full md:w-1/2 lg:w-1/3"

// Padding
className="p-4 sm:p-6 lg:p-8"

// Gap
className="gap-2 sm:gap-4 lg:gap-6"

// Text Size
className="text-sm sm:text-base lg:text-lg"

// Max Width
className="max-w-sm md:max-w-md lg:max-w-lg xl:max-w-xl"
```

## Testing Responsive Layouts

### Browser DevTools
```
1. Open Chrome DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test breakpoints:
   - Mobile: 375px (iPhone)
   - Tablet: 768px (iPad)
   - Desktop: 1280px, 1920px
```

### Tailwind Debug Screens
```tsx
// Add to layout for development
{process.env.NODE_ENV === 'development' && (
  <div className="fixed bottom-4 right-4 z-50 rounded bg-black px-2 py-1 text-xs text-white">
    <div className="sm:hidden">XS</div>
    <div className="hidden sm:block md:hidden">SM</div>
    <div className="hidden md:block lg:hidden">MD</div>
    <div className="hidden lg:block xl:hidden">LG</div>
    <div className="hidden xl:block 2xl:hidden">XL</div>
    <div className="hidden 2xl:block">2XL</div>
  </div>
)}
```

## Output Checklist

Before delivering responsive layout:
- [ ] Mobile-first approach implemented
- [ ] All required breakpoints covered (sm, md, lg, xl)
- [ ] Container widths properly constrained
- [ ] Responsive grid system implemented
- [ ] Flexible spacing applied
- [ ] Typography scales with screen size
- [ ] Images adapt to screen dimensions
- [ ] Navigation adapts to screen size
- [ ] Content hierarchy maintained across devices
- [ ] Touch targets appropriately sized (44px minimum)
- [ ] Layout tested on multiple screen sizes