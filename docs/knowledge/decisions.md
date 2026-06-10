# Key Architecture Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Backend framework | Django REST Framework | Consistent CRUD with ViewSets, browsable API |
| Frontend framework | Vanilla JS SPA | Single user, no build step, minimal deps |
| Database | SQLite (dev) | Zero config, swappable to PostgreSQL |
| AI model | Google Gemini 2.0 Flash | Fast inference, simple SDK, no GPU needed |
| Section hierarchy | Recursive FK | Arbitrary nesting without extra models |
| Editor | TipTap (ProseMirror) | Extensible, CDN-loadable, academic editing |
| PDF export | LaTeX → pdflatex | IEEE format requires LaTeX compilation |
| HTML → LaTeX | Custom converter | Domain-specific mapping for academic papers |
