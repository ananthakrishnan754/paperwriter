# ADR-0003: SQLite for Development, Swappable to PostgreSQL

## Context
The application needs persistent storage. Team is familiar with Django ORM. Data has relational structure with recursive foreign keys (Section → Section).

## Decision
Use SQLite for development. Django ORM abstracts the database, making PostgreSQL a trivial swap for production.

## Consequences
(+) Zero config database — no server process needed
(+) Same ORM code works with PostgreSQL without changes
(+) Fast test runs — no DB connection overhead
(-) No concurrent write support (not a concern for single-user app)
(-) No pgvector for potential future embedding search
(-) Limited advanced PostgreSQL features (array fields, full-text search)

## Status
Accepted
