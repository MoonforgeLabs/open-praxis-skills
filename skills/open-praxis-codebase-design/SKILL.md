---
name: open-praxis-codebase-design
description: Design or improve code modules around deep modules, small interfaces, clean seams, testability, and AI-navigable architecture. Use for API design, refactors, module boundaries, and architecture review.
---

# Alex Codebase Design

Design deep modules: a lot of behavior behind a small stable interface.

## Review Questions

- What is the public interface?
- What complexity can move behind that interface?
- Where is the clean seam?
- How will callers test behavior without depending on internals?
- What vocabulary should become domain language?
- What should be documented as an ADR or design note?

## Output

- Proposed interface.
- Module boundary.
- Alternatives considered.
- Test strategy.
- Migration plan.

Inspired by `mattpocock/skills` `codebase-design` under MIT License.
