# ADR-0007: Object-Level Permissions with Document Ownership

## Context
With user authentication in place, API resources (sections, authors, images, references) must be scoped to the user's documents. Without this, a user could access another user's sections by guessing IDs.

## Decision
- Document model has an `owner` ForeignKey to `auth.User`
- All DocumentViewSet queries filter by `owner=request.user`
- Section/Author/Image/Reference viewsets filter through the user's document IDs
- `IsOwnerOrReadOnly` permission class for Document-level access
- Export endpoints check `owner=request.user` before returning data

## Consequences
(+) Complete data isolation between users
(+) No SQL injection or ID-guessing vulnerabilities for cross-user access
(+) Consistent pattern across all viewsets
(-) All existing data must be migrated to have an owner
(-) Slightly more complex queries (subquery through document IDs)
(-) Admin user management requires Django admin or custom tools

## Status
Accepted
