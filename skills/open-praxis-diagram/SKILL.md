---
name: open-praxis-diagram
description: Create professional diagrams and visual system maps. Use for architecture diagrams, flowcharts, sequence diagrams, mind maps, timelines, state machines, data-flow diagrams, draw.io editable diagrams, Figma/FigJam-ready diagram specs, or when the user asks to “画图”, “画架构图”, “流程图”, “高大上的图”, “适配 Figma”, “适配 draw.io”, or wants to visualize a system/process/data flow.
---

# Diagram Generator

Create professional diagrams across multiple outputs:

1. **SVG**: polished dark-themed static diagrams for direct export and embedding.
2. **Figma / FigJam**: editable design specs or Figma MCP implementation plans for high-end presentation diagrams.
3. **draw.io / diagrams.net**: editable XML diagrams for technical teams and long-term maintenance.
4. **Mermaid / PlantUML**: lightweight source diagrams for docs when visual polish is secondary.

## Output Selection

Choose the output before drawing:

| User Need | Prefer | Why |
|---|---|---|
| Boss/architect presentation, polished strategy diagram | Figma / FigJam | Best visual control and editable layout |
| System architecture maintained by engineers | draw.io | Editable, portable, standard architecture tooling |
| Static image export with custom styling | SVG | Precise visual output and embeddable artifact |
| Docs-native quick diagram | Mermaid / PlantUML | Fast and easy to update in Markdown |
| Complex sequence/state/interface flow | PlantUML or draw.io | Better technical rigor than Mermaid-only visuals |

If the user explicitly asks for Figma or draw.io, follow that target. If not specified, ask only when the output medium affects the work; otherwise choose the best fit and state the choice.

## Required Design Process

1. Identify the diagram type and target tool.
2. Define the visual thesis before drawing: what the diagram must prove, not just what boxes it contains.
3. Pick a layout pattern: layered architecture, hub-and-spoke, control loop, swimlane, capability map, value chain, C4, sequence, or state machine.
4. Group components into meaningful planes or domains; avoid flat lists of boxes.
5. Draw primary flow first, then supporting dependencies, then governance/observability.
6. Keep labels concise. For Mermaid/FigJam text, do not use literal `\n`; use short labels or separate nodes.
7. Validate readability: no crossed critical arrows, no unlabeled feedback loop, no duplicated nodes, no decorative-only color changes.

## Tool-Specific References

- For Figma/FigJam deliverables, read [references/figma.md](references/figma.md).
- For draw.io / diagrams.net deliverables, read [references/drawio.md](references/drawio.md).

## SVG Design System

Use SVG when the user needs a polished static artifact or when Figma/draw.io are not available.

### Palette

| Category | Fill | Stroke | Use |
|---|---|---|---|
| Primary | `rgba(8,51,68,0.4)` | `#22d3ee` | User-facing inputs |
| Secondary | `rgba(6,78,59,0.4)` | `#34d399` | Services and processing |
| Tertiary | `rgba(76,29,149,0.4)` | `#a78bfa` | Data and persistence |
| Accent | `rgba(120,53,15,0.3)` | `#fbbf24` | Infrastructure and execution |
| Alert | `rgba(136,19,55,0.4)` | `#fb7185` | Errors and risks |
| Connector | `rgba(251,146,60,0.3)` | `#fb923c` | Buses and middleware |
| Neutral | `rgba(30,41,59,0.5)` | `#94a3b8` | External or generic systems |
| Highlight | `rgba(59,130,246,0.3)` | `#60a5fa` | Core focus or active step |

### SVG Rules

- Output a single self-contained `.svg` file.
- Use `viewBox`; do not set fixed width/height.
- Include `xmlns="http://www.w3.org/2000/svg"`.
- Use `font-family: 'JetBrains Mono', 'Noto Sans SC', 'PingFang SC', sans-serif` for Chinese support.
- Draw in this order: background, region boundaries, connections, masks, component boxes, text, legend, title.
- Use orthogonal connectors when possible.
- Save to `./diagram/{topic-slug}/` unless the user provides another path.

## Quality Bar

A good diagram should add structure, not merely recolor a flowchart. Prefer:

- Named planes such as experience, semantic, runtime, execution, asset, governance.
- Explicit control loops and feedback loops.
- Clear ownership boundaries.
- Separate “what business sees” from “what runtime does”.
- Separate static assets from runtime state.
- Separate happy path from blocker/exception path.
- A small legend or visual thesis when the diagram is complex.
