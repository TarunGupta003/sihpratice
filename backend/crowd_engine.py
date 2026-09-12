"""
ORCA Ultimate - Crowd Engine (B14)
Community-aware spreading: "sabko same jagah mat bhejo"
- Anonymous 0.25° cell registry, rolling 24h window, neighbour spill-over 0.5x
- Privacy by design: no identity, no exact coords
- Explainable penalties: 8/boat capped 24; GFW ≥50h→10, ≥15h→5
"""
import time
import math
import json
import os
from typing import Dict, Any, List
from collections import defaultdict

CROWD_STORE = os.getenv("ORCA_CROWD_STORE", "/tmp/orca_crowd.json")
CELL_DEG = 0.25
WINDOW_SEC = 24*3600

class CrowdEngine:
    def __init__(self):
        self.cells: Dict[str, List[float]] = defaultdict(list)  # cell_key -> timestamps
        self._load()

    def _cell_key(self, lat, lon):
        return f"{round(lat/CELL_DEG)*CELL_DEG:.2f},{round(lon/CELL_DEG)*CELL_DEG:.2f}"

    def _load(self):
        if os.path.exists(CROWD_STORE):
            try:
                data = json.loads(open(CROWD_STORE).read())
                now = time.time()
                for k, timestamps in data.items():
                    # Keep only within window
                    self.cells[k] = [ts for ts in timestamps if now - ts < WINDOW_SEC]
            except:
                pass

    def _save(self):
        try:
            # Atomic write
            tmp = CROWD_STORE + ".tmp"
            with open(tmp, "w") as f:
                json.dump(dict(self.cells), f)
            os.rename(tmp, CROWD_STORE)
        except:
            pass

    def record_pick(self, lat: float, lon: float):
        key = self._cell_key(lat, lon)
        self.cells[key].append(time.time())
        # Also record neighbour spill-over 0.5x? Actually penalty calc does spill, not storage
        self._save()

    def get_load(self, lat: float, lon: float) -> Dict[str, Any]:
        now = time.time()
        key = self._cell_key(lat, lon)
        # Clean old
        if key in self.cells:
            self.cells[key] = [ts for ts in self.cells[key] if now - ts < WINDOW_SEC]
        
        direct = len(self.cells.get(key, []))
        # Neighbour halo: 8 surrounding cells 0.5x weight
        halo = 0
        for dlat in [-CELL_DEG, 0, CELL_DEG]:
            for dlon in [-CELL_DEG, 0, CELL_DEG]:
                if dlat==0 and dlon==0:
                    continue
                nkey = self._cell_key(lat+dlat, lon+dlon)
                if nkey in self.cells:
                    # Clean
                    self.cells[nkey] = [ts for ts in self.cells[nkey] if now - ts < WINDOW_SEC]
                    halo += len(self.cells[nkey]) * 0.5

        total_load = direct + halo
        # Penalty: 8 per boat capped 24
        penalty = min(24, int(total_load * 8))

        return {
            "cell_key": key,
            "direct_boats": direct,
            "halo_weighted": round(halo,1),
            "total_load": round(total_load,1),
            "penalty": penalty,
            "privacy": "Anonymous cell, no identity, no exact coords"
        }

crowd_engine = CrowdEngine()
