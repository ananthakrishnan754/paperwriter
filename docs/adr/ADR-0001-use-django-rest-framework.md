# ADR-0001: Use Django REST Framework for Backend API

## Context
PaperWriter needs a full-featured REST API to serve the frontend SPA. The API must handle document CRUD, hierarchical sections, author management, image uploads, reference management, AI text processing, and LaTeX/PDF export.

## Decision
Use Django REST Framework (DRF) with ModelViewSets and DefaultRouter.

## Consequences
(+) DRF provides consistent CRUD patterns with minimal boilerplate through ViewSets
(+) Built-in serialization, validation, authentication, and permissions
(+) Browsable API for debugging during development
(+) DefaultRouter auto-generates URL patterns for all endpoints (16 total)
(-) DRF adds complexity for simple endpoints that could use plain Django views
(-) Serializer nesting for recursive sections requires custom SerializerMethodField

## Status
Accepted
