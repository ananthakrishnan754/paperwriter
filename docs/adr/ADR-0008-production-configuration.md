# ADR-0008: Production Configuration with Environment Variables

## Context
The application needs different configurations for development and production. Hardcoded settings (SECRET_KEY, DEBUG, ALLOWED_HOSTS) are security risks in production.

## Decision
Move all configuration to environment variables:
- `DJANGO_SECRET_KEY` — required in production
- `DJANGO_DEBUG` — false in production
- `DJANGO_ALLOWED_HOSTS` — comma-separated list
- `CORS_ALLOWED_ORIGINS` — comma-separated list
- `GEMINI_API_KEY` — AI API key
- `DJANGO_LOG_LEVEL` — logging level

Use WhiteNoise for static file serving (no nginx needed for simple deploys).
Use gunicorn for production WSGI serving.
Security headers enabled only when DEBUG=False.

## Consequences
(+) Single settings file with environment-driven behavior
(+) No secrets in the codebase
(+) WhiteNoise eliminates need for separate static file server
(-) Must manage environment variables in deployment
(-) Static file serving through Python is slower than nginx
(-) WhiteNoise needs `STATIC_ROOT` and `collectstatic` run during deploy

## Status
Accepted
