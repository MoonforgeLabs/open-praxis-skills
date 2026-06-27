# Knowledge Architecture (6-Layer Model)

Source: affaan-m/ECC knowledge-ops

## Layers

| Layer | Storage | Purpose | Speed | Durability |
|-------|---------|---------|-------|------------|
| 1 | Active Execution Truth | GitHub issues, PRs, Linear tasks | Real-time | Ephemeral |
| 2 | Claude Code Memory | `~/.claude/projects/*/memory/` | Fast | Persistent |
| 3 | MCP Memory Server | Structured knowledge graph | Medium | Persistent |
| 4 | Knowledge Base Repo | Durable markdown documents | Slow | Permanent |
| 5 | External Data Store | Supabase, PostgreSQL | Medium | Permanent |
| 6 | Local Context/Archive | `context/archive/` folder | Slow | Permanent |

## Routing Rules

- Code work → Layer 1 (real repos)
- Quick-access patterns → Layer 2 (memory)
- Structured relationships → Layer 3 (graph)
- Durable documentation → Layer 4 (repo)
- Human-facing notes → Layer 6 (archive)

## Ingestion: Classify → Deduplicate → Store → Index
