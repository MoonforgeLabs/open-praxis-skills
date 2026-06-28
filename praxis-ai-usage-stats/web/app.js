/**
 * AI Usage Statistics - Web 仪表盘
 */

class UsageStatsApp {
    constructor() {
        this.data = null;
        this.charts = {};
        this.init();
    }

    async init() {
        await this.loadData();
        this.renderStats();
        this.renderHealthScore();
        this.renderCharts();
        this.renderTable();
        this.bindFilters();
        this.startAutoRefresh();
    }

    async loadData() {
        try {
            const response = await fetch('data.json');
            if (!response.ok) {
                throw new Error('Failed to load data');
            }
            this.rawData = await response.json();
            this.data = this.rawData;
            document.getElementById('lastUpdate').textContent = new Date().toLocaleString('zh-CN');
        } catch (error) {
            console.error('加载数据失败:', error);
            const sampleData = this.getSampleData();
            this.rawData = sampleData;
            this.data = sampleData;
        }
    }

    getSampleData() {
        // 示例数据，用于演示
        const now = new Date();
        const events = [];
        const kinds = ['skill', 'agent', 'tool'];
        const runtimes = ['claude', 'codex', 'openhuman'];
        const skills = ['alex-translate', 'alex-diagram', 'alex-format-markdown', 'alex-image-gen', 'alex-compress-image'];
        const tools = ['Read', 'Write', 'Bash', 'Grep', 'Agent'];

        for (let i = 0; i < 100; i++) {
            const date = new Date(now - Math.random() * 7 * 24 * 60 * 60 * 1000);
            const kind = kinds[Math.floor(Math.random() * kinds.length)];
            const runtime = runtimes[Math.floor(Math.random() * runtimes.length)];
            const name = kind === 'skill' ? skills[Math.floor(Math.random() * skills.length)] :
                         kind === 'agent' ? 'subagent' : tools[Math.floor(Math.random() * tools.length)];

            events.push({
                ts: date.toISOString(),
                runtime: runtime,
                kind: kind,
                name: name,
                project: 'myCode',
                model: 'claude-3-5-sonnet',
                tokens_in: Math.floor(Math.random() * 10000),
                tokens_out: Math.floor(Math.random() * 5000),
                cost_usd: Math.random() * 0.5,
                outcome: Math.random() > 0.2 ? 'likely_solved' : 'likely_failed'
            });
        }

        return {
            stats: {
                total: {
                    total_events: events.length,
                    total_tokens_in: events.reduce((sum, e) => sum + e.tokens_in, 0),
                    total_tokens_out: events.reduce((sum, e) => sum + e.tokens_out, 0),
                    total_cost: events.reduce((sum, e) => sum + e.cost_usd, 0),
                    unique_sessions: 15,
                    unique_projects: 3
                },
                by_kind: kinds.map(k => ({
                    kind: k,
                    count: events.filter(e => e.kind === k).length,
                    tokens: events.filter(e => e.kind === k).reduce((sum, e) => sum + e.tokens_in + e.tokens_out, 0),
                    cost: events.filter(e => e.kind === k).reduce((sum, e) => sum + e.cost_usd, 0)
                })),
                by_runtime: runtimes.map(r => ({
                    runtime: r,
                    count: events.filter(e => e.runtime === r).length,
                    tokens: events.filter(e => e.runtime === r).reduce((sum, e) => sum + e.tokens_in + e.tokens_out, 0),
                    cost: events.filter(e => e.runtime === r).reduce((sum, e) => sum + e.cost_usd, 0)
                })),
                top_skills: skills.map(s => ({
                    name: s,
                    count: events.filter(e => e.name === s).length,
                    tokens: events.filter(e => e.name === s).reduce((sum, e) => sum + e.tokens_in + e.tokens_out, 0),
                    cost: events.filter(e => e.name === s).reduce((sum, e) => sum + e.cost_usd, 0)
                })),
                success_stats: {
                    success_count: events.filter(e => e.outcome === 'likely_solved').length,
                    failed_count: events.filter(e => e.outcome === 'likely_failed').length,
                    unknown_count: events.filter(e => e.outcome === 'unknown').length
                },
                daily_trend: this.generateDailyTrend(events),
                by_model: [
                    { model: 'claude-3-5-sonnet', count: 80, tokens: 500000, cost: 2.5 },
                    { model: 'claude-3-haiku', count: 20, tokens: 100000, cost: 0.5 }
                ],
                by_project: [
                    { project: 'myCode', count: 60, tokens: 300000, cost: 1.5 },
                    { project: 'skills', count: 40, tokens: 200000, cost: 1.0 }
                ],
                health_score: {
                    score: 75,
                    success_score: 30,
                    frequency_score: 25,
                    diversity_score: 20,
                    success_rate: 80,
                    daily_average: 14.3,
                    runtime_count: 3
                }
            },
            events: events.sort((a, b) => new Date(b.ts) - new Date(a.ts))
        };
    }

