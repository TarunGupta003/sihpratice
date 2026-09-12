# Flutter App — Phase 2 (After Web Checked)

This folder is placeholder for Flutter Android APK.

Architecture from prabhbani/ORCA-SIH-2026 frontend + Sangam live features.

## Structure to generate

```bash
flutter create .
```

Then implement:

```
lib/
├── bootstrap.dart — Supabase init from compile-time env vars (offline-safe)
├── core/
│   ├── auth/supabase_auth_service.dart
│   ├── sync/sync_manager.dart — offline-first outbox queue
│   ├── voice/voice_service.dart — TTS voice advisory
│   └── network/dio_client.dart
├── features/
│   ├── advisory/
│   │   ├── presentation/home_screen.dart — CAN I GO? simple UI
│   │   ├── application/advisory_provider.dart (Riverpod AsyncNotifier)
│   │   ├── domain/usecases/get_current_advisory.dart
│   │   └── data/orca_box_advisory_repository.dart
│   ├── map/
│   ├── voyage/ — voyage planner with crowd
│   ├── navigate/ — route advisory
│   ├── live/ — beacon, watch, radio
│   ├── ai/ — agent trace real
│   ├── alerts/
│   ├── locations/ — Hive + cloud sync
│   ├── catch_reports/
│   ├── history/
│   ├── official/ — fisheries dashboard
│   └── auth/profile
└── main.dart
```

## Packages (pubspec.yaml)

```yaml
dependencies:
  flutter_riverpod: ^2.4.0
  go_router: ^12.0.0
  hive: ^2.2.3
  hive_flutter: ^1.1.0
  supabase_flutter: ^2.0.0
  dio: ^5.4.0
  fl_chart: ^0.65.0
  flutter_map: ^6.0.0
  latlong2: ^0.8.1
  geolocator: ^10.0.0
  connectivity_plus: ^5.0.0
  flutter_tts: ^4.0.0
  sse_client: ^0.1.0
```

## UI Philosophy 26A

- Simple, elegant, fisher-first
- LESS UI + LESS TEXT + LESS CHOICES + CLEAR ICONS
- Home: verdict + one short line + freshness + one action
- No API/RAG/LLM/PostGIS terms on fisher screens
- Progressive disclosure: simple → details → AI trace

## Execution

```bash
cd flutter_app
flutter pub get
flutter run -d android --dart-define=SUPABASE_URL=... --dart-define=SUPABASE_ANON_KEY=...
# ORCA Box base URL configurable in app (no hardcoded IP)
```

Backend remains authoritative for safety verdict.
