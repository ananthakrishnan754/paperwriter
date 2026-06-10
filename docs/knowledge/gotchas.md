# Known Gotchas & Footguns

## LaTeX Compilation
- `pdflatex` must be installed on the system — not a Python dependency
- Windows users need MiKTeX; Linux needs texlive-latex-*
- The 3-pass compilation can fail silently if BibTeX is missing
- Long words without hyphens can overflow PDF columns (mitigated by `\sloppy`)

## Image Uploads
- `PaperImage.image` is an `ImageField` — requires `Pillow` to be installed
- Media files served by Django in dev only — production needs a real file server
- Image paths in LaTeX export use `os.path.basename()` — filename collisions possible

## Section Ordering
- The `move` action re-indexes all siblings before moving
- Concurrent move requests can cause race conditions
- No validation prevents orphaned sections if parent is deleted

## AI Integration
- `GEMINI_API_KEY` must be set in environment or `.env` file
- Gemini 2.0 Flash has rate limits on the free tier
- Poor prompt engineering can produce non-academic output
- No fallback if API call fails

## Frontend
- TipTap loaded from CDN — app won't work offline
- No input sanitization on AI output before inserting into editor
- Section editor instances created/destroyed dynamically — memory leak if not cleaned
