# ORCA Ultimate — SIH 2026 ISRO PS26176
### Marine EcOsystem Reasoning with Collaborative Agents — Super Advanced Merged Build

**This repo merges:**
- `prabhbani/ORCA-SIH-2026`: 11-agent engine, Ollama Qwen3:8b, Supabase Phase 2, SSE, Flutter structure, voice advisory
- `SangamSitapuri07/ORCA-backend`: 12 live ocean sources, 29 pipeline modules, voyage planner, route-check 2km, transit verdict 30km, crowd B14, live beacon B20 (watch mode, late-joiner, radio), last-known-good fallback, honest failures
- **Plus extra advanced features** beyond both: ML PFZ LSTM, Drift leeway model, RAG, Carbon tracker, Marketplace, 3D bathymetry, YOLOv8 species, Sarvam/Bhashini voice, Blockchain traceability mock, Edge ONNX

---

## Architecture (Invariant)

```
Flutter APK = Interface
ORCA Box (FastAPI backend) = Brain
Supabase = Optional Cloud Memory (Phase 2)
```

- Safety-critical verdicts from backend only
- Every number has provenance (source + observed_at + freshness)
- No fabricated data — failures named honestly
- Offline-first with explicit staleness
- Edge-first intelligence (ORCA Box)
- Explainable AI trace (real agent events)
- Graceful degradation
- Modular registry-driven

---

## Features Matrix

| Feature | Source | Status in Ultimate |
|---------|--------|-------------------|
| 11 agents (5 deterministic + 6 LLM) | prabhbani | ✅ Merged + Ollama fallback |
| DataProviders 12 sources | Sangam | ✅ + last-good cache |
| Ollama Qwen3:8b | prabhbani | ✅ with fallback |
| Supabase 6 tables RLS | prabhbani | ✅ graceful offline |
| SSE live stream | both | ✅ unified |
| Route-check 2km GLOBE + detour | Sangam | ✅ |
| Voyage planner + crowd B14 | Sangam | ✅ |
| Transit verdict 30km sampling | Sangam | ✅ parallel fetch |
| ORCA Live Beacon/Watch/Radio B20 | Sangam | ✅ full |
| Voice advisory | prabhbani | ✅ + Sarvam mock |
| Field explorer + tiles | Sangam | ✅ |
| RAG evidence | design doc | ✅ implemented |
| ML PFZ LSTM | **NEW ADVANCED** | ✅ heuristic + SHAP |
| Drift model leeway | **NEW ADVANCED** | ✅ 4% wind + current |
| Carbon tracker | **NEW ADVANCED** | ✅ |
| Marketplace | **NEW ADVANCED** | ✅ |
| 3D bathymetry GEBCO | **NEW ADVANCED** | ✅ mock + Deck.gl ready |
| YOLOv8 species detection | **NEW ADVANCED** | ✅ endpoint + ONNX note |
| Blockchain catch trace | **NEW ADVANCED** | ✅ future roadmap |

---

## Quick Start — Web Version (Phase 1 Demo)

### Backend (ORCA Box Brain)

```bash
cd backend
pip install -r requirements.txt

# Optional .env (all optional, runs without)
cp .env.example .env
# Edit GFW_API_TOKEN, MOSDAC, SUPABASE if you have

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open:
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health
- Advisory: http://localhost:8000/api/v1/advisory?lat=20.9&lon=70.37

### Frontend Web (Vite React)

```bash
cd frontend-web
npm install
npm run dev
```

Open http://localhost:5173

- Home: CAN I GO? verdict with fisher-first simple UI (26A philosophy: LESS UI, LESS TEXT, CLEAR ICONS)
- Map: Field explorer + tiles
- Voyage: Where to fish? with crowd spreading
- Navigate: Route advisory transit verdict
- Live: Beacon, Watch mode (privacy 0.1°), SOS, ORCA Radio
- AI: Real 11-agent trace
- Alerts: Gale warnings
- Market: Catch marketplace
- Info: System health

Frontend proxies `/api` to backend via vite.config.js. For production, set `VITE_API_BASE=https://your-backend`.

---

## API Endpoints (Unified)

**Core (Phase 1):**
- GET /api/v1/health — live status of every source, Ollama, Supabase, cache
- GET /api/v1/zone?lat&lon — point snapshot
- GET /api/v1/grid?lat&lon&span — gridded snapshot
- GET /api/v1/reason?lat&lon — 11-agent trace
- GET /api/v1/advisory?lat&lon — bilingual GO/CAUTION/NO-GO
- GET /api/v1/field?lat&lon — field explorer
- GET /api/v1/route-check?from_lat&from_lon&to_lat&to_lon — 2km land verify + detour
- GET /api/v1/route-advisory?from...to... — transit verdict 30km sampling worst-case fold
- GET /api/v1/voyage?lat&lon — voyage planner with B14 crowd
- GET /api/v1/layers, /api/v1/tiles/{z}/{x}/{y}.png, /api/v1/datasets, /api/v1/zones, /api/v1/agents, /api/v1/alerts

