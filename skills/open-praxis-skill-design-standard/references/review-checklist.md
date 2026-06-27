# Skill Review Checklist

## Frontmatter

- [ ] `name` is stable, lowercase, and unique.
- [ ] `description` includes clear triggers if model-invoked.
- [ ] User-invoked skills avoid broad auto-trigger wording.

## Scope

- [ ] One recurring job.
- [ ] No unrelated modes hidden in one file.
- [ ] Dependencies are explicit.
- [ ] Private paths and secrets are absent or intentionally scoped.

## Progressive Disclosure

- [ ] `SKILL.md` can be read quickly.
- [ ] Long references are under `references/`.
- [ ] Examples support behavior rather than duplicating instructions.

## Safety

- [ ] External writes require approval.
- [ ] Secrets are never requested or printed.
- [ ] Legal, financial, medical, security, and destructive operations include boundaries.

## Verification

- [ ] Completion artifact is named.
- [ ] Validation command exists when possible.
- [ ] README/taxonomy/marketplace updates are listed when adding a new skill.
