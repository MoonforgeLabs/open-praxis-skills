#!/usr/bin/env python3
"""生成自包含的交互式 HTML 报告 - 无需服务器，支持筛选

用法:
    python3 generate_report.py                    # 生成最近 7 天报告
    python3 generate_report.py --days 30          # 生成最近 30 天报告
    python3 generate_report.py --all-time         # 生成全部历史报告
    python3 generate_report.py --open             # 生成后自动打开浏览器
"""

import json
import sys
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent))

from db import UsageDB


def parse_args() -> Dict[str, Any]:
    args = sys.argv[1:]
    config = {
        "days": 30,  # 默认加载 30 天数据，前端可筛选
        "all_time": False,
        "open": False,
        "output": None,
    }

    i = 0
    while i < len(args):
        a = args[i]
        if a == "--days" and i + 1 < len(args):
            config["days"] = int(args[i + 1])
            i += 2
        elif a == "--all-time":
            config["all_time"] = True
            i += 1
        elif a == "--open":
            config["open"] = True
            i += 1
        elif a == "--output" and i + 1 < len(args):
            config["output"] = Path(args[i + 1])
            i += 2
        elif a == "today":
            config["days"] = 1
            i += 1
        elif a == "week":
            config["days"] = 7
            i += 1
        elif a == "month":
            config["days"] = 30
            i += 1
        else:
            i += 1

    return config


def main():
    config = parse_args()

    # 查询所有数据（加载足够的数据供筛选）
    db = UsageDB()
    days = 0 if config["all_time"] else config["days"]

    # 获取完整数据
    all_events = db.query_events(days=days)

    # 获取各维度统计
    stats_all = db.query_stats(days=days)
    stats_all["health_score"] = db.get_health_score(days=days or 30)

    db.close()

    # 准备嵌入的数据
    embedded_data = {
        "generated_at": datetime.now().isoformat(),
        "period_days": days,
        "events": all_events,
        "stats": stats_all,
    }

    # 生成 HTML
    html = generate_interactive_html(embedded_data)

    # 保存文件
    if config["output"]:
        output_path = config["output"]
    else:
        output_dir = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats" / "reports"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"report_{timestamp}.html"

    output_path.write_text(html, encoding="utf-8")
    print(f"✅ 报告已生成: {output_path}")
    print(f"📊 包含 {len(all_events)} 条事件")
    print(f"💡 直接双击打开，无需服务器")

    # 自动打开浏览器
    if config["open"]:
        webbrowser.open(f"file://{output_path}")
        print("🌐 已在浏览器中打开")