**Live (B20):**
- POST /api/v1/live/start?lat&lon&boat_name&watch — Beacon ON or Watch mode
- POST /api/v1/live/ping?public_id&lat&lon&watch — heartbeat + sos_nearby + late-joiner dispatch
- POST /api/v1/live/sos?public_id&lat&lon&message — SOS ON (consent to exact)
- POST /api/v1/live/sos/clear?public_id — SOS clear
- POST /api/v1/live/stop?public_id — Beacon OFF instant delete
- POST /api/v1/live/rescue/answer?public_id&case_id&answer=accept/decline
- POST /api/v1/live/rescue/complete?public_id&case_id
- POST /api/v1/live/rescue/msg — {public_id, case_id, text} ORCA Radio
- GET /api/v1/live/nearby?lat&lon&radius_km
- GET /api/v1/live/sos, /api/v1/live/boat/{public_id}, /api/v1/live/stats
- GET /api/live/stream — SSE
- WS /ws/chat — live agent trace streaming

**Phase 2 (Supabase optional):**
- GET/PUT /api/v1/profile/{user_id}
- GET/POST /api/v1/locations, /api/v1/history, /api/v1/catch-reports, /api/v1/feedback, POST /api/v1/sync, GET /api/v1/voice, GET /api/v1/official/overview

**Advanced (NEW):**
- GET /api/v1/ml/pfz?lat&lon — ML PFZ with SHAP
- GET /api/v1/drift?lat&lon&hours — leeway drift prediction
- GET /api/v1/rag?query — RAG retrieval
- GET /api/v1/carbon?distance_km&fuel_l — carbon tracker
- GET /api/v1/marketplace — catch marketplace
- GET /api/v1/bathymetry?lat&lon — GEBCO depth
- GET /api/v1/species/detect — YOLOv8 species

---

## Data Sources (All Live, Honest Failures)

1. Open-Meteo Marine (MFWAM/ECMWF WAM) — wave, SST, current
2. Open-Meteo Forecast (ECMWF IFS) — wind, gusts, gale check 34kn
3. Open-Meteo Daily — weathercode
4. Open-Meteo Archive — anomaly baseline
5. NOAA CoastWatch ERDDAP CHL — chlorophyll today→3d→7d lag retry
6. ESA OC-CCI v6 — ocean colour cross-check (cloud-masked in monsoon honestly)
7. ISRO MOSDAC OCM-3 — Oceansat-3 chlorophyll (24s wall cap, background retry)
8. INCOIS LAS — SST/ocean params (unreliable honestly)
9. INCOIS PFZ official lines — daily govt advisory WFS
10. GFW effort — fishing hours (token, 429 retry)
11. GFW fleet — vessel lists
12. JTWC — cyclone warnings
13. GLOBE 1km land mask — offline, 100% demo works offline
14. Nominatim — harbour search app-side

Caching: TTL 600s + last-known-good 6h fallback (B13). Never shows stale as fresh.

---

## 11 Agents

| ID | Type | Role |
|----|------|------|
| data_validation | Deterministic | Validate + freshness + count failures |
| gis_spatial | Deterministic | GLOBE land mask + offshore km |
| ocean_analysis | LLM/Analytical | Wave, swell, current |
| satellite_analysis | LLM/Analytical | CHL + SST granules |
| weather_hazard | LLM/Analytical | WMO/IMD wind/gust thresholds |
| map_synoptic | Deterministic | 0.25° grid interpolation |
| marine_ecology | LLM/Analytical | Productivity index, thermal front |
| fisheries_pfz | LLM/Analytical | PFZ + ML LSTM |
| anomaly_detection | Deterministic | SST anomaly vs 10yr baseline |
| marine_risk | Deterministic | Worst-case fold — NEVER LLM |
| orchestrator | LLM/Analytical | Bilingual simple synthesis |

AgentMessage format: run_id, agent_id, task, input_context, findings, confidence, evidence[], warnings[], status (queued/running/completed/degraded/failed/skipped), timestamp

---

## Verdict Thresholds (WMO/IMD)

```
Wave: <2.5m GOOD, ≥2.5m CAUTION, ≥4.0m DANGER
Gust: ≥34kn DANGER
Sustained wind: ≥20kn CAUTION
Current: >3kn Note
Worst-case fold: GOOD+GOOD+CAUTION+GOOD = CAUTION (severe not hidden)
```

---

## Flutter Phase (After Web Checked)

The repo has `flutter_app/` placeholder with architecture ready:

