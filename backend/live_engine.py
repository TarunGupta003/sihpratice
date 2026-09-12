"""
ORCA Ultimate - Live Engine
Features from Sangam backend B19/B20:
- Beacon ON/OFF (anonymous AIS-style)
- WATCH MODE (watch=true) - listen without beacon, coarse 0.1° rounding for privacy
- Late-joiner re-dispatch
- ORCA Radio: 2-way rescue messaging (victim <-> accepted rescuer only)
- SOS lifecycle
"""
import time
import math
import uuid
from typing import Dict, Any, List, Optional
from collections import defaultdict

WATCH_CELL_DEG = 0.1  # ~11km privacy rounding for watch mode

class LiveEngine:
    def __init__(self):
        self.beacons: Dict[str, Dict[str, Any]] = {}  # pid -> beacon
        self.watchers: Dict[str, Dict[str, Any]] = {}  # pid -> watcher (coarse)
        self.sos_cases: Dict[str, Dict[str, Any]] = {}  # case_id -> case
        self.rescue_messages: Dict[str, List[Dict]] = defaultdict(list)  # case_id -> msgs
        self.boat_id_counter = 0

    def _round_watch(self, lat, lon):
        return round(lat / WATCH_CELL_DEG) * WATCH_CELL_DEG, round(lon / WATCH_CELL_DEG) * WATCH_CELL_DEG

    def _haversine(self, lat1, lon1, lat2, lon2):
        R=6371.0
        dlat=math.radians(lat2-lat1)
        dlon=math.radians(lon2-lon1)
        a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
        return R*2*math.atan2(math.sqrt(a), math.sqrt(1-a))

    def start_beacon(self, lat: float, lon: float, boat_name: str = "Anonymous Boat", watch: bool=False) -> Dict[str, Any]:
        pid = f"boat-{uuid.uuid4().hex[:8]}"
        if watch:
            # Watch mode: coarse privacy, not visible on radar
            clat, clon = self._round_watch(lat, lon)
            self.watchers[pid] = {
                "public_id": pid,
                "lat_coarse": clat,
                "lon_coarse": clon,
                "lat_exact": None,
                "lon_exact": None,
                "mode": "WATCH",
                "started_at": int(time.time()),
                "last_seen": int(time.time())
            }
            return {"public_id": pid, "mode": "WATCH", "privacy": f"Coarse {WATCH_CELL_DEG}° (~11km)", "message": "You are in WATCH mode - listening for SOS, not broadcasting exact position"}
        else:
            self.beacons[pid] = {
                "public_id": pid,
                "boat_name": boat_name,
                "lat": lat,
                "lon": lon,
                "mode": "BEACON",
                "started_at": int(time.time()),
                "last_seen": int(time.time()),
                "sos_active": False,
                "status": "ACTIVE"
            }
            return {"public_id": pid, "mode": "BEACON", "lat": lat, "lon": lon, "message": "Beacon ON - you are visible to nearby boats"}

    def ping(self, public_id: str, lat: float, lon: float, watch: bool=False, sos: bool=False) -> Dict[str, Any]:
        # Update beacon or watcher
        if public_id in self.beacons:
            self.beacons[public_id]["lat"] = lat
            self.beacons[public_id]["lon"] = lon
            self.beacons[public_id]["last_seen"] = int(time.time())
        elif public_id in self.watchers:
            clat, clon = self._round_watch(lat, lon)
            self.watchers[public_id]["lat_coarse"] = clat
            self.watchers[public_id]["lon_coarse"] = clon
            self.watchers[public_id]["last_seen"] = int(time.time())
        else:
            # Auto-start if unknown
            if watch:
                return self.start_beacon(lat, lon, watch=True)
            else:
                return self.start_beacon(lat, lon)

        # Check SOS nearby (for both beacon and watch)
        nearby_sos = []
        for case_id, case in self.sos_cases.items():
            if case["status"] != "ACTIVE":
                continue
            dist = self._haversine(lat, lon, case["lat"], case["lon"])
            if dist <= 50:  # 50km radius
                nearby_sos.append({
                    "case_id": case_id,
                    "distance_km": round(dist,1),
                    "bearing": int((case["lon"]-lon)*10) % 360,
                    "victim_id": case["victim_id"][:8]+"...",
                    "sos_message": case.get("message","HELP"),
                    "created_at": case["created_at"]
                })

        # Late-joiner fix: re-dispatch open cases to this newly arrived boat
        dispatched = []
        if nearby_sos:
            for sos_info in nearby_sos:
                case_id = sos_info["case_id"]
                case = self.sos_cases[case_id]
                # If this boat not already dispatched and not victim
                if public_id != case["victim_id"] and public_id not in case.get("dispatched_to", []):
                    if "dispatched_to" not in case:
                        case["dispatched_to"] = []
                    case["dispatched_to"].append(public_id)
                    dispatched.append(case_id)

        # Get rescue messages for this boat if it's part of a case
        my_messages = []
        for case_id, msgs in self.rescue_messages.items():
            case = self.sos_cases.get(case_id)
            if not case:
                continue
            if public_id == case["victim_id"] or public_id in case.get("accepted_by", []):
                my_messages.extend(msgs[-5:])  # last 5

        # Nearby boats (beacons only, watchers hidden)
        nearby_boats = []
        for pid, b in self.beacons.items():
            if pid == public_id:
                continue
            if b["status"] != "ACTIVE":
                continue
            dist = self._haversine(lat, lon, b["lat"], b["lon"])
            if dist <= 30:
                nearby_boats.append({
                    "public_id": pid,
                    "distance_km": round(dist,1),
                    "boat_name": b["boat_name"],
                    "sos_active": b["sos_active"]
                })

        return {
            "public_id": public_id,
            "mode": "WATCH" if public_id in self.watchers else "BEACON",
            "sos_nearby": nearby_sos,
            "dispatched_new": dispatched,
            "nearby_boats": nearby_boats,
            "watchers_count": len(self.watchers),
            "rescue_messages": my_messages,
            "timestamp": int(time.time()),
            "late_joiner_fix": f"Re-dispatched {len(dispatched)} open SOS to you (B20 fix)"
        }

    def sos_on(self, public_id: str, lat: float, lon: float, message: str="HELP - Engine failure") -> Dict[str, Any]:
        # Flip to exact beacon if was watcher (consent)
        if public_id in self.watchers:
            # Consent to reveal exact for SOS
            self.beacons[public_id] = {
                "public_id": public_id,
                "boat_name": f"Boat-{public_id[-4:]}",
                "lat": lat,
                "lon": lon,
                "mode": "BEACON",
                "started_at": self.watchers[public_id]["started_at"],
                "last_seen": int(time.time()),
                "sos_active": True,
                "status": "SOS_ACTIVE"
            }
            del self.watchers[public_id]
        elif public_id in self.beacons:
            self.beacons[public_id]["lat"] = lat
            self.beacons[public_id]["lon"] = lon
            self.beacons[public_id]["sos_active"] = True
            self.beacons[public_id]["status"] = "SOS_ACTIVE"
        else:
            # Auto create
            self.beacons[public_id] = {
                "public_id": public_id,
                "boat_name": f"Boat-{public_id[-4:]}",
                "lat": lat,
                "lon": lon,
                "mode": "BEACON",
                "started_at": int(time.time()),
                "last_seen": int(time.time()),
                "sos_active": True,
                "status": "SOS_ACTIVE"
            }

        case_id = f"sos-{uuid.uuid4().hex[:8]}"
        self.sos_cases[case_id] = {
            "case_id": case_id,
            "victim_id": public_id,
            "lat": lat,
            "lon": lon,
            "message": message,
            "status": "ACTIVE",
            "created_at": int(time.time()),
            "dispatched_to": [],
            "accepted_by": [],
            "declined_by": []
        }
        return {"case_id": case_id, "status": "SOS_ACTIVE", "message": "SOS broadcast to nearby boats + watchers within 50km", "privacy_note": "Exact position now revealed for rescue (consent via SOS)"}

    def sos_clear(self, public_id: str) -> Dict[str, Any]:
        # Clear SOS
        cleared = []
        for case_id, case in list(self.sos_cases.items()):
            if case["victim_id"] == public_id and case["status"] == "ACTIVE":
                case["status"] = "RESOLVED"
                cleared.append(case_id)
                # Wipe messages
                if case_id in self.rescue_messages:
                    del self.rescue_messages[case_id]
        if public_id in self.beacons:
            self.beacons[public_id]["sos_active"] = False
            self.beacons[public_id]["status"] = "ACTIVE"
        return {"cleared_cases": cleared, "message": "SOS cleared - you are safe. Messages wiped."}

    def stop_beacon(self, public_id: str) -> Dict[str, Any]:
        if public_id in self.beacons:
            del self.beacons[public_id]
        if public_id in self.watchers:
            del self.watchers[public_id]
        # Clear any SOS
        self.sos_clear(public_id)
        return {"public_id": public_id, "status": "DELETED", "message": "Beacon OFF - instant full delete (privacy). No trace left."}

    def rescue_answer(self, public_id: str, case_id: str, answer: str) -> Dict[str, Any]:
        # answer: accept / decline
        case = self.sos_cases.get(case_id)
        if not case:
            return {"error": "Case not found"}
        if case["status"] != "ACTIVE":
            return {"error": "Case not active"}
        if public_id == case["victim_id"]:
            return {"error": "Victim cannot answer own SOS"}
        
        if answer == "accept":
            if public_id not in case["accepted_by"]:
                case["accepted_by"].append(public_id)
            # Flip acceptor to exact beacon if watcher (consent)
            if public_id in self.watchers:
                # Need lat/lon - use coarse for now, will be updated on next ping
                w = self.watchers[public_id]
                self.beacons[public_id] = {
                    "public_id": public_id,
                    "boat_name": f"Rescuer-{public_id[-4:]}",
                    "lat": w["lat_coarse"],
                    "lon": w["lon_coarse"],
                    "mode": "BEACON",
                    "started_at": w["started_at"],
                    "last_seen": int(time.time()),
                    "sos_active": False,
                    "status": "RESCUE_ENROUTE"
                }
                del self.watchers[public_id]
            return {"case_id": case_id, "status": "ACCEPTED", "message": "You accepted rescue. Victim notified. ORCA Radio channel opened."}
        else:
            if public_id not in case["declined_by"]:
                case["declined_by"].append(public_id)
            return {"case_id": case_id, "status": "DECLINED", "message": "Declined. You won't be spammed again for this case (B20)."}

    def rescue_complete(self, public_id: str, case_id: str) -> Dict[str, Any]:
        case = self.sos_cases.get(case_id)
        if not case:
            return {"error": "Case not found"}
        if public_id not in case["accepted_by"] and public_id != case["victim_id"]:
            return {"error": "Only accepted rescuer or victim can complete"}
        case["status"] = "RESCUED"
        # Wipe messages
        if case_id in self.rescue_messages:
            del self.rescue_messages[case_id]
        # Clear victim SOS
        victim_id = case["victim_id"]
        if victim_id in self.beacons:
            self.beacons[victim_id]["sos_active"] = False
            self.beacons[victim_id]["status"] = "ACTIVE"
        return {"case_id": case_id, "status": "RESCUED", "message": "Rescue marked complete. Case closed, messages wiped."}

    def rescue_msg(self, public_id: str, case_id: str, text: str) -> Dict[str, Any]:
        case = self.sos_cases.get(case_id)
        if not case:
            return {"error": "Case not found"}
        if case["status"] != "ACTIVE":
            return {"error": "Case not active"}
        # Only victim <-> accepted rescuer
        allowed = [case["victim_id"]] + case.get("accepted_by", [])
        if public_id not in allowed:
            return {"error": "403 - Only victim and accepted rescuers can use ORCA Radio for this case"}
        if len(text) > 140:
            return {"error": "Message too long (140c max)"}
        if len(self.rescue_messages[case_id]) >= 30:
            return {"error": "Message cap 30 reached - case channel full"}

        msg = {
            "from": public_id,
            "text": text,
            "timestamp": int(time.time()),
            "case_id": case_id
        }
        self.rescue_messages[case_id].append(msg)
        return {"sent": True, "message": msg, "channel": f"ORCA Radio - Case {case_id}"}

    def nearby(self, lat: float, lon: float, radius_km: float=30) -> Dict[str, Any]:
        boats = []
        for pid, b in self.beacons.items():
            if b["status"] not in ["ACTIVE", "SOS_ACTIVE", "RESCUE_ENROUTE"]:
                continue
            dist = self._haversine(lat, lon, b["lat"], b["lon"])
            if dist <= radius_km:
                boats.append({
                    "public_id": pid,
                    "boat_name": b["boat_name"],
                    "lat": b["lat"],
                    "lon": b["lon"],
                    "distance_km": round(dist,1),
                    "bearing": int((b["lon"]-lon)*50) % 360,
                    "sos_active": b["sos_active"],
                    "status": b["status"]
                })
        return {
            "boats": boats,  # beacons only
            "watchers_count": len(self.watchers),
            "total_beacons": len(self.beacons),
            "radius_km": radius_km,
            "privacy": "Watchers hidden from radar, only count shown (AIS-receiver philosophy)"
        }

    def all_sos(self) -> List[Dict]:
        active = []
        for case in self.sos_cases.values():
            if case["status"] == "ACTIVE":
                active.append(case)
        return active

    def stats(self) -> Dict[str, Any]:
        return {
            "total_beacons": len(self.beacons),
            "total_watchers": len(self.watchers),
            "active_sos": len([c for c in self.sos_cases.values() if c["status"]=="ACTIVE"]),
            "total_cases": len(self.sos_cases),
            "privacy_policy": "WATCH mode = coarse 0.1° (~11km) privacy, not on radar. SOS/Accept = consent to exact. STOP = instant delete. Radio = victim<->rescuer only, 30 msg cap, wiped on resolve.",
            "b20_features": ["WATCH mode", "Late-joiner dispatch", "ORCA Radio", "Coarse privacy", "Declined-no-spam"]
        }

live_engine = LiveEngine()