    generateDailyTrend(events) {
        const days = {};
        events.forEach(e => {
            const date = e.ts.split('T')[0];
            if (!days[date]) {
                days[date] = { count: 0, tokens: 0, cost: 0 };
            }
            days[date].count++;
            days[date].tokens += e.tokens_in + e.tokens_out;
            days[date].cost += e.cost_usd;
        });

        return Object.entries(days)
            .sort(([a], [b]) => b.localeCompare(a))
            .slice(0, 7)
            .map(([date, data]) => ({ date, ...data }));
    }

    renderStats() {
        if (!this.data || !this.data.stats) return;

        const stats = this.data.stats;
        const total = stats.total;

        document.getElementById('totalEvents').textContent =
            (total.total_events || 0).toLocaleString();

        const totalTokens = (total.total_tokens_in || 0) + (total.total_tokens_out || 0);
        document.getElementById('totalTokens').textContent =
            (totalTokens / 1_000_000).toFixed(1) + 'M';

        document.getElementById('totalCost').textContent =
            '$' + (total.total_cost || 0).toFixed(2);

        const successStats = stats.success_stats || {};
        const totalKnown = (successStats.success_count || 0) + (successStats.failed_count || 0);
        const successRate = totalKnown > 0 ?
            ((successStats.success_count || 0) / totalKnown * 100).toFixed(1) : 0;
        document.getElementById('successRate').textContent = successRate + '%';

        const healthScore = stats.health_score || {};
        document.getElementById('healthScore').textContent =
            (healthScore.score || 0) + '/100';

        const dailyTrend = stats.daily_trend || [];
        const dailyAvg = dailyTrend.length > 0 ?
            (dailyTrend.reduce((sum, d) => sum + d.count, 0) / dailyTrend.length).toFixed(1) : 0;
        document.getElementById('dailyAvg').textContent = dailyAvg;
    }

    renderHealthScore() {
        if (!this.data || !this.data.stats || !this.data.stats.health_score) return;

        const health = this.data.stats.health_score;
        const score = health.score || 0;

        const circle = document.getElementById('scoreCircle');
        circle.style.setProperty('--score', score);
        circle.style.setProperty('--score-color', this.getScoreColor(score));
        document.getElementById('scoreValue').textContent = score;

        document.getElementById('successScore').textContent =
            (health.success_score || 0) + '/40';
        document.getElementById('frequencyScore').textContent =
            (health.frequency_score || 0) + '/30';
        document.getElementById('diversityScore').textContent =
            (health.diversity_score || 0) + '/30';
    }

    getScoreColor(score) {
        if (score >= 70) return '#28a745';
        if (score >= 40) return '#ffc107';
        return '#dc3545';
    }

    renderCharts() {
        this.renderTrendChart();
        this.renderKindChart();
        this.renderRuntimeChart();
        this.renderModelChart();
        this.renderSkillsChart();
        this.renderProjectsChart();
    }

