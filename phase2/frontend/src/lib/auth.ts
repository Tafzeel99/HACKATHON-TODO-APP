"use client";

import type { TokenResponse, User, UserCreate, UserLogin } from "@/types/user";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const TOKEN_KEY = "todo_auth_token";

/**
 * Get the stored authentication token.
 */
export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

/**
 * Store the authentication token.
 */
export function setToken(token: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(TOKEN_KEY, token);
}

/**
 * Remove the authentication token.
 */
export function removeToken(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(TOKEN_KEY);
}

/**
 * Check if user is authenticated.
 */
export function isAuthenticated(): boolean {
  return !!getToken();
}

/**
 * Sign up a new user.
 */
export async function signup(data: UserCreate): Promise<User> {
  const response = await fetch(`${API_URL}/api/auth/signup`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to sign up");
  }

  return response.json();
}

/**
 * Sign in an existing user.
 */
export async function signin(data: UserLogin): Promise<TokenResponse> {
  const response = await fetch(`${API_URL}/api/auth/signin`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Invalid email or password");
  }

  const tokenData: TokenResponse = await response.json();
  setToken(tokenData.access_token);
  return tokenData;
}

/**
 * Sign out the current user.
 */
export async function signout(): Promise<void> {
  const token = getToken();

  if (token) {
    try {
      await fetch(`${API_URL}/api/auth/signout`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
    } catch {
      // Ignore signout errors, just remove token
    }
  }

  removeToken();
}
