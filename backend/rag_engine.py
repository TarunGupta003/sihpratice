"""
ORCA Ultimate - RAG Engine
Grounds AI reasoning in relevant source material
- Semantic + keyword retrieval + reranking
- Evidence object with source, dataset, timestamp, location, relevance
"""
import math
from typing import List, Dict, Any

# Mock knowledge base (in real, would be vector DB with embeddings)
KNOWLEDGE_BASE = [
    {"id": "doc-001", "source": "INCOIS PFZ Manual", "dataset": "PFZ", "content": "Potential Fishing Zones are identified by SST 27-29C and chlorophyll 0.5-2.5 mg/m3 overlap. Thermal fronts indicate fish aggregation.", "tags": ["pfz", "sst", "chlorophyll", "fish"], "location": "Indian EEZ", "timestamp": "2024-01-15"},
    {"id": "doc-002", "source": "WMO Small Craft Advisory", "dataset": "WMO", "content": "Small craft advisory: Wave height >2.5m CAUTION, >4.0m DANGER. Wind gust >34kn DANGER, sustained >20kn CAUTION.", "tags": ["wave", "wind", "safety", "threshold"], "location": "Global", "timestamp": "2023-06-01"},
    {"id": "doc-003", "source": "NOAA Ocean Colour", "dataset": "NOAA", "content": "Chlorophyll-a >1.5 mg/m3 indicates high plankton bloom, favorable for sardine and mackerel. Cloud masking common during monsoon.", "tags": ["chlorophyll", "plankton", "fish"], "location": "Global", "timestamp": "2024-03-10"},
    {"id": "doc-004", "source": "ISRO MOSDAC OCM-3 User Guide", "dataset": "MOSDAC", "content": "Oceansat-3 OCM-3 provides 360m resolution ocean colour, 2-day revisit. Requires SSO login. Data latency 3-6 hours.", "tags": ["mosdac", "ocm-3", "satellite"], "location": "India", "timestamp": "2023-12-01"},
    {"id": "doc-005", "source": "GLOBE 1km DEM", "dataset": "GLOBE", "content": "GLOBE 1km land mask used for route verification. Samples every 2km, detour via 16-angle search.", "tags": ["land", "route", "gis"], "location": "Global", "timestamp": "2022-01-01"},
    {"id": "doc-006", "source": "Marine Ecology Review", "dataset": "Ecology", "content": "Thermal gradient >0.5°C/km indicates front, high productivity. SST anomaly +0.4°C normal for September in Arabian Sea.", "tags": ["sst", "ecology", "front"], "location": "Arabian Sea", "timestamp": "2024-02-20"},
    {"id": "doc-007", "source": "Global Fishing Watch", "dataset": "GFW", "content": "AIS-derived fishing effort >50h/km2 indicates heavy pressure, CPUE drops. Fleet presence context for voyage planning.", "tags": ["gfw", "ais", "fleet", "effort"], "location": "Global", "timestamp": "2024-05-01"},
    {"id": "doc-008", "source": "IMD Cyclone Warning", "dataset": "JTWC", "content": "JTWC provides tropical cyclone warnings. During cyclone, all fishing banned within 200km radius.", "tags": ["cyclone", "jtwc", "storm"], "location": "Indian Ocean", "timestamp": "2024-06-15"},
]

class RAGEngine:
    def retrieve(self, query: str, top_k=5) -> List[Dict[str, Any]]:
        # Simple keyword + semantic (mock) retrieval
        q_lower = query.lower()
        scored = []
        for doc in KNOWLEDGE_BASE:
            score = 0
            for tag in doc["tags"]:
                if tag in q_lower:
                    score += 2
            # Content overlap
            for word in q_lower.split():
                if len(word)>3 and word in doc["content"].lower():
                    score += 1
            # Semantic boost for marine terms
            if any(term in q_lower for term in ["wave", "wind", "safe", "pfz", "fish"]):
                if any(term in doc["content"].lower() for term in ["wave", "wind", "fish", "pfz"]):
                    score += 1
            if score>0:
                scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = []
        for score, doc in scored[:top_k]:
            results.append({
                "document_id": doc["id"],
                "source": doc["source"],
                "dataset": doc["dataset"],
                "content": doc["content"],
                "relevance_score": round(score/10, 2),
                "location": doc["location"],
                "timestamp": doc["timestamp"],
                "chunk_id": f"{doc['id']}-chunk-0"
            })
        return results

    def context_builder(self, query: str, evidence: List[Dict]) -> str:
        ctx = f"Query: {query}\n\nEvidence:\n"
        for ev in evidence:
            ctx += f"- [{ev['source']}] {ev['content']} (score {ev['relevance_score']})\n"
        return ctx

rag_engine = RAGEngine()
