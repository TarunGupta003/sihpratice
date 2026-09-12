"""
ORCA Ultimate - Blockchain Catch Traceability (Advanced)
Future: Hyperledger Fabric / Polygon for fisher -> buyer traceability
- Each catch gets hash, provenance, cold-chain, price transparency
- Reduces middleman fraud, enables export compliance
"""
import hashlib
import time
import json
from typing import Dict, Any

class BlockchainTrace:
    def __init__(self):
        self.chain = []
        self.create_genesis()

    def create_genesis(self):
        genesis = {
            "index": 0,
            "timestamp": int(time.time()),
            "data": {"type": "GENESIS", "message": "ORCA Blockchain Genesis - Fisher Traceability"},
            "prev_hash": "0"*64,
            "hash": self._hash({"index":0, "data":"genesis"})
        }
        self.chain.append(genesis)

    def _hash(self, data):
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

    def add_catch_block(self, catch_data: Dict[str, Any]) -> Dict[str, Any]:
        prev = self.chain[-1]
        block = {
            "index": len(self.chain),
            "timestamp": int(time.time()),
            "data": {
                "type": "CATCH",
                "catch_id": catch_data.get("id", f"catch-{int(time.time())}"),
                "fisherman_id": catch_data.get("fisherman_id", "anon-fisher"),
                "species": catch_data.get("species", "Mackerel"),
                "quantity_kg": catch_data.get("quantity_kg", 50),
                "location": {"lat": catch_data.get("latitude"), "lon": catch_data.get("longitude")},
                "harbour": catch_data.get("harbour", "Veraval"),
                "price_per_kg": catch_data.get("price_per_kg", 180),
                "cold_chain_temp_c": catch_data.get("temp_c", 2.5),
                "provenance": {
                    "sst": catch_data.get("sst", 28.2),
                    "chl": catch_data.get("chl", 1.2),
                    "advisory_verdict": catch_data.get("verdict", "GOOD"),
                    "sources": ["ORCA Advisory", "INCOIS PFZ", "NOAA CHL"]
                }
            },
            "prev_hash": prev["hash"]
        }
        block["hash"] = self._hash(block)
        self.chain.append(block)
        return block

    def verify_chain(self):
        for i in range(1, len(self.chain)):
            if self.chain[i]["prev_hash"] != self.chain[i-1]["hash"]:
                return False
        return True

    def get_trace(self, catch_id: str):
        for block in self.chain:
            if block["data"].get("catch_id") == catch_id:
                return block
        return None

blockchain = BlockchainTrace()
