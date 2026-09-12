# Advanced Features Beyond Both Repos

## 1. ML PFZ Predictor
- Model: LSTM-like heuristic trained on 5yr INCOIS+NOAA+catch
- Inputs: SST, CHL, SST gradient
- Outputs: PFZ probability, species, confidence, SHAP explanation
- Endpoint: /api/v1/ml/pfz?lat&lon
- Future: Real ONNX model with 15 arc-sec GEBCO + OCM-3

## 2. Drift Model (Leeway)
- For SOS: predicts where disabled boat drifts
- Formula: 4% wind + 100% current (empirical small boat)
- Hourly positions + search radius 1.5x uncertainty
- Endpoint: /api/v1/drift?lat&lon&hours

## 3. Crowd Engine B14
- Problem: "sabko same jagah mat bhejo" — all boats same #1 spot → stock pressure
- Solution: Anonymous 0.25° cells, 24h window, neighbour 0.5x, penalty 8/boat capped 24, GFW penalty 10/5
- Privacy: No identity, no exact coords, atomic JSON
- Endpoint: integrated in /api/v1/voyage

## 4. ORCA Live B20
- Beacon ON/OFF anonymous AIS-style
- Watch mode: watch=true, coarse 0.1° (~11km) privacy, not on radar, only count
- Late-joiner: every ping re-dispatches open SOS
- ORCA Radio: case-channel victim↔accepted rescuer only (403 else), 140c, 30 cap, wiped on resolve
- Privacy: STOP = instant full delete, SOS/accept = consent to exact

## 5. RAG Evidence
- Knowledge base: INCOIS, WMO, NOAA, MOSDAC, GLOBE, Ecology, GFW, JTWC
- Retrieval: keyword + semantic + reranking
- Evidence object: source, dataset, timestamp, location, relevance score
- Endpoint: /api/v1/rag?query

## 6. Carbon Tracker
- Diesel 2.68 kg CO2/L
- Green score 0-100
- Advice: optimize via route-advisory

## 7. Marketplace
- Direct fisher-buyer, reduces middleman
- Future: blockchain catch traceability (Hyperledger)

## 8. 3D Bathymetry
- GEBCO mock, depth, slope, seabed type
- Frontend: Deck.gl terrain

## 9. YOLOv8 Species Detection
- ONNX 5MB model, edge inference on ORCA Box
- Supported: Mackerel, Sardine, Pomfret, Tuna, Bombay Duck, Seer Fish

## 10. Voice (Sarvam/Bhashini)
- Telugu/Hindi/English TTS
- Browser SpeechSynthesis fallback for web demo

## 11. Last-Known-Good Fallback B13
- TTL cache + separate long-lived last-good store
- 6h expiry, non-mutation, clear wipes stale
- Honest: "...cached Nm old" tag, never fresh as current

## 12. Honest Failure Reporting
- Every source failure named: cloud-masked, timeout, rate-limit, no token
- Validation agent counts 3/7 sources OK
- UI shows reason, never invents values
