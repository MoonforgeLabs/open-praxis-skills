# Figma / FigJam Diagram Guide

Use this reference when the user asks for Figma, FigJam, high-end presentation diagrams, commercial architecture visuals, executive diagrams, or diagrams that must be manually editable by designers/architects.

## When to Use Figma

Prefer Figma/FigJam for:

- Executive architecture maps and strategy diagrams.
- Business model, ecosystem, value-chain, and capability maps.
- Diagrams that need polished typography, spacing, color, and later manual editing.
- Multi-frame deliverables such as one overview page plus drill-down pages.

Avoid Figma as the only source for highly technical sequence/state diagrams that need version-controlled text source; pair it with Mermaid/PlantUML/draw.io if needed.

## Deliverable Modes

1. **Figma-ready spec**: produce a structured layout spec with frames, components, text, colors, and connector rules.
2. **Figma MCP creation**: when Figma tools are available and the user wants a live file, use the Figma MCP. Load the `figma-use` skill before calling `use_figma`; use `generate_diagram` only for supported Mermaid-style FigJam diagrams.
3. **Hybrid**: create a local SVG first, then import/upload it to Figma as a visual baseline while preserving an editable spec.

## Recommended Frames

For complex architecture docs, create multiple frames instead of one overloaded image:

- `01 System Overview`: business entrypoints, core platform, assets, execution loop.
- `02 Runtime Architecture`: interface, orchestration, rule engine, state manager, plan builder.
- `03 Control Flow`: control-before, control-during, control-after, feedback loop.
- `04 Integration Map`: App, AI, automation, voice, gateway interactions.
- `05 Governance`: rule package lifecycle, validation, gray release, rollback, observability.

## Visual Patterns

Use one of these patterns before drawing:

- **Three-plane architecture**: Experience plane, domain runtime plane, execution plane.
- **Four-plane architecture**: Experience, semantic, execution, asset/governance.
- **Control-loop**: intent, validate, plan, execute, callback, refresh, explain, learn.
- **Capability map**: grouped capability domains with ownership and consumers.
- **Swimlane**: business side, domain model, control gateway, device, observability.

## Figma Layout Rules

- Use 16:9 frame for presentation, e.g. `1920 x 1080`.
- Use 12-column grid for architecture maps.
- Keep 64 px outer margin and 32 px group gutters.
- Use large section titles and short node labels; move details into captions.
- Prefer cards with 1 title line and 1 short subtitle line.
- Use consistent semantic colors: entrypoints, runtime, data assets, execution, governance, risk.
- Use orthogonal connectors with labels for critical flows.
- Avoid raw Mermaid line breaks or literal `\n` in node labels.

## Figma Style Tokens

Suggested dark executive style:

- Background: `#0B1020`.
- Surface: `#111827` with 70-90% opacity.
- Grid/border: `#243044`.
- Primary cyan: `#22D3EE`.
- Runtime green: `#34D399`.
- Asset violet: `#A78BFA`.
- Execution amber: `#FBBF24`.
- Risk rose: `#FB7185`.
- Text primary: `#F8FAFC`.
- Text secondary: `#94A3B8`.

## Figma MCP Notes

When writing to Figma:

- Use `create_new_file` only if the user does not provide a file.
- Use `use_figma` for custom editable diagrams.
- Prefer creating frames, rectangles, text nodes, and connectors programmatically.
- Keep every major group named: `Experience Plane`, `Domain Runtime`, `Asset Plane`, `Execution Loop`, `Governance`.
- After creating the diagram, return the Figma URL.

## Quality Checklist

Before finalizing:

- Does the diagram communicate a point of view, not just components?
- Can a leader understand it in 30 seconds?
- Can an architect inspect boundaries and responsibilities?
- Are feedback loops visible?
- Are governance and observability explicit?
- Is there enough whitespace for presentation use?