    renderTrendChart() {
        const ctx = document.getElementById('trendChart').getContext('2d');
        const dailyTrend = this.data.stats.daily_trend || [];

        if (this.charts.trend) {
            this.charts.trend.destroy();
        }

        this.charts.trend = new Chart(ctx, {
            type: 'line',
            data: {
                labels: dailyTrend.map(d => d.date),
                datasets: [
                    {
                        label: '事件数',
                        data: dailyTrend.map(d => d.count),
                        borderColor: '#667eea',
                        backgroundColor: 'rgba(102, 126, 234, 0.1)',
                        tension: 0.4,
                        fill: true,
                        yAxisID: 'y'
                    },
                    {
                        label: 'Token (M)',
                        data: dailyTrend.map(d => d.tokens / 1_000_000),
                        borderColor: '#764ba2',
                        backgroundColor: 'rgba(118, 75, 162, 0.1)',
                        tension: 0.4,
                        fill: true,
                        yAxisID: 'y1'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    mode: 'index',
                    intersect: false,
                },
                plugins: {
                    legend: {
                        position: 'top',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.dataset.label || '';
                                if (label) {
                                    label += ': ';
                                }
                                if (context.dataset.label.includes('Token')) {
                                    label += context.parsed.y.toFixed(2) + 'M';
                                } else {
                                    label += context.parsed.y;
                                }
                                return label;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        display: true,
                        position: 'left',
                        title: {
                            display: true,
                            text: '事件数'
                        }
                    },
                    y1: {
                        type: 'linear',
                        display: true,
                        position: 'right',
                        title: {
                            display: true,
                            text: 'Token (M)'
                        },
                        grid: {
                            drawOnChartArea: false,
                        },
                    }
                }
            }
        });
    }

    renderKindChart() {
        const ctx = document.getElementById('kindChart').getContext('2d');
        const byKind = this.data.stats.by_kind || [];

        if (this.charts.kind) {
            this.charts.kind.destroy();
        }

        this.charts.kind = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: byKind.map(k => k.kind),
                datasets: [{
                    data: byKind.map(k => k.count),
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#f093fb'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    renderRuntimeChart() {
        const ctx = document.getElementById('runtimeChart').getContext('2d');
        const byRuntime = this.data.stats.by_runtime || [];

        if (this.charts.runtime) {
            this.charts.runtime.destroy();
        }

        this.charts.runtime = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: byRuntime.map(r => r.runtime),
                datasets: [{
                    data: byRuntime.map(r => r.count),
                    backgroundColor: [
                        '#4CAF50',
                        '#2196F3',
                        '#FF9800'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }

    renderModelChart() {
        const ctx = document.getElementById('modelChart').getContext('2d');
        const byModel = this.data.stats.by_model || [];

        if (this.charts.model) {
            this.charts.model.destroy();
        }

        this.charts.model = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: byModel.map(m => m.model),
                datasets: [{
                    label: '使用次数',
                    data: byModel.map(m => m.count),
                    backgroundColor: '#667eea',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    renderSkillsChart() {
        const ctx = document.getElementById('skillsChart').getContext('2d');
        const topSkills = this.data.stats.top_skills || [];

        if (this.charts.skills) {
            this.charts.skills.destroy();
        }

        this.charts.skills = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: topSkills.map(s => s.name),
                datasets: [{
                    label: '使用次数',
                    data: topSkills.map(s => s.count),
                    backgroundColor: '#764ba2',
                    borderRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    renderProjectsChart() {
        const ctx = document.getElementById('projectsChart').getContext('2d');
        const byProject = this.data.stats.by_project || [];

        if (this.charts.projects) {
            this.charts.projects.destroy();
        }

        this.charts.projects = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: byProject.map(p => p.project),
                datasets: [{
                    data: byProject.map(p => p.count),
                    backgroundColor: [
                        '#667eea',
                        '#764ba2',
                        '#f093fb',
                        '#f5576c',
                        '#4facfe'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });
    }

    renderTable() {
        const tbody = document.getElementById('eventsTable');
        const events = this.data.events || [];

        if (events.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; padding: 20px;">暂无数据</td></tr>';
            return;
        }

        const html = events.slice(0, 50).map(event => {
            const ts = new Date(event.ts);
            const timeStr = ts.toLocaleString('zh-CN', {
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
            });

            const tokens = (event.tokens_in || 0) + (event.tokens_out || 0);
            const cost = (event.cost_usd || 0).toFixed(4);
            const outcome = event.outcome || 'unknown';

            const kindClass = `badge-${event.kind}`;
            const outcomeClass = `badge-${outcome === 'likely_solved' ? 'success' :
                                         outcome === 'likely_failed' ? 'failed' : 'unknown'}`;

            const outcomeEmoji = outcome === 'likely_solved' ? '✅' :
                                outcome === 'likely_failed' ? '❌' : '❓';

            return `
                <tr>
                    <td>${timeStr}</td>
                    <td><span class="badge badge-${event.runtime === 'claude' ? 'skill' :
                                                   event.runtime === 'codex' ? 'agent' : 'tool'}">${event.runtime}</span></td>
                    <td><span class="badge ${kindClass}">${event.kind}</span></td>
                    <td>${event.name}</td>
                    <td>${tokens.toLocaleString()}</td>
                    <td>$${cost}</td>
                    <td><span class="badge ${outcomeClass}">${outcomeEmoji} ${outcome}</span></td>
                </tr>
            `;
        }).join('');

        tbody.innerHTML = html;
    }

    bindFilters() {
        document.getElementById('period').addEventListener('change', () => this.applyFilters());
        document.getElementById('runtime').addEventListener('change', () => this.applyFilters());
        document.getElementById('kind').addEventListener('change', () => this.applyFilters());
    }

    applyFilters() {
        const period = parseInt(document.getElementById('period').value);
        const runtime = document.getElementById('runtime').value;
        const kind = document.getElementById('kind').value;

        let filteredEvents = [...(this.rawData?.events || [])];

        // 按时间范围过滤（period 为天数，0 表示全部）
        if (period > 0) {
            const now = new Date();
            let cutoff;
            if (period === 1) {
                // "今天" - 从今天 0 点开始
                cutoff = new Date(now.getFullYear(), now.getMonth(), now.getDate());
            } else {
                cutoff = new Date(now - period * 24 * 60 * 60 * 1000);
            }
            filteredEvents = filteredEvents.filter(e => new Date(e.ts) >= cutoff);
        }

        // 按 runtime 过滤
        if (runtime !== 'all') {
            filteredEvents = filteredEvents.filter(e => e.runtime === runtime);
        }

        // 按类型过滤
        if (kind !== 'all') {
            filteredEvents = filteredEvents.filter(e => e.kind === kind);
        }

        // 基于过滤后的事件重新计算统计
        this.data = this.recalculateStats(filteredEvents);
        this.renderStats();
        this.renderHealthScore();
        this.renderCharts();
        this.renderTable();
    }

    recalculateStats(events) {
        const kinds = ['skill', 'agent', 'tool'];
        const runtimes = [...new Set(events.map(e => e.runtime))];
        const models = [...new Set(events.map(e => e.model).filter(Boolean))];
        const projects = [...new Set(events.map(e => e.project).filter(Boolean))];
        const skills = events.filter(e => e.kind === 'skill').map(e => e.name);
        const tools = events.filter(e => e.kind === 'tool').map(e => e.name);

        const totalTokensIn = events.reduce((sum, e) => sum + (e.tokens_in || 0), 0);
        const totalTokensOut = events.reduce((sum, e) => sum + (e.tokens_out || 0), 0);
        const totalCost = events.reduce((sum, e) => sum + (e.cost_usd || 0), 0);

        // 按类型统计
        const byKind = kinds.map(k => {
            const kindEvents = events.filter(e => e.kind === k);
            return {
                kind: k,
                count: kindEvents.length,
                tokens: kindEvents.reduce((sum, e) => sum + (e.tokens_in || 0) + (e.tokens_out || 0), 0),
                cost: kindEvents.reduce((sum, e) => sum + (e.cost_usd || 0), 0)
            };
        });

        // 按 runtime 统计
        const byRuntime = runtimes.map(r => {
            const rtEvents = events.filter(e => e.runtime === r);
            return {
                runtime: r,
                count: rtEvents.length,
                tokens: rtEvents.reduce((sum, e) => sum + (e.tokens_in || 0) + (e.tokens_out || 0), 0),
                cost: rtEvents.reduce((sum, e) => sum + (e.cost_usd || 0), 0)
            };
        });

        // 按模型统计
        const byModel = models.map(m => {
            const modelEvents = events.filter(e => e.model === m);
            return {
                model: m,
                count: modelEvents.length,
                tokens: modelEvents.reduce((sum, e) => sum + (e.tokens_in || 0) + (e.tokens_out || 0), 0),
                cost: modelEvents.reduce((sum, e) => sum + (e.cost_usd || 0), 0)
            };
        });

        // 按项目统计
        const byProject = projects.map(p => {
            const projEvents = events.filter(e => e.project === p);
            return {
                project: p,
                count: projEvents.length,
                tokens: projEvents.reduce((sum, e) => sum + (e.tokens_in || 0) + (e.tokens_out || 0), 0),
                cost: projEvents.reduce((sum, e) => sum + (e.cost_usd || 0), 0)
            };
        });

        // Top skills
        const skillCounts = {};
        skills.forEach(s => { skillCounts[s] = (skillCounts[s] || 0) + 1; });
        const topSkills = Object.entries(skillCounts)
            .map(([name, count]) => {
                const skillEvents = events.filter(e => e.name === name);
                return {
                    name,
                    count,
                    tokens: skillEvents.reduce((sum, e) => sum + (e.tokens_in || 0) + (e.tokens_out || 0), 0),
                    cost: skillEvents.reduce((sum, e) => sum + (e.cost_usd || 0), 0)
                };
            })
            .sort((a, b) => b.count - a.count);

        // 成功/失败统计
        const successCount = events.filter(e => e.outcome === 'likely_solved').length;
        const failedCount = events.filter(e => e.outcome === 'likely_failed').length;
        const unknownCount = events.filter(e => !e.outcome || e.outcome === 'unknown').length;

        // 每日趋势
        const dailyTrend = this.generateDailyTrend(events);

        // 健康评分
        const totalKnown = successCount + failedCount;
        const successRate = totalKnown > 0 ? (successCount / totalKnown * 100) : 0;
        const days = new Set(events.map(e => e.ts.split('T')[0])).size || 1;
        const dailyAvg = events.length / days;
        const runtimeCount = runtimes.length;
        const successScore = Math.min(40, Math.round(successRate * 0.4));
        const frequencyScore = Math.min(30, Math.round(dailyAvg * 2));
        const diversityScore = Math.min(30, runtimeCount * 10);
        const healthScore = successScore + frequencyScore + diversityScore;

        // 计算会话数（使用唯一项目+日期组合作为近似）
        const sessions = new Set(events.map(e => `${e.project}-${e.ts?.split('T')[0]}`));

        return {
            stats: {
                total: {
                    total_events: events.length,
                    total_tokens_in: totalTokensIn,
                    total_tokens_out: totalTokensOut,
                    total_cost: totalCost,
                    unique_sessions: sessions.size,
                    unique_projects: projects.length
                },
                by_kind: byKind,
                by_runtime: byRuntime,
                by_model: byModel,
                by_project: byProject,
                top_skills: topSkills,
                success_stats: {
                    success_count: successCount,
                    failed_count: failedCount,
                    unknown_count: unknownCount
                },
                daily_trend: dailyTrend,
                health_score: {
                    score: healthScore,
                    success_score: successScore,
                    frequency_score: frequencyScore,
                    diversity_score: diversityScore,
                    success_rate: successRate,
                    daily_average: dailyAvg,
                    runtime_count: runtimeCount
                }
            },
            events: events.sort((a, b) => new Date(b.ts) - new Date(a.ts))
        };
    }

    startAutoRefresh() {
        // 每 5 分钟自动刷新
        setInterval(async () => {
            await this.loadData();
            this.applyFilters();
        }, 5 * 60 * 1000);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new UsageStatsApp();
});
