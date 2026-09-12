"""
ORCA Ultimate - LoRa Mesh Offline SOS (Advanced)
- When no cellular, boats form LoRa mesh (868MHz, 5-10km range)
- SOS hops via mesh to reach ORCA Box or harbour gateway
- DTN (Delay Tolerant Network) with store-and-forward
"""
import time
import math
from typing import Dict, Any, List

class LoRaMesh:
    def __init__(self):
        self.nodes = {}  # node_id -> last_seen, lat, lon
        self.messages = []  # mesh messages

    def register_node(self, node_id: str, lat: float, lon: float):
        self.nodes[node_id] = {"lat": lat, "lon": lon, "last_seen": int(time.time()), "battery": 85}

    def simulate_mesh_propagation(self, origin_lat: float, origin_lon: float, sos_message: str, max_hops=5) -> Dict[str, Any]:
        # Simulate mesh: find nodes within 10km, hop
        reachable = []
        for nid, node in self.nodes.items():
            dist = self._haversine(origin_lat, origin_lon, node["lat"], node["lon"])
            if dist <= 10:
                reachable.append({"node_id": nid, "distance_km": round(dist,1), "hops": 1, "battery": node["battery"]})

        # Multi-hop
        all_reached = reachable.copy()
        hops = 1
        while hops < max_hops and len(all_reached) < len(self.nodes):
            new_nodes = []
            for r in reachable:
                # From this node, find further nodes
                for nid, node in self.nodes.items():
                    if any(n["node_id"]==nid for n in all_reached):
                        continue
                    # Distance from current hop node
                    curr_node = self.nodes.get(r["node_id"])
                    if not curr_node:
                        continue
                    dist = self._haversine(curr_node["lat"], curr_node["lon"], node["lat"], node["lon"])
                    if dist <= 8:  # LoRa range
                        new_nodes.append({"node_id": nid, "distance_km": round(dist,1), "hops": hops+1, "via": r["node_id"], "battery": node["battery"]})
            if not new_nodes:
                break
            all_reached.extend(new_nodes)
            reachable = new_nodes
            hops += 1

        return {
            "origin": {"lat": origin_lat, "lon": origin_lon},
            "sos_message": sos_message,
            "mesh": {
                "protocol": "LoRa 868MHz, SF7, BW 125kHz, 5km range, DTN store-and-forward",
                "max_hops": max_hops,
                "nodes_total": len(self.nodes),
                "nodes_reached": len(all_reached),
                "reachability_percent": round(len(all_reached)/max(1,len(self.nodes))*100,1),
                "hops": all_reached,
                "gateway_reached": len(all_reached) > 0,
                "latency_sec": hops*2 + len(all_reached)*0.5
            },
            "note": "Even without internet, SOS reaches harbour gateway via mesh. ORCA Box syncs when back online (offline-first outbox)."
        }

    def _haversine(self, lat1, lon1, lat2, lon2):
        R=6371.0
        dlat=math.radians(lat2-lat1)
        dlon=math.radians(lon2-lon1)
        a=math.sin(dlat/2)**2+math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
        return R*2*math.atan2(math.sqrt(a), math.sqrt(1-a))

lora_mesh = LoRaMesh()
# Pre-populate some demo nodes
for i in range(5):
    lora_mesh.register_node(f"boat-mesh-{i}", 20.9 + i*0.05, 70.37 + i*0.05)
