# Design Gate & Plan Contracts

Source: obra/superpowers brainstorming + writing-plans + executing-plans

## Brainstorming Gate (Hard Gate)

No implementation before design approved: explore intent → propose approaches → write spec → self-check → user review → handoff to writing-plans

## Plan Contracts

Each task documents: Consumes (from prior task) + Produces (for next task) with exact types. No placeholders (TBD/TODO = failure).

## Subagent Dispatch

- Model selection by role (cheap/standard/powerful)
- File handoffs (not text paste) to avoid context pollution
- Durable progress ledger (conversation memory lost on compaction)
