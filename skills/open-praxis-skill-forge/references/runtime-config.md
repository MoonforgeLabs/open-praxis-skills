# Runtime Configuration Pattern

Source: anysearch-skill

## Problem

Platform detection (Python vs Node vs Bash) is slow and repeated on every skill activation. Wasting tool calls on `python --version`, `node --version`, etc.

## Solution: runtime.conf

Detect the runtime ONCE during installation, persist to a config file, read directly on subsequent uses.

### runtime.conf Format

```
Runtime: Python
Command: python3 <skill_dir>/scripts/my_cli.py
```

### Detection Priority

```
Python  >  Node.js  >  Shell (PowerShell on Windows, Bash on Linux/macOS)
```

### Detection Procedure

1. Check `python --version` and `python3 --version` — use whichever works (version ≥ 3.6)
2. If Python fails, check `node --version` (version ≥ 12)
3. If Node fails, check shell: PowerShell 5.1+ on Windows, bash 3.2+ with jq/curl on Linux/macOS

### Usage Flow

```
First use:
  Detect runtime → Write runtime.conf → Execute command

Subsequent uses:
  Read runtime.conf → Execute command directly (skip detection)
```

### Fallback

If runtime.conf is missing or the stored command fails, fall back to full detection procedure.

## Multi-Platform CLI Pattern (anysearch)

Provide the same CLI in multiple runtimes from a single source of truth:

```
scripts/
├── anysearch_cli.py      # Python CLI
├── anysearch_cli.js      # Node.js CLI
├── anysearch_cli.sh      # Bash CLI
├── anysearch_cli.ps1     # PowerShell CLI
├── generate.py           # Generates shared blocks from single source
└── shared/
    ├── constants.json    # Shared config (domains, endpoints)
    └── doc_spec.md       # Shared documentation
```

### generate.py Pattern

One script reads `shared/` and generates the common code blocks in all 4 CLIs. This ensures consistency — change once, propagate everywhere.

## Offline Help: doc Command

Each CLI includes a `doc` command that prints the full interface spec offline:

```bash
python3 <skill_dir>/scripts/my_cli.py doc
```

Rules:
- `doc` is local-only, makes no network requests
- Use `doc` only when the CLI interface is unknown or a command fails
- For routine calls, use the stored command from runtime.conf directly
- Don't run `doc` on every activation — wastes tool calls and tokens
