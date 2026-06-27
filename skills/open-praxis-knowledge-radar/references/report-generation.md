# 报告生成详解

## 生成报告

```bash
# 生成 HTML 报告（带样式）
python3 scripts/generate_report_v2.py --format html --open

# 生成 Markdown 报告
python3 scripts/generate_report_v2.py --format md

# 指定输出文件
python3 scripts/generate_report_v2.py --format html --output report.html

# 简洁模式
python3 scripts/generate_report_v2.py --simple
```

## 报告内容

### 统计概览

- 总任务数
- 状态分布（inbox/next/active/learning/learned/applied/waiting/done/archived）
- 领域分布（code-understanding/ai-os/skill-creation 等）
- 优先级分布（P0/P1/P2/P3）
- 来源分布（manual/dingtalk/url 等）

### 最近入库的 URL

表格形式展示：
- 领域
- 标题（带链接）
- 摘要
- 来源
- 时间

### 任务列表

按状态分组展示：
- 状态 emoji
- 优先级
- 领域
- 标题
- 摘要
- 来源
- 时间

### 待学习队列

按优先级排序的待学习任务列表。

## 报告位置

报告保存在：`~/.praxis-skills/data/knowledge-radar/reports/`

- HTML 报告：`report-*.html`
- Markdown 报告：`report-*.md`

## 存储清理

```bash
# 干运行（查看会清理什么）
bash scripts/cleanup.sh --dry-run

# 实际清理
bash scripts/cleanup.sh
```

### 清理策略

| 项目 | 策略 | 说明 |
|------|------|------|
| 报告文件 | 保留 7 天 | 超过 7 天自动删除 |
| 日志文件 | 保留 30 天 | 超过 30 天自动删除 |
| 报告目录 | 最大 10MB | 超过时删除最旧的报告 |
| 日志目录 | 最大 5MB | 超过时删除最旧的日志 |

## 自动清理

自动捕获脚本中已配置自动清理：
- 每次运行时清理超过 7 天的报告
- 每次运行时清理超过 30 天的日志
- 限制报告目录大小（最大 10MB）
- 限制日志目录大小（最大 5MB）
