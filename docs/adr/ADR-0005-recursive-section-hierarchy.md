# ADR-0005: Recursive Foreign Key for Section Hierarchy

## Context
Academic papers have hierarchical section structures (section → subsection → subsubsection). The data model must support arbitrary nesting depth without schema changes.

## Decision
Use a recursive foreign key on the Section model: `parent = ForeignKey('self', null=True, blank=True)`.

## Consequences
(+) Supports arbitrary nesting depth without a separate subsection model
(+) Simple query pattern: filter by `parent=None` for top-level sections
(+) Easy reordering within sibling groups
(-) Recursive serialization requires custom SerializerMethodField
(-) Deep nesting (3+ levels) becomes harder to query efficiently
(-) No built-in validation for max depth in the model layer

## Status
Accepted
