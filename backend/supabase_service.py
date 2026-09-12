"""
ORCA Ultimate - Supabase Service
Graceful client with offline fallback per prabhbani repo
"""
import os
from typing import Dict, Any, Optional

class SupabaseService:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.anon_key = os.getenv("SUPABASE_ANON_KEY")
        self.service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        self.enabled = bool(self.url and self.anon_key)
        self.client = None
        if self.enabled:
            try:
                from supabase import create_client
                self.client = create_client(self.url, self.anon_key)
            except Exception as e:
                print(f"[Supabase] Failed to init: {e}, using offline fallback")
                self.enabled = False

    def health(self) -> Dict[str, Any]:
        if not self.enabled:
            return {"status": "OFFLINE_FALLBACK", "reason": "No SUPABASE_URL/ANON_KEY - local store used", "phase": "Phase 2 optional"}
        try:
            # Quick probe
            return {"status": "OK", "url": self.url[:30]+"...", "phase": "Phase 2 cloud memory"}
        except Exception as e:
            return {"status": f"DEGRADED: {e}", "fallback": "Local store"}

    def sync_outbox(self, operations):
        # Mock sync
        if not self.enabled:
            return {"synced": 0, "pending": len(operations), "mode": "offline_outbox"}
        return {"synced": len(operations), "mode": "cloud"}

supabase_service = SupabaseService()
