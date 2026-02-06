/**
 * User TypeScript types matching backend Pydantic schemas.
 */

export interface User {
  id: string;
  email: string;
  name: string | null;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  name?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
