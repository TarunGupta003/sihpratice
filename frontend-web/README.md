# ORCA Ultimate Web Frontend

Vite + React fisher-first simple UI.

## Run

```bash
npm install
npm run dev
# http://localhost:5173
```

Backend must run at http://localhost:8000 (proxied via vite.config.js).

Set custom backend:
```bash
VITE_API_BASE=http://192.168.1.5:8000 npm run dev
```

## Structure

- src/services/api.js — all backend calls
- src/hooks/useSSE.js — SSE live stream
- src/App.jsx — 9 tabs: Home, Map, Voyage, Navigate, Live, AI, Alerts, Market, Info
- Simple inline styles for elegance, no heavy UI libs (per 26A: LESS UI)

## Build

```bash
npm run build
npm run preview
```
