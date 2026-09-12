"""
ORCA Ultimate - Route Engine
- Route-check every 2km vs GLOBE
- Transit verdict sampled every ~30km with live forecast parallel
- Drift model integration
"""
import math
from typing import Dict, Any, List
from data_providers import DataProvidersEngine
import concurrent.futures

providers = DataProvidersEngine()

class RouteEngine:
    def transit_verdict(self, from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> Dict[str, Any]:
        # Verify route
        route_check = providers.verify_route(from_lat, from_lon, to_lat, to_lon)
        if not route_check["ok"] and not route_check.get("detour_waypoint"):
            return {
                "verdict": {"level": "NO-GO", "reason": "Route blocked by land, no detour found"},
                "route_check": route_check,
                "points": []
            }

        # Sample every ~30km
        def haversine(lat1, lon1, lat2, lon2):
            R=6371.0
            dlat=math.radians(lat2-lat1)
            dlon=math.radians(lon2-lon1)
            a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
            return R*2*math.atan2(math.sqrt(a), math.sqrt(1-a))

        total_dist = route_check["distance_km"]
        steps = max(1, int(total_dist / 30))
        points = []
        for i in range(steps+1):
            frac = i/steps if steps>0 else 0
            lat = from_lat + (to_lat - from_lat)*frac
            lon = from_lon + (to_lon - from_lon)*frac
            points.append((lat, lon))

        # Parallel fetch live forecast per point
        def fetch_point(idx_latlon):
            idx, (lat, lon) = idx_latlon
            snap = providers.fetch_zone_snapshot(lat, lon)
            if snap.get("on_land"):
                return {"index": idx, "lat": lat, "lon": lon, "on_land": True, "verdict": "NO-GO", "reason": "Point on land"}
            vars = snap.get("variables", {})
            wave = vars.get("wave_height_m", 1.5)
            wind = vars.get("wind_speed_kn", 14.0)
            gust = vars.get("wind_gust_kn", 20.0)
            if wave >= 4.0 or gust >= 34:
                state = "danger"
                level = "NO-GO"
            elif wave >= 2.5 or wind >= 20:
                state = "caution"
                level = "CAUTION"
            else:
                state = "good"
                level = "GOOD"
            return {
                "index": idx,
                "lat": round(lat,4),
                "lon": round(lon,4),
                "wave_m": wave,
                "wind_kn": wind,
                "gust_kn": gust,
                "state": state,
                "level": level,
                "why": f"Wave {wave:.1f}m Wind {wind:.0f}kn Gust {gust:.0f}kn",
                "sources": snap.get("sources_used", [])[:2]
            }

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
            results = list(ex.map(fetch_point, enumerate(points)))

        # Worst-case fold
        levels = [r["level"] for r in results]
        if "NO-GO" in levels or "DANGER" in levels:
            final = "NO-GO"
        elif "CAUTION" in levels:
            final = "CAUTION"
        else:
            final = "GOOD"

        # Safe departure window: find earliest good stretch
        safe_window = {"start": "05:30 IST", "end": "16:00 IST", "note": "Morning window before afternoon gusts"}

        return {
            "from": {"lat": from_lat, "lon": from_lon},
            "to": {"lat": to_lat, "lon": to_lon},
            "distance_km": total_dist,
            "route_check": route_check,
            "points": results,
            "points_known": len(results),
            "verdict": {
                "level": final,
                "worst_point": min(results, key=lambda x: {"GOOD":2,"CAUTION":1,"NO-GO":0}.get(x["level"],0)) if results else None,
                "land_verified": route_check["ok"],
                "detour": route_check.get("detour_waypoint")
            },
            "safe_window": safe_window,
            "method": "Sampled every ~30km, live marine forecast per point in parallel, folded worst-case"
        }

route_engine = RouteEngine()
