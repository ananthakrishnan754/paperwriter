# ADR-0006: JWT Authentication with simplejwt

## Context
PaperWriter needs user authentication to isolate documents between users. Without this, any user can read/edit any document. The frontend is a vanilla SPA, so session-based auth (cookies) is more complex to set up than token-based auth.

## Decision
Use `djangorestframework-simplejwt` for JWT authentication with:
- Access tokens expiring in 1 hour
- Refresh tokens expiring in 7 days
- Token rotation on refresh (old tokens invalidated)
- Bearer token header for API requests

## Consequences
(+) Stateless authentication — no server-side session storage needed
(+) Works naturally with SPA frontend (store token in localStorage/memory)
(+) Token rotation improves security (old refresh tokens invalidated)
(-) Tokens cannot be revoked server-side (until refresh)
(-) Frontend must handle token storage securely (avoid XSS)
(-) Requires token refresh logic in the frontend

## Status
Accepted
