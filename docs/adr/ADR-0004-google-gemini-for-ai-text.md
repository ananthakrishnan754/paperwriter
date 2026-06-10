# ADR-0004: Google Gemini 2.0 Flash for AI Text Transformation

## Context
The application needs AI-powered text transformation (rewrite, shorten, expand) for academic writing assistance. The model must be fast, accessible via API, and produce high-quality academic text.

## Decision
Use Google Gemini 2.0 Flash via the `google-generativeai` Python SDK.

## Consequences
(+) Fast inference suitable for real-time editing assistance
(+) Simple Python SDK with straightforward API
(+) No self-hosting or GPU infrastructure needed
(+) Pay-per-use pricing — cost-effective for low-volume usage
(-) Requires internet connection and API key
(-) Output quality depends on prompt engineering
(-) Vendor lock-in — switching to another model requires prompt redesign
(-) Free tier has rate limits

## Status
Accepted
