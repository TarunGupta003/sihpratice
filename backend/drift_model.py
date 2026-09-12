"""
ORCA Ultimate - Drift Model (Advanced Feature)
Leeway drift prediction for SOS: predicts where a disabled boat drifts given current + wind
Uses simple vector addition + empirical leeway factors
"""
import math
from typing import Dict, Any, List

class DriftModel:
    def predict(self, lat: float, lon: float, current_speed_kn: float, current_dir_deg: float, wind_speed_kn: float, wind_dir_deg: float, hours: int=6) -> Dict[str, Any]:
        # Leeway: 3-5% of wind speed for small fishing boat
        leeway_factor = 0.04
        leeway_speed = wind_speed_kn * leeway_factor
        # Total drift vector = current + leeway
        # Convert to components
        def to_components(speed, dir_deg):
            rad = math.radians(dir_deg)
            # Dir is where current flows TO (oceanographic)
            # For drift, use same
            north = speed * math.cos(rad)
            east = speed * math.sin(rad)
            return north, east

        cur_n, cur_e = to_components(current_speed_kn, current_dir_deg)
        lee_n, lee_e = to_components(leeway_speed, wind_dir_deg)
        total_n = cur_n + lee_n
        total_e = cur_e + lee_e
        total_speed = math.hypot(total_n, total_e)

        # Predict positions hourly
        positions = []
        curr_lat, curr_lon = lat, lon
        for h in range(1, hours+1):
            # Approx: 1 kn = 1.852 km/h, 1 deg lat ~111km, lon ~111*cos(lat) km
            dlat = (total_n * 1.852 * 1) / 111.0
            dlon = (total_e * 1.852 * 1) / (111.0 * math.cos(math.radians(curr_lat)))
            curr_lat += dlat
            curr_lon += dlon
            positions.append({
                "hour": h,
                "latitude": round(curr_lat,4),
                "longitude": round(curr_lon,4),
                "distance_from_origin_km": round(math.hypot((curr_lat-lat)*111, (curr_lon-lon)*111*math.cos(math.radians(lat))),1)
            })

        return {
            "origin": {"lat": lat, "lon": lon},
            "current": {"speed_kn": current_speed_kn, "dir_deg": current_dir_deg},
            "wind": {"speed_kn": wind_speed_kn, "dir_deg": wind_dir_deg},
            "leeway": {"speed_kn": round(leeway_speed,2), "factor": leeway_factor},
            "total_drift": {"speed_kn": round(total_speed,2), "north_kn": round(total_n,2), "east_kn": round(total_e,2)},
            "predictions": positions,
            "method": "Leeway drift model: 4% wind + 100% current, empirical for small motorized boat",
            "search_radius_km": round(total_speed * 1.852 * hours * 1.5,1),  # 1.5x uncertainty
            "advice": f"Search within {round(total_speed * 1.852 * hours * 1.5,1)}km down-drift. Drift speed {total_speed:.1f}kn."
        }

drift_model = DriftModel()
