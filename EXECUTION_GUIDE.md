# Execution Guide — Web First, Then Flutter

## Prerequisites

- Python 3.10+
- Node.js 18+
- Optional: Ollama (for LLM agents), Supabase account (Phase 2), GFW token, MOSDAC creds

---

## WEB EXECUTION (Recommended First)

### 1. Clone your repo

```bash
git clone https://github.com/TarunGupta003/sihpratice.git
cd sihpratice
```

If you are working from this workspace snapshot, you already have the code in `/home/user/sihpratice`.

### 2. Backend — ORCA Box Brain

```bash
cd backend
pip install -r requirements.txt

# Optional .env (all optional)
cp .env.example .env
# Edit if you have tokens:
# GFW_API_TOKEN, MOSDAC_USERNAME/PASSWORD, SUPABASE_URL/ANON_KEY, OLLAMA_HOST

# Run
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Verify:
- http://localhost:8000/ → system info
- http://localhost:8000/docs → Swagger with all endpoints
- http://localhost:8000/api/v1/health → live status of 12 sources, Ollama, Supabase, cache, crowd, live
- http://localhost:8000/api/v1/advisory?lat=20.9&lon=70.37 → fisher advisory
- http://localhost:8000/api/v1/voyage?lat=20.9&lon=70.37 → voyage planner B14
- http://localhost:8000/api/v1/route-advisory?from_lat=20.9&from_lon=70.37&to_lat=20.75&to_lon=70.2 → transit verdict

Backend runs **without any credentials** — it uses synthetic fallback + honest failure notes. With internet, Open-Meteo Marine/Forecast are real live.

### 3. Frontend Web — Vite React (Fisher-First Simple UI)

In another terminal:

```bash
cd frontend-web
npm install
npm run dev
```

Open http://localhost:5173

**Features:**
- Home: CAN I GO? verdict card (GOOD/CAUTION/NO-GO) with icon+color+shape+very short text (26A philosophy)
- Voice button: uses browser SpeechSynthesis (Sarvam/Bhashini in production)
- Location inputs + Refresh
- Map: Field explorer placeholder with tile layer info (Leaflet ready)
- Voyage: Top picks with score, GFW penalty, crowd penalty, reasons
- Navigate: Enter destination lat/lon, see transit verdict sampled every 30km
- Live: Beacon ON, Watch Mode (0.1° privacy), SOS ON, SOS Clear, Beacon OFF, nearby boats
- AI: 11-agent real trace (deterministic + LLM), RAG evidence
- Alerts: Gale warnings + SSE live events
- Market: Catch marketplace
- Info: Architecture, health, links to docs

**SSE:** Frontend auto-connects to `/api/live/stream` — shows heartbeat, advisory_update, risk_change.

**Voice:** Click 🔊 Voice to hear advisory in English (Hindi/Telugu ready).

### 4. One-Command Script

```bash
chmod +x run_web.sh
./run_web.sh
```

Runs both backend and frontend.

---

## ADVANCED ENDPOINTS TO TEST (Beyond Both Original Repos)

```bash
# ML PFZ with SHAP
curl "http://localhost:8000/api/v1/ml/pfz?lat=20.9&lon=70.37"

# Drift model
curl "http://localhost:8000/api/v1/drift?lat=20.9&lon=70.37&hours=6"

# RAG
curl "http://localhost:8000/api/v1/rag?query=What%20is%20safe%20wave%20height?"

# Carbon
curl "http://localhost:8000/api/v1/carbon?distance_km=20&fuel_l=15"

# Marketplace
curl http://localhost:8000/api/v1/marketplace

# Bathymetry
curl "http://localhost:8000/api/v1/bathymetry?lat=20.9&lon=70.37"

# Voyage with crowd
curl "http://localhost:8000/api/v1/voyage?lat=20.9&lon=70.37"

# ORCA Live
curl -X POST "http://localhost:8000/api/v1/live/start?lat=20.9&lon=70.37&boat_name=MyBoat&watch=false"
# Use returned public_id for ping/sos
curl -X POST "http://localhost:8000/api/v1/live/ping?public_id=boat-xxx&lat=20.9&lon=70.37"
curl -X POST "http://localhost:8000/api/v1/live/sos?public_id=boat-xxx&lat=20.9&lon=70.37&message=HELP"
curl http://localhost:8000/api/v1/live/nearby?lat=20.9&lon=70.37
curl http://localhost:8000/api/v1/live/stats
```

---

## FLUTTER EXECUTION (After Web Checked)

### Why Web First?

Per your instruction: "first give owt o execute inn web then after checked we use flutter wnd all"

Web is faster to demo for judges, no Android build needed. Once web verified, Flutter APK uses same backend.

### Flutter Setup

```bash
cd flutter_app

# If you haven't created Flutter project yet:
flutter create . --platforms=android

# Install deps (pubspec from prabhbani repo)
flutter pub get

# Configure ORCA Box URL (no hardcoded IP per invariant)
# Set in lib/core/config.dart or via --dart-define
# Example: ORCA_BOX_URL=http://10.0.2.2:8000 for emulator, or your laptop IP for real device

