# Code Patterns

## API Design
- All endpoints registered via DRF `DefaultRouter`
- CRUD endpoints use `ModelViewSet` for consistency
- Custom actions use `@action(detail=True, methods=['post'])`
- Non-CRUD endpoints use `@api_view(['GET', 'POST'])`

## Serialization
- Recursive sections use `SerializerMethodField` with nested `SectionSerializer`
- Image URLs are built with `request.build_absolute_uri()` in serializer context
- Document serializer nests sections (top-level only), authors, images, references

## LaTeX Generation
- 172-line converter: maps section depth to `\section{}` / `\subsection{}` / `\subsubsection{}`
- HTML tags converted with regex: `<strong>` → `\textbf{}`, `<em>` → `\textit{}`
- Figures emitted after section content with `\begin{figure}[htbp]`
- 3-pass compilation: pdflatex → bibtex → pdflatex → pdflatex
- IEEEtran.cls copied from `ieee_format/` directory

## AI Integration
- Prompt includes: document title, section title, selected text, user command
- Output contract: model returns ONLY modified text, no explanations
- Error handling: catch-all exception returns 500 with error message

## Frontend State
- State managed through DOM events and `fetch()`-based API calls
- One TipTap editor instance per section
- Sections stored as array, rendered into sidebar nav
- Save status indicator ("Saved" / "Unsaved changes")

## Testing
- Use pytest with `--reuse-db` for faster test runs
- Use `model-bakery` for model instance factories
- Aim for 90%+ coverage on new code
