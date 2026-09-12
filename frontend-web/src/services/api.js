const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000';

export async function fetchAdvisory(lat, lon) {
  const r = await fetch(`${BASE}/api/v1/advisory?lat=${lat}&lon=${lon}`);
  if(!r.ok) throw new Error(await r.text());
  return r.json();
}
export async function fetchZone(lat, lon) {
  const r = await fetch(`${BASE}/api/v1/zone?lat=${lat}&lon=${lon}`);
  return r.json();
}
export async function fetchHealth() {
  const r = await fetch(`${BASE}/api/v1/health`);
  return r.json();
}
export async function fetchReason(lat, lon) {
  const r = await fetch(`${BASE}/api/v1/reason?lat=${lat}&lon=${lon}`);
  return r.json();
}
export async function fetchVoyage(lat, lon) {
  const r = await fetch(`${BASE}/api/v1/voyage?lat=${lat}&lon=${lon}`);
  return r.json();
}
export async function fetchRouteAdvisory(fromLat, fromLon, toLat, toLon) {
  const r = await fetch(`${BASE}/api/v1/route-advisory?from_lat=${fromLat}&from_lon=${fromLon}&to_lat=${toLat}&to_lon=${toLon}`);
  return r.json();
}
export async function fetchAlerts(lat, lon) {
  const r = await fetch(`${BASE}/api/v1/alerts?lat=${lat}&lon=${lon}`);
  return r.json();
}
export async function fetchLiveNearby(lat, lon) {
  const r = await fetch(`${BASE}/api/v1/live/nearby?lat=${lat}&lon=${lon}`);
  return r.json();
}
export async function fetchLiveStats() {
  const r = await fetch(`${BASE}/api/v1/live/stats`);
  return r.json();
}
export async function startBeacon(lat, lon, boatName, watch=false) {
  const r = await fetch(`${BASE}/api/v1/live/start?lat=${lat}&lon=${lon}&boat_name=${encodeURIComponent(boatName)}&watch=${watch}`, {method:'POST'});
  return r.json();
}
export async function pingBeacon(pid, lat, lon, watch=false) {
  const r = await fetch(`${BASE}/api/v1/live/ping?public_id=${pid}&lat=${lat}&lon=${lon}&watch=${watch}`, {method:'POST'});
  return r.json();
}
export async function sosOn(pid, lat, lon, msg) {
  const r = await fetch(`${BASE}/api/v1/live/sos?public_id=${pid}&lat=${lat}&lon=${lon}&message=${encodeURIComponent(msg)}`, {method:'POST'});
  return r.json();
}
export async function sosClear(pid) {
  const r = await fetch(`${BASE}/api/v1/live/sos/clear?public_id=${pid}`, {method:'POST'});
  return r.json();
}
export async function stopBeacon(pid) {
  const r = await fetch(`${BASE}/api/v1/live/stop?public_id=${pid}`, {method:'POST'});
  return r.json();
}
export async function rescueAnswer(pid, caseId, ans) {
  const r = await fetch(`${BASE}/api/v1/live/rescue/answer?public_id=${pid}&case_id=${caseId}&answer=${ans}`, {method:'POST'});
  return r.json();
}
export async function fetchMLPFZ(lat, lon) {
  const r = await fetch(`${BASE}/api/v1/ml/pfz?lat=${lat}&lon=${lon}`);
  return r.json();
}
export async function fetchDrift(lat, lon) {
  const r = await fetch(`${BASE}/api/v1/drift?lat=${lat}&lon=${lon}`);
  return r.json();
}
export async function fetchRAG(q) {
  const r = await fetch(`${BASE}/api/v1/rag?query=${encodeURIComponent(q)}`);
  return r.json();
}
export async function fetchMarketplace() {
  const r = await fetch(`${BASE}/api/v1/marketplace`);
  return r.json();
}
export async function fetchBathymetry(lat, lon) {
  const r = await fetch(`${BASE}/api/v1/bathymetry?lat=${lat}&lon=${lon}`);
  return r.json();
}
export { BASE };
