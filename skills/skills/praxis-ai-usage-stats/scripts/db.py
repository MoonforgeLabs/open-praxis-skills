#!/usr/bin/env python3
"""SQLite 数据库管理模块 - 用于持久化存储 AI 工具使用统计"""

import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
import json

DB_PATH = Path.home() / ".praxis-skills" / "data" / "ai-usage-stats" / "usage.db"


class UsageDB:
    """AI 工具使用统计数据库"""

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_tables()

    def _init_tables(self):
        """初始化数据库表结构"""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                runtime TEXT NOT NULL,
                kind TEXT NOT NULL,
                name TEXT NOT NULL,
                project TEXT DEFAULT '',
                model TEXT DEFAULT '',
                context TEXT DEFAULT '',
                tokens_in INTEGER DEFAULT 0,
                tokens_out INTEGER DEFAULT 0,
                cache_read INTEGER DEFAULT 0,
                cache_creation INTEGER DEFAULT 0,
                latency_ms INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0,
                outcome TEXT DEFAULT 'unknown',
                triggered_by TEXT DEFAULT '',
                user_followup TEXT DEFAULT '',
                interrupted INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                session_id TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts);
            CREATE INDEX IF NOT EXISTS idx_events_kind ON events(kind);
            CREATE INDEX IF NOT EXISTS idx_events_name ON events(name);
            CREATE INDEX IF NOT EXISTS idx_events_runtime ON events(runtime);
            CREATE INDEX IF NOT EXISTS idx_events_project ON events(project);
            CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id);
            CREATE INDEX IF NOT EXISTS idx_events_outcome ON events(outcome);

            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                runtime TEXT NOT NULL,
                started_at TEXT NOT NULL,
                ended_at TEXT,
                project TEXT DEFAULT '',
                model TEXT DEFAULT '',
                total_tokens_in INTEGER DEFAULT 0,
                total_tokens_out INTEGER DEFAULT 0,
                total_cost REAL DEFAULT 0.0,
                event_count INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE INDEX IF NOT EXISTS idx_sessions_runtime ON sessions(runtime);
            CREATE INDEX IF NOT EXISTS idx_sessions_started ON sessions(started_at);

            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT NOT NULL,
                runtime TEXT NOT NULL,
                kind TEXT NOT NULL,
                count INTEGER DEFAULT 0,
                tokens_in INTEGER DEFAULT 0,
                tokens_out INTEGER DEFAULT 0,
                cost_usd REAL DEFAULT 0.0,
                PRIMARY KEY (date, runtime, kind)
            );
        """)
        self.conn.commit()

    def insert_event(self, event: Dict[str, Any]) -> int:
        """插入一条事件记录"""
        cursor = self.conn.execute(
            """INSERT INTO events (
                ts, runtime, kind, name, project, model, context,
                tokens_in, tokens_out, cache_read, cache_creation,
                latency_ms, cost_usd, outcome, triggered_by,
                user_followup, interrupted, error_count, session_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                event.get("ts", datetime.now().isoformat()),
                event.get("runtime", "unknown"),
                event.get("kind", "tool"),
                event.get("name", ""),
                event.get("project", ""),
                event.get("model", ""),
                event.get("context", ""),
                event.get("tokens_in", 0),
                event.get("tokens_out", 0),
                event.get("cache_read", 0),
                event.get("cache_creation", 0),
                event.get("latency_ms", 0),
                event.get("cost_usd", 0.0),
                event.get("outcome", "unknown"),
                event.get("triggered_by", ""),
                event.get("user_followup", ""),
                event.get("interrupted", 0),
                event.get("error_count", 0),
                event.get("session_id", ""),
            )
        )
        self.conn.commit()
        return cursor.lastrowid

    def insert_events_batch(self, events: List[Dict[str, Any]]) -> int:
        """批量插入事件记录"""
        cursor = self.conn.cursor()
        cursor.executemany(
            """INSERT INTO events (
                ts, runtime, kind, name, project, model, context,
                tokens_in, tokens_out, cache_read, cache_creation,
                latency_ms, cost_usd, outcome, triggered_by,
                user_followup, interrupted, error_count, session_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    e.get("ts", datetime.now().isoformat()),
                    e.get("runtime", "unknown"),
                    e.get("kind", "tool"),
                    e.get("name", ""),
                    e.get("project", ""),
                    e.get("model", ""),
                    e.get("context", ""),
                    e.get("tokens_in", 0),
                    e.get("tokens_out", 0),
                    e.get("cache_read", 0),
                    e.get("cache_creation", 0),
                    e.get("latency_ms", 0),
                    e.get("cost_usd", 0.0),
                    e.get("outcome", "unknown"),
                    e.get("triggered_by", ""),
                    e.get("user_followup", ""),
                    e.get("interrupted", 0),
                    e.get("error_count", 0),
                    e.get("session_id", ""),
                )
                for e in events
            ]
        )
        self.conn.commit()
        return len(events)

    def update_event_outcome(self, event_id: int, outcome: str,
                             user_followup: str = "") -> bool:
        """更新事件结果（用于手动标记）"""
        self.conn.execute(
            "UPDATE events SET outcome = ?, user_followup = ? WHERE id = ?",
            (outcome, user_followup, event_id)
        )
        self.conn.commit()
        return True

    def cleanup_old_records(self, days: int = 90) -> int:
        """清理超过 N 天的旧记录"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        cursor = self.conn.execute("DELETE FROM events WHERE ts < ?", (cutoff,))
        self.conn.commit()
        return cursor.rowcount

    def query_events(self, days: int = 7, runtime: str = "all",
                     kind: str = "all", project: Optional[str] = None,
                     name: Optional[str] = None,
                     outcome: Optional[str] = None) -> List[Dict[str, Any]]:
        """查询事件记录"""
        conditions = []
        params = []

        # 时间过滤
        if days > 0:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            conditions.append("ts >= ?")
            params.append(since)

        # Runtime 过滤
        if runtime != "all":
            conditions.append("runtime = ?")
            params.append(runtime)

        # 类型过滤
        if kind != "all":
            conditions.append("kind = ?")
            params.append(kind)

        # 项目过滤
        if project:
            conditions.append("project LIKE ?")
            params.append(f"%{project}%")

        # 名称过滤
        if name:
            conditions.append("name LIKE ?")
            params.append(f"%{name}%")

        # 结果过滤
        if outcome:
            conditions.append("outcome = ?")
            params.append(outcome)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT * FROM events
            WHERE {where_clause}
            ORDER BY ts DESC
        """

        cursor = self.conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

    def query_stats(self, days: int = 7, runtime: str = "all") -> Dict[str, Any]:
        """查询统计信息"""
        conditions = []
        params = []

        if days > 0:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            conditions.append("ts >= ?")
            params.append(since)

        if runtime != "all":
            conditions.append("runtime = ?")
            params.append(runtime)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        # 总体统计
        total_query = f"""
            SELECT
                COUNT(*) as total_events,
                SUM(tokens_in) as total_tokens_in,
                SUM(tokens_out) as total_tokens_out,
                SUM(cache_read) as total_cache_read,
                SUM(cache_creation) as total_cache_creation,
                SUM(cost_usd) as total_cost,
                SUM(latency_ms) as total_latency,
                COUNT(DISTINCT session_id) as unique_sessions,
                COUNT(DISTINCT project) as unique_projects
            FROM events WHERE {where_clause}
        """
        total_stats = dict(self.conn.execute(total_query, params).fetchone())

        # 按类型统计
        kind_query = f"""
            SELECT kind, COUNT(*) as count,
                   SUM(tokens_in + tokens_out) as tokens,
                   SUM(cost_usd) as cost
            FROM events WHERE {where_clause}
            GROUP BY kind ORDER BY count DESC
        """
        kind_stats = [dict(row) for row in self.conn.execute(kind_query, params).fetchall()]

        # 按 Runtime 统计
        runtime_query = f"""
            SELECT runtime, COUNT(*) as count,
                   SUM(tokens_in + tokens_out) as tokens,
                   SUM(cost_usd) as cost
            FROM events WHERE {where_clause}
            GROUP BY runtime ORDER BY count DESC
        """
        runtime_stats = [dict(row) for row in self.conn.execute(runtime_query, params).fetchall()]

        # Top Skills
        skills_query = f"""
            SELECT name, COUNT(*) as count,
                   SUM(tokens_in + tokens_out) as tokens,
                   SUM(cost_usd) as cost,
                   AVG(latency_ms) as avg_latency
            FROM events WHERE {where_clause} AND kind = 'skill'
            GROUP BY name ORDER BY count DESC LIMIT 10
        """
        top_skills = [dict(row) for row in self.conn.execute(skills_query, params).fetchall()]

        # Top Agents
        agents_query = f"""
            SELECT name, COUNT(*) as count,
                   SUM(tokens_in + tokens_out) as tokens,
                   SUM(cost_usd) as cost
            FROM events WHERE {where_clause} AND kind = 'agent'
            GROUP BY name ORDER BY count DESC LIMIT 10
        """
        top_agents = [dict(row) for row in self.conn.execute(agents_query, params).fetchall()]

        # Top Tools
        tools_query = f"""
            SELECT name, COUNT(*) as count,
                   SUM(tokens_in + tokens_out) as tokens,
                   SUM(cost_usd) as cost
            FROM events WHERE {where_clause} AND kind = 'tool'
            GROUP BY name ORDER BY count DESC LIMIT 10
        """
        top_tools = [dict(row) for row in self.conn.execute(tools_query, params).fetchall()]

        # 成功率统计
        success_query = f"""
            SELECT
                COUNT(CASE WHEN outcome = 'likely_solved' THEN 1 END) as success_count,
                COUNT(CASE WHEN outcome = 'likely_failed' THEN 1 END) as failed_count,
                COUNT(CASE WHEN outcome = 'unknown' THEN 1 END) as unknown_count
            FROM events WHERE {where_clause}
        """
        success_stats = dict(self.conn.execute(success_query, params).fetchone())

        # 每日趋势
        daily_query = f"""
            SELECT DATE(ts) as date, COUNT(*) as count,
                   SUM(tokens_in + tokens_out) as tokens,
                   SUM(cost_usd) as cost
            FROM events WHERE {where_clause}
            GROUP BY DATE(ts) ORDER BY date DESC LIMIT 30
        """
        daily_trend = [dict(row) for row in self.conn.execute(daily_query, params).fetchall()]

        # 按项目统计
        project_query = f"""
            SELECT project, COUNT(*) as count,
                   SUM(tokens_in + tokens_out) as tokens,
                   SUM(cost_usd) as cost
            FROM events WHERE {where_clause} AND project != ''
            GROUP BY project ORDER BY count DESC LIMIT 10
        """
        by_project = [dict(row) for row in self.conn.execute(project_query, params).fetchall()]

        # 按模型统计
        model_query = f"""
            SELECT model, COUNT(*) as count,
                   SUM(tokens_in + tokens_out) as tokens,
                   SUM(cost_usd) as cost
            FROM events WHERE {where_clause} AND model != ''
            GROUP BY model ORDER BY count DESC LIMIT 10
        """
        by_model = [dict(row) for row in self.conn.execute(model_query, params).fetchall()]

        return {
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "runtime_filter": runtime,
            "total": total_stats,
            "by_kind": kind_stats,
            "by_runtime": runtime_stats,
            "top_skills": top_skills,
            "top_agents": top_agents,
            "top_tools": top_tools,
            "success_stats": success_stats,
            "daily_trend": daily_trend,
            "by_project": by_project,
            "by_model": by_model,
        }

    def query_daily_trend(self, days: int = 30,
                          runtime: str = "all") -> List[Dict[str, Any]]:
        """查询每日趋势"""
        conditions = []
        params = []

        if days > 0:
            since = (datetime.now() - timedelta(days=days)).isoformat()
            conditions.append("ts >= ?")
            params.append(since)

        if runtime != "all":
            conditions.append("runtime = ?")
            params.append(runtime)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"""
            SELECT DATE(ts) as date,
                   runtime,
                   kind,
                   COUNT(*) as count,
                   SUM(tokens_in) as tokens_in,
                   SUM(tokens_out) as tokens_out,
                   SUM(cost_usd) as cost
            FROM events WHERE {where_clause}
            GROUP BY DATE(ts), runtime, kind
            ORDER BY date DESC
        """

        return [dict(row) for row in self.conn.execute(query, params).fetchall()]

    def query_session_details(self, session_id: str) -> Dict[str, Any]:
        """查询会话详情"""
        events = [dict(row) for row in self.conn.execute(
            "SELECT * FROM events WHERE session_id = ? ORDER BY ts",
            (session_id,)
        ).fetchall()]

        if not events:
            return {}

        return {
            "session_id": session_id,
            "events": events,
            "total_events": len(events),
            "total_tokens": sum(e["tokens_in"] + e["tokens_out"] for e in events),
            "total_cost": sum(e["cost_usd"] for e in events),
            "started_at": events[0]["ts"],
            "ended_at": events[-1]["ts"],
        }

    def get_health_score(self, days: int = 7) -> Dict[str, Any]:
        """计算健康评分"""
        stats = self.query_stats(days)

        total = stats["total"]["total_events"] or 0
        if total == 0:
            return {"score": 0, "details": "No data"}

        success = stats["success_stats"]["success_count"] or 0
        failed = stats["success_stats"]["failed_count"] or 0

        # 成功率评分 (0-40分)
        success_rate = success / total if total > 0 else 0
        success_score = min(40, success_rate * 40)

        # 使用频率评分 (0-30分) - 每天至少 10 个事件得满分
        daily_avg = total / days if days > 0 else 0
        frequency_score = min(30, (daily_avg / 10) * 30)

        # 多样性评分 (0-30分) - 使用多种 runtime 得满分
        runtime_count = len(stats["by_runtime"])
        diversity_score = min(30, runtime_count * 10)

        total_score = success_score + frequency_score + diversity_score

        return {
            "score": round(total_score),
            "success_score": round(success_score),
            "frequency_score": round(frequency_score),
            "diversity_score": round(diversity_score),
            "success_rate": round(success_rate * 100, 1),
            "daily_average": round(daily_avg, 1),
            "runtime_count": runtime_count,
        }

    def export_json(self, output_path: Path, days: int = 7,
                    runtime: str = "all") -> Path:
        """导出统计数据为 JSON"""
        stats = self.query_stats(days, runtime)
        events = self.query_events(days, runtime)

        export_data = {
            "stats": stats,
            "events": events[:1000],  # 限制导出数量
        }

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        return output_path

    def close(self):
        """关闭数据库连接"""
        self.conn.close()


def get_db() -> UsageDB:
    """获取数据库实例"""
    return UsageDB()


if __name__ == "__main__":
    # 测试代码
    db = get_db()
    print(f"Database created at: {db.db_path}")
    print(f"Total events: {db.query_stats()['total']['total_events']}")
    db.close()
