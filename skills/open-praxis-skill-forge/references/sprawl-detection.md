# Sprawl Detection

Source: mattpocock/skills writing-great-skills

## Sprawl ≠ No-Op ≠ Duplication

- No-op: line doesn't change behavior → delete
- Duplication: same meaning twice → keep one
- Sprawl: too long even if all lines useful → extract or split

## Thresholds

< 200: ✅ | 200-350: ⚠️ | 350-500: 🟡 | > 500: 🔴

## Treatment: push to context pointer, split by branch, split by sequence
