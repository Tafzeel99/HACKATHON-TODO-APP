"use client";

import { useChatKit, ChatKit } from "@openai/chatkit-react";
import { getToken } from "@/lib/auth";

// ChatKit API URL - points to Phase 3 backend
const CHATKIT_API_URL = process.env.NEXT_PUBLIC_CHAT_API_URL || "http://localhost:8001";
// Domain key from OpenAI platform (required for ChatKit)
const CHATKIT_DOMAIN_KEY = process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY || "";

/**
 * TodoX ChatKit Component
 *
 * Integrates OpenAI ChatKit with our self-hosted Phase 3 backend.
 * Uses the backend's /chatkit endpoint for processing messages.
 *
 * Required env variables:
 * - NEXT_PUBLIC_CHAT_API_URL: Phase 3 backend URL
 * - NEXT_PUBLIC_OPENAI_DOMAIN_KEY: Domain key from OpenAI platform
 */
export function TodoChatKit() {
  const token = getToken();
  const hasDomainKey = Boolean(CHATKIT_DOMAIN_KEY);

  // Initialize ChatKit with our backend configuration
  // Note: Hook is always called to satisfy React rules, but only used when domainKey exists
  const { control } = useChatKit({
    api: {
      url: `${CHATKIT_API_URL}/chatkit`,
      domainKey: CHATKIT_DOMAIN_KEY || "placeholder",
      // Custom fetch to add authorization header
      fetch: async (input: RequestInfo | URL, init?: RequestInit) => {
        return fetch(input, {
          ...init,
          headers: {
            ...init?.headers,
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        });
      },
    },
    // Theme configuration
    theme: {
      colorScheme: "light",
      radius: "round",
    },
    // Start screen configuration
    startScreen: {
      greeting: "What can I help you with today?",
      prompts: [
        { label: "Add a new task", prompt: "Add a task to buy groceries", icon: "plus" },
        { label: "Show my tasks", prompt: "Show me all my tasks", icon: "notebook" },
        { label: "What's pending?", prompt: "What tasks are pending?", icon: "clock" },
      ],
    },
    // Composer configuration
    composer: {
      placeholder: "Ask me to manage your tasks...",
    },
    // Header configuration
    header: {
      enabled: true,
      title: {
        enabled: true,
        text: "TodoX Agent",
      },
    },
  });

  // Show configuration instructions if domain key is missing
  if (!hasDomainKey) {
    return (
      <div className="h-full w-full flex flex-col items-center justify-center p-8">
        <div className="text-center space-y-4 max-w-md">
          <div className="text-4xl">⚙️</div>
          <h3 className="text-lg font-semibold">ChatKit Configuration Required</h3>
          <p className="text-sm text-muted-foreground">
            To use OpenAI ChatKit, you need to configure your domain key.
          </p>
          <div className="text-left bg-muted p-4 rounded-lg text-xs space-y-2">
            <p><strong>Steps:</strong></p>
            <ol className="list-decimal list-inside space-y-1">
              <li>Go to <code>platform.openai.com/settings</code></li>
              <li>Navigate to Security → Domain Allowlist</li>
              <li>Add your domain (e.g., localhost:3000)</li>
              <li>Copy the domain key</li>
              <li>Add to <code>.env.local</code>:</li>
            </ol>
            <code className="block bg-background p-2 rounded mt-2">
              NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-key-here
            </code>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full flex flex-col">
      {/* ChatKit container */}
      <div className="flex-1 min-h-0 rounded-lg border bg-card overflow-hidden">
        <ChatKit
          control={control}
          style={{
            width: "100%",
            height: "100%",
            minHeight: "500px",
          }}
        />
      </div>
    </div>
  );
}
