# ADR-0002: Vanilla JavaScript SPA over Framework

## Context
The frontend needs a rich WYSIWYG editing experience with TipTap editor, LaTeX preview, image management, and AI command modal. The app has a single user at a time — no complex state management required.

## Decision
Use vanilla JavaScript SPA with TipTap loaded from CDN. No build step.

## Consequences
(+) Zero build tooling — no webpack, vite, or bundler needed
(+) Minimal dependencies — only TipTap, its extensions, and latex.js from CDN
(+) Fast iteration — edit HTML/JS and refresh
(-) No type safety — all state managed through DOM events and fetch calls
(-) Manual state management — no React/Vue reactivity
(-) Harder to test — no component isolation without a test framework

## Status
Accepted