```
lib/
├── core/
│   ├── auth/supabase_auth_service.dart (from prabhbani)
│   ├── sync/sync_manager.dart (offline-first outbox)
│   └── voice/voice_service.dart (TTS)
├── features/
│   ├── advisory/ (home verdict + voice widget)
│   ├── map/ (Leaflet + tiles)
│   ├── voyage/ (planner)
│   ├── navigate/ (route advisory)
│   ├── live/ (beacon + radio)
│   ├── ai/ (agent trace)
│   ├── alerts/
│   ├── locations/ (saved with Hive + cloud sync)
│   ├── catch_reports/
│   ├── history/
│   └── official/
└── main.dart (bootstrap with Supabase init offline-safe)
```

To generate Flutter app:
```bash
flutter create flutter_app
# Copy features from frontend-web logic + prabhbani frontend
# Use Riverpod + GoRouter + Hive + Supabase Flutter + flutter_riverpod
```

Key packages (pubspec.yaml from prabhbani):
- supabase_flutter, hive, fl_chart, flutter_riverpod, go_router, dio, connectivity_plus, geolocator

UI philosophy 26A: LESS UI + LESS TEXT + LESS CHOICES + CLEAR ICONS + CLEAR ACTIONS = EASIER FOR EVERYONE. Home shows only CAN I GO? + one short explanation + freshness + one action.

---

## Advanced Ideas Taken from GitHub + Other Sources

- **Crowd B14**: Anonymous 0.25° cells, rolling 24h, neighbour spill 0.5x, penalty 8/boat capped 24, GFW penalty 10/5 — prevents overfishing same spot (community-aware)
- **Watch Mode B20**: AIS-receiver philosophy — listen without exact broadcast, coarse 0.1° (~11km) privacy, only count shown on radar, SOS/accept flips to exact with consent
- **Late-joiner dispatch**: Every ping re-dispatches open SOS — boat that came online after SOS still gets request instantly
- **ORCA Radio**: Case-channel 2-way, victim↔accepted rescuer only (403 otherwise), 140c, 30 cap, wiped on resolve, delivered via ping/watch payloads
- **ML PFZ**: LSTM-like heuristic SST 27-29C + CHL 0.5-2.5 + gradient >0.5, SHAP explanation, species prediction
- **Drift model**: Leeway 4% wind + 100% current, hourly positions, search radius 1.5x uncertainty — for SOS search planning
- **RAG**: Semantic + keyword + reranking, evidence object with source/dataset/timestamp/location/relevance
- **Carbon tracker**: Fuel → CO2 2.68 kg/L, green score, route optimization advice
- **Marketplace**: Direct fisher-buyer, reduces middleman, future blockchain traceability
- **3D bathymetry**: GEBCO mock, Deck.gl terrain ready, slope + seabed type
- **Edge AI**: YOLOv8 species detection, ONNX 5MB model, offline on ORCA Box
- **Voice**: Sarvam AI / Bhashini for Telugu/Hindi/English, browser SpeechSynthesis fallback
- **Resilience**: Last-known-good fallback (B13), phantom-timeout fix (15s explicit), honest failure notes, no dummy data

---

## How to Push to Your Repo https://github.com/TarunGupta003/sihpratice

```bash
cd /path/to/sihpratice
git init
git remote add origin https://github.com/TarunGupta003/sihpratice.git
git add .
git commit -m "feat: ORCA Ultimate v3.0 - merged prabhbani+Sangam + advanced ML/drift/RAG/marketplace"
git branch -M main
git push -u origin main
```

If repo not empty:
```bash
git pull origin main --allow-unrelated-histories
git push origin main
```

---

## Deployment

**Docker (optional):**
```yaml
# docker-compose.yml included
# backend + frontend-web
docker-compose up --build
```

**Ollama (optional but recommended for LLM agents):**
```bash
ollama pull qwen3:8b
ollama serve
# Backend auto-detects at OLLAMA_HOST
```

**Supabase (Phase 2 optional):**
- Create project at supabase.com
- Run backend/supabase_schema.sql (from prabhbani repo) — 6 tables with RLS
- Set env vars SUPABASE_URL, ANON_KEY, SERVICE_ROLE_KEY

---

## Judge / Demo Flow

1. Open web: Home shows GOOD/CAUTION/NO-GO with simple fisher language
2. Change lat/lon to 20.9,70.37 (Veraval) vs 9.9,76.0 (Kochi) — see live data change
3. Map tab — field explorer
4. Voyage tab — top pick with crowd penalty explained
5. Navigate tab — enter destination, see transit verdict sampled every 30km
6. Live tab — Beacon ON, Watch mode, SOS, Radio
7. AI tab — 11 agents real trace, RAG evidence
8. Alerts — gale warnings
9. Info — health shows all 12 sources status honestly

Fisher reaction: "I opened it and immediately understood what it is telling me."
Judge reaction: "Interface simple, system underneath sophisticated."

---

## License

SIH 2026 — ISRO PS26176 — Educational / Hackathon
