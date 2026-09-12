"""
ORCA Ultimate - Voyage Planner
Combines INCOIS PFZ official + NOAA CHL hotspots + ML PFZ + Crowd spreading + GFW
"""
import math
import random
from typing import Dict, Any, List
from data_providers import DataProvidersEngine
from crowd_engine import crowd_engine

providers = DataProvidersEngine()

class VoyagePlanner:
    def generate_candidates(self, lat: float, lon: float, count=8) -> List[Dict[str, Any]]:
        # Generate candidate fishing spots around current location within 30km
        candidates = []
        random.seed(int(lat*1000 + lon*1000))
        for i in range(count):
            angle = random.uniform(0, 360)
            dist_km = random.uniform(5, 35)
            dlat = (dist_km/111.0) * math.cos(math.radians(angle))
            dlon = (dist_km/(111.0*math.cos(math.radians(lat)))) * math.sin(math.radians(angle))
            clat = lat + dlat
            clon = lon + dlon
            # Fetch live conditions at that exact spot
            snap = providers.fetch_zone_snapshot(clat, clon)
            if snap.get("on_land"):
                continue
            vars = snap.get("variables", {})
            chl = vars.get("chlorophyll_mg_m3", 1.0)
            sst = vars.get("sst_celsius", 28.0)
            wave = vars.get("wave_height_m", 1.5)
            wind = vars.get("wind_speed_kn", 14.0)
            pfz = snap.get("pfz", {})

            # Scoring: CHL + SST optimal + PFZ + safety
            # SST optimal 27-29C, CHL 0.5-3.0 high
            sst_score = max(0, 20 - abs(sst-28.0)*8)
            chl_score = min(30, chl*12)
            pfz_score = 25 if pfz.get("pfz_nearby") else (10 if chl>1.2 else 0)
            safety_score = 20 if wave<2.0 and wind<18 else (10 if wave<2.5 else 0)
            base_score = sst_score + chl_score + pfz_score + safety_score

            # GFW penalty
            gfw = snap.get("gfw", {})
            gfw_hours = gfw.get("fishing_effort_hours") or 0
            gfw_penalty = 0
            gfw_note = ""
            if gfw_hours >= 50:
                gfw_penalty = 10
                gfw_note = f"GFW AIS fleet heavy {gfw_hours}h → -10 (stock pressure)"
            elif gfw_hours >= 15:
                gfw_penalty = 5
                gfw_note = f"GFW AIS fleet moderate {gfw_hours}h → -5"

            # Crowd penalty
            crowd = crowd_engine.get_load(clat, clon)
            crowd_penalty = crowd["penalty"]
            crowd_note = f"Community {crowd['total_load']} boats in cell {crowd['cell_key']} → -{crowd_penalty}" if crowd_penalty>0 else "No community load"

            final_score = max(0, base_score - gfw_penalty - crowd_penalty)

            candidates.append({
                "id": f"spot-{i+1}",
                "latitude": round(clat,4),
                "longitude": round(clon,4),
                "distance_km": round(dist_km,1),
                "bearing_deg": int(angle),
                "variables": vars,
                "pfz": pfz,
                "gfw": gfw,
                "score_base": round(base_score,1),
                "score_final": round(final_score,1),
                "penalties": {
                    "gfw": gfw_penalty,
                    "crowd": crowd_penalty
                },
                "reasons": [
                    f"SST {sst:.1f}°C optimal → +{sst_score:.0f}",
                    f"CHL {chl:.2f} mg/m³ → +{chl_score:.0f}",
                    f"PFZ {'nearby '+str(pfz.get('distance_km'))+'km' if pfz.get('pfz_nearby') else 'no official line, ML hotspot'} → +{pfz_score}",
                    f"Safety wave {wave:.1f}m wind {wind:.0f}kn → +{safety_score}",
                    gfw_note or "GFW no heavy fleet → +0",
                    crowd_note
                ],
                "crowd": crowd,
                "sources": snap.get("sources_used", [])
            })

        # Sort by final score
        candidates.sort(key=lambda x: x["score_final"], reverse=True)
        return candidates

    def plan(self, lat: float, lon: float) -> Dict[str, Any]:
        candidates = self.generate_candidates(lat, lon, count=10)
        # Top-3 deep GFW check already done in candidate generation
        # Record #1 as served for next fisher spread
        if candidates:
            top = candidates[0]
            crowd_engine.record_pick(top["latitude"], top["longitude"])

        return {
            "origin": {"lat": lat, "lon": lon},
            "candidates": candidates,
            "top_pick": candidates[0] if candidates else None,
            "policy": "B14 crowd-spread: ranked spots de-scored by (a) GFW AIS fleet hours (30d, top-3) and (b) ORCA's own anonymous community picks (0.25° cells, 24h). Served #1 remembered → next fisher nudged to next-best. Sabko same jagah nahi bhejte.",
            "scoring": "SST optimal 27-29C + CHL 0.5-3.0 + PFZ + safety - GFW penalty - community penalty",
            "timestamp": __import__("time").time()
        }

voyage_planner = VoyagePlanner()
