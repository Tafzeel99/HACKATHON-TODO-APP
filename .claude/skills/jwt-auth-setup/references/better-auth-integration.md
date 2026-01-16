# Better Auth Integration Guide

This guide covers the integration between Better Auth (frontend) and FastAPI (backend) for JWT-based authentication.

## How Better Auth JWT Works

Better Auth can be configured to issue JWT tokens when users log in. These tokens are self-contained credentials that include user information and can be verified by any service that knows the secret key.

### Frontend Configuration

In your Next.js frontend with Better Auth:

```javascript
// In your Better Auth configuration
import { betterAuth } from "better-auth";

export const auth = betterAuth({
  // Enable JWT plugin to issue tokens
  jwt: {
    secret: process.env.BETTER_AUTH_SECRET,
    expiresIn: "7d", // Token expiry time
  },
  // Other configuration...
});
```

### Backend Verification

The FastAPI backend verifies JWT tokens issued by Better Auth using the same secret key.

## Shared Secret Configuration

Both frontend (Better Auth) and backend (FastAPI) must use the same secret key for JWT signing and verification:

```env
# Environment variables
BETTER_AUTH_SECRET=your-super-secret-key-at-least-32-characters-long
```

## Security Benefits

| Benefit | Description |
|---------|-------------|
| User Isolation | Each user only sees their own tasks |
| Stateless Auth | Backend doesn't need to call frontend to verify users |
| Token Expiry | JWTs expire automatically (configurable) |
| Independent Verification | Frontend and backend can verify auth separately |

## Common Integration Issues

1. **Secret Mismatch**: Ensure the same BETTER_AUTH_SECRET is used in both frontend and backend
2. **Algorithm Mismatch**: Better Auth typically uses HS256 algorithm
3. **Clock Skew**: Account for slight time differences between services
4. **Token Format**: Better Auth JWTs contain user information in standard claims