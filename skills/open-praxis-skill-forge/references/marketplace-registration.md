# Marketplace Registration

Source: anthropics/skills skill-creator

## marketplace.json Structure

```json
{
  "name": "praxis-skills",
  "owner": { "name": "Alex" },
  "plugins": [{
    "name": "praxis-skills",
    "source": "./",
    "strict": false,
    "skills": ["./skills/praxis-translate", "./skills/praxis-diagram"]
  }]
}
```

- `strict: false` → expose all skills in source dir
- `strict: true` → only expose listed skills

## Install: `/plugin marketplace add owner/repo` + `/plugin install name@marketplace`