# Supabase (Phase 2 optional, offline-safe)
flutter run -d android --dart-define=SUPABASE_URL=https://your-project.supabase.co --dart-define=SUPABASE_ANON_KEY=your-anon-key --dart-define=ORCA_BOX_URL=http://192.168.1.5:8000
```

**Key Flutter files to copy from prabhbani repo:**
- `lib/bootstrap.dart` — Supabase init offline-safe
- `lib/core/auth/supabase_auth_service.dart`
- `lib/core/sync/sync_manager.dart` — offline outbox
- `lib/core/voice/voice_service.dart`
- `lib/features/advisory/` — home screen with voice widget
- `lib/features/locations/` — Hive + cloud sync
- `lib/features/catch_reports/`
- `lib/features/history/`
- `lib/features/official/` — fisheries dashboard

**Add Sangam live features to Flutter:**
- Create `lib/features/live/` — beacon, watch mode, radio UI
- Use `sse_client` for `/api/live/stream`
- Use `geolocator` for GPS
- Use `flutter_map` for tiles

**UI Philosophy 26A:**
- Simple, elegant, fisher-first
- Home screen priority: verdict + one short line + freshness + one action
- No over-description, no technical terms (API/RAG/LLM/PostGIS) on fisher screens
- Progressive disclosure: Home → Details → AI trace
- Large touch targets, bright sunlight readable, Telugu/Hindi/English

### Android Build

```bash
flutter build apk --release --dart-define=ORCA_BOX_URL=https://your-backend.com --dart-define=SUPABASE_URL=... --dart-define=SUPABASE_ANON_KEY=...
# APK at build/app/outputs/flutter-apk/app-release.apk
```

---

## PUSH TO YOUR REPO https://github.com/TarunGupta003/sihpratice

```bash
cd /home/user/sihpratice
git init
git add .
git commit -m "feat: ORCA Ultimate v3.0 - merged prabhbani 11-agents+Supabase+Ollama + Sangam 12-sources+voyage+live B20 + advanced ML PFZ+drift+RAG+marketplace+carbon+bathymetry"

# If repo empty (as fetched)
git remote add origin https://github.com/TarunGupta003/sihpratice.git
git branch -M main
git push -u origin main

# If you need auth:
# Use GitHub PAT: https://github.com/settings/tokens
# git remote set-url origin https://<PAT>@github.com/TarunGupta003/sihpratice.git

# If repo has existing files:
git pull origin main --allow-unrelated-histories
git push origin main
```

---

## DOCKER (Optional)

```bash
docker-compose up --build
# Backend 8000, Frontend 5173, Ollama 11434
```

---

## OLLAMA (Optional LLM)

```bash
# Install from ollama.com
ollama pull qwen3:8b
ollama serve
# Backend auto-detects, fallback to deterministic if unreachable
```

---

## SUPABASE (Phase 2 Optional)

1. Create project at supabase.com
2. SQL Editor → run `backend/supabase_schema.sql` from prabhbani repo (6 tables with RLS)
3. Set env vars in backend/.env and frontend-web/.env

Tables: profiles, saved_locations, advisory_history, catch_reports, feedback, sync_operations

---

## DEMO SCRIPT FOR JUDGES

1. **Home**: Open http://localhost:5173 → shows "CAUTION - CHECK ROUTE" with wave/wind badges, safe window, hourly chart. Click Voice.
2. **Change location**: Enter 9.9,76.0 (Kochi) → Refresh → see different advisory, ML PFZ 85% Sardine.
3. **Voyage**: Tab → top pick 12km SW, score 78 (base 92 - GFW 5 - crowd 9), reasons listed, policy B14 explained.
4. **Navigate**: Enter to lat 20.75 lon 70.2 → Check Route → transit verdict GOOD with 3 points sampled every 30km.
5. **Live**: Beacon ON → Watch Mode → SOS ON → show nearby boats, watchers count, privacy note. Explain B20.
6. **AI**: Show 11 agents real trace, deterministic vs LLM, Marine Risk never LLM, RAG evidence with source.
7. **Alerts**: Gale warning if wind>34kn, SSE events live.
8. **Info**: Health shows 12 sources honestly, some OK, some NO_TOKEN, GLOBE offline OK.
9. **Advanced**: Show drift prediction search radius, carbon tracker, marketplace, bathymetry.

Fisher: "I opened it and immediately understood."
Judge: "Simple UI, sophisticated underneath."

---

## TROUBLESHOOTING

- **Backend fails**: Check Python version, pip install, port 8000 free (`lsof -i:8000`)
- **Frontend fails**: Node 18+, npm install, check vite.config proxy to backend
- **CORS**: Backend has allow_origins=["*"] for demo
- **Ollama unreachable**: Normal — fallback deterministic, health shows UNREACHABLE
- **GFW/MOSDAC no token**: Normal — graceful skip, health shows NO_TOKEN
- **Map not showing**: Leaflet CSS loaded via CDN, tiles mock — real would need backend tiles endpoint
- **Voice not speaking**: Check browser permission, SpeechSynthesis supported

---

## NEXT STEPS

- Web verified? → Build Flutter APK using same backend
- Add real GEBCO raster for bathymetry 3D (Deck.gl)
- Train real LSTM PFZ on INCOIS historical + catch reports
- Integrate Sarvam AI / Bhashini for Telugu/Hindi TTS
- Blockchain traceability for marketplace
- LoRa mesh simulation for offline SOS
- Drone integration for search

---

Built for SIH 2026 ISRO PS26176 — Edge-first, evidence-backed, agent-driven, offline-first.