def generate_interactive_html(data: Dict[str, Any]) -> str:
    """生成自包含的交互式 HTML"""
    events_json = json.dumps(data["events"], ensure_ascii=False)
    stats_json = json.dumps(data["stats"], ensure_ascii=False)
    generated_at = data["generated_at"]

    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📊 AI Usage Statistics</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 12px; margin-bottom: 20px; }}
        .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; }}
        .filters {{ background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); display: flex; gap: 15px; flex-wrap: wrap; align-items: center; }}
        .filter-group {{ display: flex; align-items: center; gap: 8px; }}
        .filter-group label {{ font-weight: 600; color: #333; font-size: 14px; }}
        select {{ padding: 10px 15px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; background: white; cursor: pointer; }}
        select:focus {{ outline: none; border-color: #667eea; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 15px; margin-bottom: 20px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: 700; color: #667eea; }}
        .stat-label {{ color: #666; font-size: 14px; margin-top: 5px; }}
        .charts-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .chart-container h3 {{ margin-bottom: 15px; color: #333; }}
        .chart-wrapper {{ position: relative; height: 250px; }}
        .table-container {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); margin-bottom: 20px; overflow-x: auto; }}
        .table-container h3 {{ margin-bottom: 15px; color: #333; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        th {{ background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; position: sticky; top: 0; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
        tr:hover {{ background: #f8f9fa; }}
        .badge {{ padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; }}
        .badge-skill {{ background: #e3f2fd; color: #1565c0; }}
        .badge-agent {{ background: #e8f5e9; color: #2e7d32; }}
        .badge-tool {{ background: #fff3e0; color: #ef6c00; }}
        .footer {{ text-align: center; padding: 20px; color: #999; font-size: 13px; }}
        @media (max-width: 768px) {{
            .charts-row {{ grid-template-columns: 1fr; }}
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .filters {{ flex-direction: column; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 AI Usage Statistics</h1>
            <p>生成时间: {generated_at} | 支持按时间段、Runtime、类型筛选</p>
        </div>

        <div class="filters">
            <div class="filter-group">
                <label>📅 时间段:</label>
                <select id="filterDays">
                    <option value="1">今天</option>
                    <option value="7">最近 7 天</option>
                    <option value="14">最近 14 天</option>
                    <option value="30" selected>最近 30 天</option>
                    <option value="0">全部时间</option>
                </select>
            </div>
            <div class="filter-group">
                <label>🖥️ Runtime:</label>
                <select id="filterRuntime">
                    <option value="all">全部 Runtime</option>
                    <option value="claude">Claude Code</option>
                    <option value="codex">Codex</option>
                </select>
            </div>
            <div class="filter-group">
                <label>🔧 类型:</label>
                <select id="filterKind">
                    <option value="all">全部类型</option>
                    <option value="skill">Skill</option>
                    <option value="agent">Agent</option>
                    <option value="tool">Tool</option>
                </select>
            </div>
        </div>

        <div class="stats-grid" id="statsGrid"></div>

        <div class="charts-row">
            <div class="chart-container">
                <h3>📈 使用趋势</h3>
                <div class="chart-wrapper"><canvas id="trendChart"></canvas></div>
            </div>
            <div class="chart-container">
                <h3>📊 类型分布</h3>
                <div class="chart-wrapper"><canvas id="kindChart"></canvas></div>
            </div>
        </div>

        <div class="charts-row">
            <div class="chart-container">
                <h3>🖥️ Runtime 分布</h3>
                <div class="chart-wrapper"><canvas id="runtimeChart"></canvas></div>
            </div>
            <div class="chart-container">
                <h3>🏆 Top 10 Skills</h3>
                <div class="chart-wrapper"><canvas id="skillsChart"></canvas></div>
            </div>
        </div>

        <div class="table-container">
            <h3>📋 事件列表 (<span id="eventCount">0</span> 条)</h3>
            <table>
                <thead>
                    <tr>
                        <th>时间</th>
                        <th>Runtime</th>
                        <th>类型</th>
                        <th>名称</th>
                        <th>Token</th>
                        <th>成本</th>
                    </tr>
                </thead>
                <tbody id="eventsBody"></tbody>
            </table>
        </div>

        <div class="section">
            <h2>💰 计费规则（每 1M tokens）</h2>
            <table style="width:100%;border-collapse:collapse;font-size:13px;">
                <tr style="background:#f5f5f5;">
                    <th style="padding:8px;text-align:left;">模型</th>
                    <th style="padding:8px;text-align:right;">Input</th>
                    <th style="padding:8px;text-align:right;">Output</th>
                    <th style="padding:8px;text-align:right;">Cache Read</th>
                    <th style="padding:8px;text-align:left;">来源</th>
                </tr>
                <tr style="border-bottom:1px solid #eee;"><td style="padding:6px;">Claude Opus 4</td><td style="padding:6px;text-align:right;">$15.00</td><td style="padding:6px;text-align:right;">$75.00</td><td style="padding:6px;text-align:right;">$1.50</td><td style="padding:6px;color:#888;">Anthropic 官价</td></tr>
                <tr style="border-bottom:1px solid #eee;"><td style="padding:6px;">Claude Sonnet 4</td><td style="padding:6px;text-align:right;">$3.00</td><td style="padding:6px;text-align:right;">$15.00</td><td style="padding:6px;text-align:right;">$0.30</td><td style="padding:6px;color:#888;">Anthropic 官价</td></tr>
                <tr style="border-bottom:1px solid #eee;"><td style="padding:6px;">Claude Haiku 4</td><td style="padding:6px;text-align:right;">$0.80</td><td style="padding:6px;text-align:right;">$4.00</td><td style="padding:6px;text-align:right;">$0.08</td><td style="padding:6px;color:#888;">Anthropic 官价</td></tr>
                <tr style="border-bottom:1px solid #eee;background:#e8f5e9;"><td style="padding:6px;">MiMo-V2.5-Pro (小米)</td><td style="padding:6px;text-align:right;">$0.435</td><td style="padding:6px;text-align:right;">$0.87</td><td style="padding:6px;text-align:right;">$0.044</td><td style="padding:6px;color:#888;">OpenRouter</td></tr>
                <tr style="border-bottom:1px solid #eee;background:#e8f5e9;"><td style="padding:6px;">MiMo-V2.5 (小米)</td><td style="padding:6px;text-align:right;">$0.105</td><td style="padding:6px;text-align:right;">$0.28</td><td style="padding:6px;text-align:right;">$0.01</td><td style="padding:6px;color:#888;">OpenRouter</td></tr>
                <tr style="border-bottom:1px solid #eee;background:#fff8e1;"><td style="padding:6px;font-weight:bold;">GPT-5.5</td><td style="padding:6px;text-align:right;font-weight:bold;">$5.00</td><td style="padding:6px;text-align:right;font-weight:bold;">$30.00</td><td style="padding:6px;text-align:right;font-weight:bold;">$0.50</td><td style="padding:6px;color:#888;">OpenAI 官价</td></tr>
                <tr style="border-bottom:1px solid #eee;"><td style="padding:6px;">GPT-5</td><td style="padding:6px;text-align:right;">$2.50</td><td style="padding:6px;text-align:right;">$15.00</td><td style="padding:6px;text-align:right;">$0.25</td><td style="padding:6px;color:#888;">OpenAI 官价</td></tr>
                <tr style="border-bottom:1px solid #eee;"><td style="padding:6px;">GPT-4o</td><td style="padding:6px;text-align:right;">$5.00</td><td style="padding:6px;text-align:right;">$15.00</td><td style="padding:6px;text-align:right;">-</td><td style="padding:6px;color:#888;">OpenAI 官价</td></tr>
                <tr style="border-bottom:1px solid #eee;"><td style="padding:6px;">GPT-4o-mini</td><td style="padding:6px;text-align:right;">$0.15</td><td style="padding:6px;text-align:right;">$0.60</td><td style="padding:6px;text-align:right;">-</td><td style="padding:6px;color:#888;">OpenAI 官价</td></tr>
            </table>
            <p style="color:#888;font-size:12px;margin-top:8px;">💡 费用 = (input_tokens × input_rate + output_tokens × output_rate + cache_read_tokens × cache_rate) ÷ 1,000,000</p>
            <p style="color:#888;font-size:12px;">⚠️ ppio 等代理服务的实际价格可能与官价不同，上表为 OpenAI/Anthropic 官方定价</p>
        </div>

        <div class="footer">
            <p>📊 Generated by praxis-ai-usage-stats | 双击打开，无需服务器</p>
        </div>
    </div>

    <script>
        // 嵌入的数据
        const ALL_EVENTS = {events_json};
        const ALL_STATS = {stats_json};

        // 图表实例
        let trendChart, kindChart, runtimeChart, skillsChart;

        // 筛选数据
        function filterEvents(events, days, runtime, kind) {{
            return events.filter(e => {{
                // 时间筛选（按自然日）
                if (days > 0) {{
                    const today = new Date();
                    today.setHours(0, 0, 0, 0);
                    const cutoff = new Date(today);
                    cutoff.setDate(cutoff.getDate() - days + 1);
                    const eventDate = new Date(e.ts);
                    if (eventDate < cutoff) return false;
                }}
                // Runtime 筛选
                if (runtime !== 'all' && e.runtime !== runtime) return false;
                // 类型筛选
                if (kind !== 'all' && e.kind !== kind) return false;
                return true;
            }});
        }}

        // 计算统计
        function calcStats(events) {{
            const total = events.length;
            const tokens = events.reduce((sum, e) => sum + (e.tokens_in || 0) + (e.tokens_out || 0), 0);
            const cost = events.reduce((sum, e) => sum + (e.cost_usd || 0), 0);

            // 按类型
            const byKind = {{}};
            events.forEach(e => {{ byKind[e.kind] = (byKind[e.kind] || 0) + 1; }});

            // 按 Runtime
            const byRuntime = {{}};
            events.forEach(e => {{ byRuntime[e.runtime] = (byRuntime[e.runtime] || 0) + 1; }});

            // 按日期
            const byDate = {{}};
            events.forEach(e => {{
                const date = e.ts.split('T')[0];
                byDate[date] = (byDate[date] || 0) + 1;
            }});

            // Top Skills
            const skillCounts = {{}};
            events.filter(e => e.kind === 'skill').forEach(e => {{
                skillCounts[e.name] = (skillCounts[e.name] || 0) + 1;
            }});
            const topSkills = Object.entries(skillCounts)
                .sort((a, b) => b[1] - a[1])
                .slice(0, 10);

            return {{ total, tokens, cost, byKind, byRuntime, byDate, topSkills }};
        }}

        // 更新统计卡片
        function updateStatsCards(stats) {{
            document.getElementById('statsGrid').innerHTML = `
                <div class="stat-card">
                    <div class="stat-value">${{stats.total.toLocaleString()}}</div>
                    <div class="stat-label">总事件数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${{(stats.tokens / 1000000).toFixed(1)}}M</div>
                    <div class="stat-label">总 Token</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">$${{stats.cost.toFixed(2)}}</div>
                    <div class="stat-label">总成本</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${{Object.keys(stats.byRuntime).length}}</div>
                    <div class="stat-label">Runtime 数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${{Object.keys(stats.byKind).length}}</div>
                    <div class="stat-label">类型数</div>
                </div>
            `;
        }}

        // 更新趋势图
        function updateTrendChart(byDate) {{
            const dates = Object.keys(byDate).sort();
            const counts = dates.map(d => byDate[d]);

            if (trendChart) trendChart.destroy();
            trendChart = new Chart(document.getElementById('trendChart'), {{
                type: 'line',
                data: {{
                    labels: dates,
                    datasets: [{{
                        label: '事件数',
                        data: counts,
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102,126,234,0.1)',
                        tension: 0.4,
                        fill: true
                    }}]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});
        }}

        // 更新类型分布图
        function updateKindChart(byKind) {{
            const labels = Object.keys(byKind);
            const data = Object.values(byKind);

            if (kindChart) kindChart.destroy();
            kindChart = new Chart(document.getElementById('kindChart'), {{
                type: 'doughnut',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: data,
                        backgroundColor: ['#667eea', '#764ba2', '#f093fb']
                    }}]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});
        }}

        // 更新 Runtime 分布图
        function updateRuntimeChart(byRuntime) {{
            const labels = Object.keys(byRuntime);
            const data = Object.values(byRuntime);

            if (runtimeChart) runtimeChart.destroy();
            runtimeChart = new Chart(document.getElementById('runtimeChart'), {{
                type: 'doughnut',
                data: {{
                    labels: labels,
                    datasets: [{{
                        data: data,
                        backgroundColor: ['#4CAF50', '#2196F3', '#FF9800']
                    }}]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});
        }}

        // 更新 Top Skills 图
        function updateSkillsChart(topSkills) {{
            const labels = topSkills.map(s => s[0]);
            const data = topSkills.map(s => s[1]);

            if (skillsChart) skillsChart.destroy();
            skillsChart = new Chart(document.getElementById('skillsChart'), {{
                type: 'bar',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: '使用次数',
                        data: data,
                        backgroundColor: '#764ba2'
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    indexAxis: 'y'
                }}
            }});
        }}

        // 更新事件表格
        function updateEventsTable(events) {{
            document.getElementById('eventCount').textContent = events.length;
            const tbody = document.getElementById('eventsBody');
            tbody.innerHTML = events.slice(-50).reverse().map(e => `
                <tr>
                    <td>${{e.ts.substring(0, 16)}}</td>
                    <td>${{e.runtime}}</td>
                    <td><span class="badge badge-${{e.kind}}">${{e.kind}}</span></td>
                    <td>${{e.name}}</td>
                    <td>${{((e.tokens_in || 0) + (e.tokens_out || 0)).toLocaleString()}}</td>
                    <td>$${{(e.cost_usd || 0).toFixed(4)}}</td>
                </tr>
            `).join('');
        }}

        // 刷新所有视图
        function refresh() {{
            const days = parseInt(document.getElementById('filterDays').value);
            const runtime = document.getElementById('filterRuntime').value;
            const kind = document.getElementById('filterKind').value;

            const filtered = filterEvents(ALL_EVENTS, days, runtime, kind);
            const stats = calcStats(filtered);

            updateStatsCards(stats);
            updateTrendChart(stats.byDate);
            updateKindChart(stats.byKind);
            updateRuntimeChart(stats.byRuntime);
            updateSkillsChart(stats.topSkills);
            updateEventsTable(filtered);
        }}

        // 绑定事件
        document.getElementById('filterDays').addEventListener('change', refresh);
        document.getElementById('filterRuntime').addEventListener('change', refresh);
        document.getElementById('filterKind').addEventListener('change', refresh);

        // 初始化
        refresh();
    </script>
</body>
</html>'''


if __name__ == "__main__":
    main()
