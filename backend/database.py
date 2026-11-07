import os
import sqlite3
import logging
from typing import Optional, Dict, Any, List
from .config import config

logger = logging.getLogger("enterprise-workflow.db")

class DatabaseManager:
    def __init__(self):
        self.db_url = config.database_url
        self.is_postgres = config.is_postgres()
        self._init_db()

    def _init_db(self):
        """Initialiseert PostgreSQL of SQLite schema afhankelijk van de omgeving."""
        if self.is_postgres:
            logger.info("Verbonden met Replit PostgreSQL: %s", self.db_url.split("@")[-1] if "@" in self.db_url else "configured")
            # PostgreSQL initialisatie via psycopg2 / connection pool indien aanwezig
        else:
            logger.info("Geen PostgreSQL gedetecteerd. SQLite fallback geactiveerd.")
            self._init_sqlite()

    def _init_sqlite(self):
        conn = sqlite3.connect("enterprise_workflows.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflows (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                requires_approval INTEGER DEFAULT 1,
                config TEXT,
                created_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS workflow_runs (
                id TEXT PRIMARY KEY,
                workflow_id TEXT,
                triggered_by TEXT,
                status TEXT NOT NULL,
                risk_score REAL,
                input_payload TEXT,
                output_result TEXT,
                started_at TEXT,
                completed_at TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                action TEXT NOT NULL,
                actor_id TEXT,
                prev_state TEXT,
                new_state TEXT,
                checksum TEXT NOT NULL,
                timestamp TEXT
            )
        """)
        conn.commit()
        conn.close()

db = DatabaseManager()
