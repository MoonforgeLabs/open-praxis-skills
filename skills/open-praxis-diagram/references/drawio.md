# draw.io / diagrams.net Diagram Guide

Use this reference when the user asks for draw.io, diagrams.net, `.drawio`, editable technical architecture diagrams, or diagrams that engineers need to maintain outside Figma.

## When to Use draw.io

Prefer draw.io for:

- Editable system architecture diagrams for engineering teams.
- Network, deployment, integration, and control-flow diagrams.
- Diagrams that must be versioned as XML in a repository.
- Architecture docs that need both image export and editable source.

Avoid draw.io for high-end marketing visuals where Figma is better.

## Output Format

Create a `.drawio` file containing mxfile XML. When useful, also export or generate an `.svg` preview.

Recommended save paths:

- `./diagram/{topic-slug}/{name}.drawio`
- `./diagram/{topic-slug}/{name}.svg`

## Layout Patterns

Use one of these patterns:

- **Layered architecture**: users, APIs, runtime services, data assets, execution systems, observability.
- **Swimlane process**: business, domain service, control gateway, device, callback, monitoring.
- **C4 context/container/component**: use this for formal software architecture.
- **Capability map**: grouped modules with dependencies and consumers.
- **Lifecycle**: rule package create, validate, publish, gray, observe, rollback.

## draw.io Styling Rules

- Use rounded rectangles for components.
- Use containers for domains/layers.
- Use orthogonal connectors, not diagonal spaghetti.
- Label important connectors with verbs: `validate`, `resolve`, `evaluate`, `generate plan`, `callback`, `refresh`.
- Use line jumps only if unavoidable.
- Use color semantically, not decoratively.
- Use short labels; put details in notes or separate drill-down diagrams.

Suggested colors:

| Domain | Fill | Stroke |
|---|---|---|
| Business entry | `#E0F2FE` | `#0284C7` |
| Runtime service | `#DCFCE7` | `#16A34A` |
| Core engine | `#DBEAFE` | `#2563EB` |
| Data asset | `#F3E8FF` | `#7C3AED` |
| Execution | `#FEF3C7` | `#D97706` |
| Risk/failure | `#FFE4E6` | `#E11D48` |
| Governance | `#E2E8F0` | `#64748B` |

## XML Generation Guidance

If generating draw.io XML directly:

- Root should be `<mxfile>` with one or more `<diagram>` pages.
- Use `mxGraphModel > root` with cells.
- Include cells `0` and `1` as root graph cells.
- Use `vertex="1" parent="1"` for nodes.
- Use `edge="1" parent="1" source="..." target="..."` for connectors.
- Put geometry in `mxGeometry`.
- Prefer stable deterministic ids such as `node-domain-runtime` and `edge-api-rule`.

Minimal node style:

```xml
style="rounded=1;whiteSpace=wrap;html=1;fillColor=#DBEAFE;strokeColor=#2563EB;fontColor=#0F172A;arcSize=12;"
```

Minimal edge style:

```xml
style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;strokeColor=#64748B;"
```

## Export Options

If diagrams.net CLI or desktop is available, export with:

```bash
draw.io --export --format svg --output output.svg input.drawio
```

If unavailable, still provide the `.drawio` XML source and tell the user it can be opened at diagrams.net.

## Quality Checklist

Before finalizing:

- Is the `.drawio` file editable and not just an embedded image?
- Are architecture boundaries represented as containers?
- Are primary and feedback flows distinguishable?
- Are execution path and governance path separated?
- Are labels short enough to read at 100% zoom?
- Can the diagram be maintained in git as source?
