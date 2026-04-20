"""
Audit logging: full compliance trail of all agent decisions and human actions.
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, Any

from src.data_contracts import AuditEvent


class AuditLogger:
    """SQLite-based audit log for full compliance trail."""
    
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize audit table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                contract_id TEXT NOT NULL,
                actor TEXT,
                event_details TEXT NOT NULL,
                outcome TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
    
    def log(
        self,
        event_type: str,
        contract_id: str,
        event_details: Dict[str, Any],
        outcome: str = "success",
        actor: str = None
    ) -> AuditEvent:
        """Log an event to the audit trail."""
        event = AuditEvent(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            contract_id=contract_id,
            actor=actor or "system",
            event_details=event_details,
            outcome=outcome
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO audit_events 
            (event_type, timestamp, contract_id, actor, event_details, outcome)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            event.event_type,
            event.timestamp.isoformat(),
            event.contract_id,
            event.actor,
            json.dumps(event.event_details),
            event.outcome
        ))
        conn.commit()
        conn.close()
        
        return event
    
    def get_audit_trail(self, contract_id: str) -> list[Dict[str, Any]]:
        """Retrieve full audit trail for a contract."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT event_type, timestamp, actor, event_details, outcome
            FROM audit_events
            WHERE contract_id = ?
            ORDER BY timestamp ASC
        """, (contract_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        trail = []
        for row in rows:
            trail.append({
                "event_type": row[0],
                "timestamp": row[1],
                "actor": row[2],
                "event_details": json.loads(row[3]),
                "outcome": row[4]
            })
        
        return trail
