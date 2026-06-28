# 知识运维详解

## 间隔重复（Spaced Repetition）

学完一个知识点后，自动安排复习计划（FSRS-6 算法）：

```
学完 → 第 1 天 → 第 3 天 → 第 7 天 → 第 14 天 → 第 30 天 → 第 90 天
```

```bash
# 查看今日复习任务
python3 scripts/knowledge_ops.py review

# 标记复习完成（自动安排下次）
python3 scripts/knowledge_ops.py review --do
```

## 知识 Lint

定期检查知识库质量：

```bash
# 检查
python3 scripts/knowledge_ops.py lint

# 自动修复
python3 scripts/knowledge_ops.py lint --fix
```

检查项：
- 🔴 重复条目（同 URL 不同时间入库）
- 🟡 过期条目（inbox 超过 30 天未处理）
- 🟡 不完整条目（learned 但没学习笔记）
- 🔵 孤儿条目（learned 超过 14 天但没 applied）
- 🟡 未分类条目（没有 area）

## 内容质量分级

```bash
python3 scripts/knowledge_ops.py grade
```

| 等级 | 来源 | 优先级 |
|------|------|--------|
| A | 官方文档、学术论文 | 最高 |
| B | 高星 GitHub、知名博客 | 高 |
| C | 社区内容（Reddit、推特） | 中 |
| D | 其他 | 低 |

## Dedup 检查

```bash
python3 scripts/knowledge_ops.py dedup
```

检查重复条目（同 URL 或同标题）。

## 学习进度

```bash
python3 scripts/knowledge_ops.py progress
```

按 area 显示学习完成度。

## Inbox 分拣

```bash
python3 scripts/knowledge_ops.py triage
```

显示 inbox 中待分拣的条目。
