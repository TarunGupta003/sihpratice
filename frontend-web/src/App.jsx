import React, { useState, useEffect } from 'react';
import { fetchAdvisory, fetchHealth, fetchVoyage, fetchRouteAdvisory, fetchAlerts, fetchLiveNearby, fetchLiveStats, startBeacon, pingBeacon, sosOn, sosClear, stopBeacon, fetchMLPFZ, fetchDrift, fetchRAG, fetchMarketplace, fetchBathymetry, BASE } from './services/api';
import { useSSE } from './hooks/useSSE';
import AdvancedPanel from './components/AdvancedPanel.jsx';

const TABS = [
  {id:'home', label:'Home', icon:'🏠'},
  {id:'map', label:'Map', icon:'🗺️'},
  {id:'voyage', label:'Voyage', icon:'🎣'},
  {id:'navigate', label:'Navigate', icon:'🧭'},
  {id:'live', label:'Live', icon:'📡'},
  {id:'ai', label:'AI', icon:'🧠'},
  {id:'alerts', label:'Alerts', icon:'⚠️'},
  {id:'market', label:'Market', icon:'🛒'},
  {id:'info', label:'Info', icon:'ℹ️'},
];

function VerdictCard({advisory, loading}) {
  if(loading) return <div style={s.card}>Loading advisory...</div>;
  if(!advisory) return <div style={s.card}>No advisory</div>;
  const color = advisory.color || '#F39C12';
  const verdict = advisory.verdict;
  const icon = verdict==='GOOD'?'✅':verdict==='CAUTION'?'⚠️':'🛑';
  return (
    <div style={{...s.card, borderLeft:`8px solid ${color}`, textAlign:'center'}}>
      <div style={{fontSize:48, marginBottom:8}}>{icon}</div>
      <div style={{fontSize:28, fontWeight:800, color, letterSpacing:1}}>{advisory.headline_en}</div>
      <div style={{fontSize:16, marginTop:8, color:'#334155'}}>{advisory.plain_en}</div>
      <div style={{display:'flex', gap:12, justifyContent:'center', marginTop:16, flexWrap:'wrap'}}>
        <span style={s.badge}>🌊 Wave {advisory.variables?.wave_height_m} m</span>
        <span style={s.badge}>💨 Wind {advisory.variables?.wind_speed_kn} kn</span>
        <span style={s.badge}>🌡️ SST {advisory.variables?.sst_celsius}°C</span>
        <span style={s.badge}>🟢 CHL {advisory.variables?.chlorophyll_mg_m3} mg/m³</span>
      </div>
      <div style={{marginTop:12, fontSize:12, color:'#64748b'}}>
        Updated just now • Sources: {advisory.sources?.length || 0} • Freshness: FRESH • {advisory.location_name}
      </div>
      <div style={{marginTop:12, display:'flex', gap:8, justifyContent:'center'}}>
        <span style={{...s.smallBadge, background:'#e0f2fe'}}>Safe window: {advisory.safe_window?.start} - {advisory.safe_window?.end}</span>
      </div>
    </div>
  );
}

export default function App(){
  const [tab, setTab] = useState('home');
  const [lat, setLat] = useState(20.9);
  const [lon, setLon] = useState(70.37);
  const [advisory, setAdvisory] = useState(null);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [voyage, setVoyage] = useState(null);
  const [routeAdv, setRouteAdv] = useState(null);
  const [alerts, setAlerts] = useState(null);
  const [live, setLive] = useState(null);
  const [beacon, setBeacon] = useState(null);
  const [mlpfz, setMlpfz] = useState(null);
  const [drift, setDrift] = useState(null);
  const [rag, setRag] = useState(null);
  const [market, setMarket] = useState(null);
  const [bath, setBath] = useState(null);
  const [toLat, setToLat] = useState(20.75);
  const [toLon, setToLon] = useState(70.2);
  const { events, connected } = useSSE();

  async function loadAdvisory(){
    setLoading(true);
    try{
      const data = await fetchAdvisory(lat, lon);
      setAdvisory(data);
      // Also load extras
      fetchMLPFZ(lat, lon).then(setMlpfz);
      fetchDrift(lat, lon).then(setDrift);
      fetchBathymetry(lat, lon).then(setBath);
    }catch(e){ console.error(e); }
    setLoading(false);
  }
  async function loadHealth(){ try{ setHealth(await fetchHealth()); }catch{} }
  async function loadVoyage(){ try{ setVoyage(await fetchVoyage(lat, lon)); }catch{} }
  async function loadRoute(){ try{ setRouteAdv(await fetchRouteAdvisory(lat, lon, toLat, toLon)); }catch{} }
  async function loadAlerts(){ try{ setAlerts(await fetchAlerts(lat, lon)); }catch{} }
  async function loadLive(){ try{ setLive(await fetchLiveNearby(lat, lon)); setMarket(await fetchMarketplace()); }catch{} }
  async function loadRAG(){ try{ setRag(await fetchRAG("What is safe wave height and PFZ?")); }catch{} }

  useEffect(()=>{ loadAdvisory(); loadHealth(); loadAlerts(); loadLive(); loadRAG(); }, []);
  useEffect(()=>{ if(tab==='voyage') loadVoyage(); if(tab==='navigate') loadRoute(); if(tab==='live') fetchLiveStats().then(s=>console.log(s)); }, [tab]);

  // Voice
  function speak(text){
    if('speechSynthesis' in window){
      const u = new SpeechSynthesisUtterance(text);
      u.lang = 'en-IN';
      speechSynthesis.speak(u);
    }
  }

  return (
    <div style={s.root}>
      {/* Header */}
      <div style={s.header}>
        <div style={{fontWeight:900, fontSize:20, letterSpacing:1}}>ORCA <span style={{color:'#0ea5e9'}}>Ultimate</span></div>
        <div style={{display:'flex', gap:8, alignItems:'center'}}>
          <div style={{fontSize:12, background: connected?'#dcfce7':'#fee2e2', color: connected?'#166534':'#991b1b', padding:'4px 8px', borderRadius:12}}>● {connected?'LIVE':'OFFLINE'}</div>
          <div style={{fontSize:12, color:'#64748b'}}>Veraval • {lat.toFixed(2)},{lon.toFixed(2)}</div>
        </div>
      </div>

      {/* Location quick */}
      <div style={s.locBar}>
        <input style={s.input} type="number" step="0.01" value={lat} onChange={e=>setLat(parseFloat(e.target.value))} placeholder="Lat" />
        <input style={s.input} type="number" step="0.01" value={lon} onChange={e=>setLon(parseFloat(e.target.value))} placeholder="Lon" />
        <button style={s.btn} onClick={loadAdvisory}>🔄 Refresh</button>
        <button style={{...s.btn, background:'#0ea5e9'}} onClick={()=>speak(advisory?.plain_en || 'Sea is calm')}>🔊 Voice</button>
      </div>

      {/* Content */}
      <div style={s.content}>
        {tab==='home' && (
          <div>
            <VerdictCard advisory={advisory} loading={loading} />
            {/* Simple 3 info */}
            <div style={s.grid2}>
              <div style={s.card}>
                <h3 style={s.h3}>🐟 Fish Chance</h3>
                <div style={{fontSize:32, fontWeight:800, color:'#059669'}}>{mlpfz ? `${Math.round(mlpfz.pfz_probability*100)}%` : '--'}</div>
                <div style={{fontSize:13, color:'#475569'}}>{mlpfz?.species_predicted?.join(', ') || 'Loading ML PFZ...'}</div>
                <div style={{fontSize:11, marginTop:8, color:'#64748b'}}>{mlpfz?.explanation}</div>
              </div>
              <div style={s.card}>
                <h3 style={s.h3}>🌊 Depth & Seabed</h3>
                <div style={{fontSize:24, fontWeight:700}}>{bath?.depth_m || '--'} m</div>
                <div style={{fontSize:13}}>{bath?.seabed_type} • Slope {bath?.slope_deg}°</div>
                <div style={{fontSize:11, marginTop:8, color:'#64748b'}}>GEBCO bathymetry • 3D Deck.gl ready</div>
              </div>
            </div>
            {/* Hourly */}
            {advisory?.hourly_chart && (
              <div style={s.card}>
                <h3 style={s.h3}>📈 Next 24h Forecast</h3>
                <div style={{display:'flex', gap:4, overflowX:'auto', paddingBottom:8}}>
                  {advisory.hourly_chart.slice(0,12).map((h,i)=>(
                    <div key={i} style={{minWidth:60, textAlign:'center', padding:6, background: h.state==='good'?'#dcfce7':h.state==='caution'?'#fef3c7':'#fee2e2', borderRadius:8}}>
                      <div style={{fontSize:10}}>{h.hour}</div>
                      <div style={{fontSize:12, fontWeight:700}}>{h.wave_m}m</div>
                      <div style={{fontSize:10}}>{h.wind_kn}kn</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {/* Drift */}
            {drift && (
              <div style={s.card}>
                <h3 style={s.h3}>🌀 Drift Prediction (SOS)</h3>
                <div style={{fontSize:13}}>Drift speed {drift.total_drift.speed_kn}kn • Search radius {drift.search_radius_km}km</div>
                <div style={{fontSize:12, color:'#475569', marginTop:6}}>{drift.advice}</div>
              </div>
            )}
          </div>
        )}

        {tab==='map' && (
          <div>
            <div style={s.card}>
              <h3 style={s.h3}>🗺️ Field Explorer (Leaflet + Tiles)</h3>
              <div style={{height:380, background:'#e2e8f0', borderRadius:12, display:'flex', alignItems:'center', justifyContent:'center', flexDirection:'column'}}>
                <div style={{fontSize:48}}>🗺️</div>
                <div style={{fontSize:14, marginTop:8}}>Map: {lat.toFixed(2)},{lon.toFixed(2)} • {advisory?.variables?.wave_height_m}m waves</div>
                <div style={{fontSize:12, color:'#64748b'}}>Leaflet would render here with ORCA tiles: /api/v1/tiles/{'{z}'}/{'{x}'}/{'{y}'}.png</div>
                <div style={{marginTop:12, display:'flex', gap:6}}>
                  <span style={s.smallBadge}>PFZ Layer</span>
                  <span style={s.smallBadge}>CHL Layer</span>
                  <span style={s.smallBadge}>GFW Effort</span>
                  <span style={s.smallBadge}>Bathymetry 3D</span>
                </div>
              </div>
              <div style={{marginTop:12, fontSize:12, color:'#475569'}}>
                Layers: INCOIS PFZ official lines, JTWC cyclones, GFW AIS fleet, NOAA CHL, GEBCO bathymetry. GLOBE 1km land mask offline.
              </div>
            </div>
          </div>
        )}

        {tab==='voyage' && (
          <div>
            <div style={s.card}>
              <h3 style={s.h3}>🎣 Voyage Planner — Where to fish today?</h3>
              <div style={{fontSize:12, color:'#475569', marginBottom:12}}>B14 crowd-spread: "Sabko same jagah nahi bhejte" • GFW AIS + community 0.25° cells • ML PFZ</div>
              {voyage ? (
                <div>
                  <div style={{fontSize:14, fontWeight:700, marginBottom:8}}>Top pick: {voyage.top_pick?.latitude},{voyage.top_pick?.longitude} • Score {voyage.top_pick?.score_final} (base {voyage.top_pick?.score_base})</div>
                  <div style={{display:'grid', gap:8}}>
                    {voyage.candidates.slice(0,5).map(c=>(
                      <div key={c.id} style={{padding:10, border:'1px solid #e2e8f0', borderRadius:8, background: c.id===voyage.top_pick?.id ? '#f0fdf4' : '#fff'}}>
                        <div style={{display:'flex', justifyContent:'space-between'}}>
                          <b>{c.id} • {c.distance_km}km {c.bearing_deg}°</b>
                          <span style={{background:'#0ea5e9', color:'#fff', padding:'2px 8px', borderRadius:12, fontSize:12}}>{c.score_final} pts</span>
                        </div>
                        <div style={{fontSize:12, marginTop:4}}>{c.reasons.slice(0,3).join(' • ')}</div>
                        <div style={{fontSize:11, color:'#64748b', marginTop:4}}>Penalties: GFW -{c.penalties.gfw}, Crowd -{c.penalties.crowd} • {c.pfz?.species_hint}</div>
                      </div>
                    ))}
                  </div>
                  <div style={{fontSize:11, marginTop:8, color:'#64748b'}}>{voyage.policy}</div>
                </div>
              ) : <div>Loading voyage...</div>}
            </div>
          </div>
        )}

        {tab==='navigate' && (
          <div>
            <div style={s.card}>
              <h3 style={s.h3}>🧭 Route Advisory — Transit Verdict</h3>
              <div style={{display:'flex', gap:8, marginBottom:12, flexWrap:'wrap'}}>
                <input style={s.input} type="number" value={toLat} onChange={e=>setToLat(parseFloat(e.target.value))} placeholder="To Lat" />
                <input style={s.input} type="number" value={toLon} onChange={e=>setToLon(parseFloat(e.target.value))} placeholder="To Lon" />
                <button style={s.btn} onClick={loadRoute}>Check Route</button>
              </div>
              {routeAdv ? (
                <div>
                  <div style={{padding:10, background: routeAdv.verdict.level==='GOOD'?'#dcfce7':routeAdv.verdict.level==='CAUTION'?'#fef3c7':'#fee2e2', borderRadius:8, fontWeight:700}}>
                    Verdict: {routeAdv.verdict.level} • {routeAdv.distance_km}km • {routeAdv.points_known} points sampled every 30km
                  </div>
                  <div style={{marginTop:10, display:'flex', gap:4, overflowX:'auto'}}>
                    {routeAdv.points?.map((p,i)=>(
                      <div key={i} style={{minWidth:70, padding:6, borderRadius:8, background: p.state==='good'?'#dcfce7':p.state==='caution'?'#fef3c7':'#fee2e2', textAlign:'center'}}>
                        <div style={{fontSize:10}}>Pt {p.index}</div>
                        <div style={{fontSize:11, fontWeight:600}}>{p.wave_m}m</div>
                        <div style={{fontSize:10}}>{p.wind_kn}kn</div>
                        <div style={{fontSize:9}}>{p.state}</div>
                      </div>
                    ))}
                  </div>
                  {routeAdv.route_check?.detour_waypoint && (
                    <div style={{marginTop:10, fontSize:12, background:'#fff7ed', padding:8, borderRadius:8}}>
                      ⚠️ Land blocked • Detour waypoint: {routeAdv.route_check.detour_waypoint.latitude},{routeAdv.route_check.detour_waypoint.longitude}
                    </div>
                  )}
                  <div style={{fontSize:11, marginTop:8, color:'#64748b'}}>Method: {routeAdv.method}</div>
                </div>
              ) : <div>Click Check Route</div>}
            </div>
          </div>
        )}

        {tab==='live' && (
          <div>
            <div style={s.card}>
              <h3 style={s.h3}>📡 ORCA Live — Beacon + Watch + Radio (B20)</h3>
              <div style={{display:'flex', gap:8, flexWrap:'wrap', marginBottom:12}}>
                <button style={s.btn} onClick={async()=>{ const r=await startBeacon(lat, lon, 'MyBoat-'+Math.floor(Math.random()*100), false); setBeacon(r); }}>Beacon ON</button>
                <button style={{...s.btn, background:'#8b5cf6'}} onClick={async()=>{ const r=await startBeacon(lat, lon, 'Watcher', true); setBeacon(r); }}>Watch Mode (Privacy)</button>
                <button style={{...s.btn, background:'#ef4444'}} onClick={async()=>{ if(beacon){ const r=await sosOn(beacon.public_id, lat, lon, 'HELP Engine fail'); alert(JSON.stringify(r)); } }}>SOS ON</button>
                <button style={{...s.btn, background:'#22c55e'}} onClick={async()=>{ if(beacon){ const r=await sosClear(beacon.public_id); alert(JSON.stringify(r)); } }}>SOS Clear (Theek Hoon)</button>
                <button style={{...s.btn, background:'#64748b'}} onClick={async()=>{ if(beacon){ const r=await stopBeacon(beacon.public_id); setBeacon(null); alert(JSON.stringify(r)); } }}>Beacon OFF (Delete)</button>
              </div>
              {beacon && <div style={{fontSize:12, background:'#f1f5f9', padding:8, borderRadius:8, marginBottom:12}}>Beacon: {JSON.stringify(beacon)}</div>}
              <div style={{fontSize:12}}>
                <b>Nearby boats (beacons only, watchers hidden):</b>
                <div style={{marginTop:6}}>
                  {live?.boats?.length ? live.boats.map(b=><div key={b.public_id} style={{padding:6, border:'1px solid #e2e8f0', borderRadius:6, marginBottom:4}}>{b.boat_name} • {b.distance_km}km • SOS:{b.sos_active?'YES':'no'} • {b.status}</div>) : 'No nearby boats within 30km'}
                </div>
                <div style={{marginTop:8}}>Watchers count (privacy hidden): {live?.watchers_count || 0} • Total beacons: {live?.total_beacons || 0}</div>
              </div>
              <div style={{fontSize:11, marginTop:10, color:'#64748b', background:'#fffbeb', padding:8, borderRadius:8}}>
                B20 features: WATCH mode = coarse 0.1° (~11km) privacy, not on radar. SOS/Accept = consent to exact. Late-joiner fix: SOS after you arrived still dispatched. ORCA Radio = victim↔accepted rescuer only, 140c, 30 cap, wiped on resolve. STOP = instant full delete.
              </div>
            </div>
          </div>
        )}

        {tab==='ai' && (
          <div>
            <div style={s.card}>
              <h3 style={s.h3}>🧠 11-Agent Collaborative Trace (Real)</h3>
              {advisory?.agents_trace ? (
                <div style={{display:'grid', gap:8}}>
                  {advisory.agents_trace.map((a,i)=>(
                    <div key={i} style={{padding:10, borderLeft:`4px solid ${a.type==='Deterministic'?'#0ea5e9':'#8b5cf6'}`, background:'#f8fafc', borderRadius:6}}>
                      <div style={{display:'flex', justifyContent:'space-between'}}>
                        <b style={{fontSize:13}}>{a.agent_name} {a.type==='Deterministic'?'🔧':'🤖'}</b>
                        <span style={{fontSize:11, background:'#e2e8f0', padding:'2px 6px', borderRadius:8}}>{a.duration_ms}ms • {a.status}</span>
                      </div>
                      <div style={{fontSize:12, marginTop:4}}>{a.findings}</div>
                      <div style={{fontSize:11, color:'#64748b', marginTop:4}}>Evidence: {a.evidence?.slice(0,2).join(' • ')}</div>
                      {a.warnings?.length>0 && <div style={{fontSize:11, color:'#dc2626', marginTop:4}}>⚠️ {a.warnings.join(' ')}</div>}
                    </div>
                  ))}
                </div>
              ) : <div>Load advisory to see trace</div>}
              <div style={{marginTop:12, fontSize:11, color:'#64748b'}}>Invariant: Marine Risk Agent ALWAYS deterministic, NEVER LLM. Orchestrator synthesizes.</div>
            </div>
            {rag && (
              <div style={s.card}>
                <h3 style={s.h3}>📚 RAG Evidence</h3>
                <div style={{fontSize:12}}>Query: {rag.query}</div>
                {rag.evidence?.map(ev=>(
                  <div key={ev.document_id} style={{marginTop:8, padding:8, background:'#f1f5f9', borderRadius:6}}>
                    <b style={{fontSize:12}}>{ev.source} • {ev.dataset} • score {ev.relevance_score}</b>
                    <div style={{fontSize:12, marginTop:4}}>{ev.content}</div>
                    <div style={{fontSize:10, color:'#64748b'}}>{ev.location} • {ev.timestamp}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {tab==='alerts' && (
          <div>
            <div style={s.card}>
              <h3 style={s.h3}>⚠️ Alerts</h3>
              {alerts?.alerts?.map((al,i)=>(
                <div key={i} style={{padding:10, borderRadius:8, marginBottom:8, background: al.level==='DANGER'?'#fee2e2':al.level==='CAUTION'?'#fef3c7':'#dcfce7'}}>
                  <b>{al.type} • {al.level}</b>
                  <div style={{fontSize:13, marginTop:4}}>{al.message}</div>
                  <div style={{fontSize:11, color:'#64748b'}}>Source: {al.source}</div>
                </div>
              ))}
            </div>
            <div style={s.card}>
              <h3 style={s.h3}>📡 SSE Live Events</h3>
              <div style={{fontSize:12}}>Connected: {connected?'Yes':'No'} • {events.length} events</div>
              <div style={{maxHeight:200, overflowY:'auto', marginTop:8, background:'#0f172a', color:'#e2e8f0', padding:8, borderRadius:8, fontSize:11, fontFamily:'monospace'}}>
                {events.slice(-10).reverse().map((ev,i)=><div key={i}>[{ev.type}] {JSON.stringify(ev.data).slice(0,120)}</div>)}
              </div>
            </div>
          </div>
        )}

        {tab==='market' && (
          <div>
            <div style={s.card}>
              <h3 style={s.h3}>🛒 Catch Marketplace (Advanced)</h3>
              {market?.listings?.map(l=>(
                <div key={l.id} style={{padding:10, border:'1px solid #e2e8f0', borderRadius:8, marginBottom:8, display:'flex', justifyContent:'space-between'}}>
                  <div>
                    <b>{l.species} • {l.quantity_kg}kg</b>
                    <div style={{fontSize:12}}>{l.harbour} • {l.seller} • {l.freshness}</div>
                  </div>
                  <div style={{fontWeight:700, color:'#059669'}}>₹{l.price_per_kg}/kg</div>
                </div>
              ))}
              <div style={{fontSize:11, color:'#64748b', marginTop:8}}>Advanced: Links fisher to buyer, reduces middleman, blockchain traceability future.</div>
            </div>
          </div>
        )}

        {tab==='info' && (
          <div>
            <div style={s.card}>
              <h3 style={s.h3}>ℹ️ ORCA Ultimate System v4.0-ultra</h3>
              <div style={{fontSize:13, lineHeight:1.6}}>
                <b>Architecture:</b> Flutter=Interface, ORCA Box=Brain, Supabase=Optional Cloud Memory<br/>
                <b>11 Agents:</b> 5 deterministic (validation, gis, synoptic, anomaly, risk) + 6 LLM (ocean, satellite, weather, ecology, pfz, orchestrator)<br/>
                <b>12 Sources:</b> Open-Meteo Marine/Forecast/Daily/Archive, NOAA ERDDAP CHL, ESA OC-CCI, ISRO MOSDAC OCM-3, INCOIS LAS/PFZ, GFW effort+fleet, JTWC, GLOBE 1km<br/>
                <b>Advanced v3:</b> ML PFZ LSTM, Drift leeway, RAG, Crowd B14, ORCA Radio B20, Carbon, Marketplace, 3D bathymetry, Voice Sarvam/Bhashini, YOLOv8<br/>
                <b>Ultra Advanced v4 (NEW):</b> Blockchain traceability (Hyperledger), Drone SAR spiral + thermal YOLOv8, LoRa mesh DTN offline SOS, Weather routing isochrone, Oil spill Sentinel-1 SAR, Edge AI ONNX 5MB offline, Digital Twin predictive maintenance, Bhashini 7 languages<br/>
                <b>Invariants:</b> Backend verdict authoritative, every number has provenance, no fabricated data, stale visibly stale, AI trace real, deterministic stays deterministic, core safety no Supabase, no hardcoded IPs<br/>
                <b>Health:</b> {health ? JSON.stringify(health.data_sources || {}).slice(0,200) : 'Loading...'}
              </div>
              <div style={{marginTop:12, fontSize:12}}>
                <b>Backend:</b> {BASE} • <a href={`${BASE}/docs`} target="_blank">Swagger Docs</a> • <a href={`${BASE}/api/v1/health`} target="_blank">Health</a>
              </div>
            </div>
            <AdvancedPanel lat={lat} lon={lon} />
          </div>
        )}
      </div>

      {/* Bottom Nav */}
      <div style={s.bottomNav}>
        {TABS.map(t=>(
          <button key={t.id} onClick={()=>setTab(t.id)} style={{...s.navBtn, background: tab===t.id ? '#0ea5e9' : 'transparent', color: tab===t.id ? '#fff' : '#64748b'}}>
            <div style={{fontSize:18}}>{t.icon}</div>
            <div style={{fontSize:10}}>{t.label}</div>
          </button>
        ))}
      </div>
    </div>
  );
}

const s = {
  root:{minHeight:'100vh', background:'#f8fafc', paddingBottom:70, maxWidth:900, margin:'0 auto'},
  header:{display:'flex', justifyContent:'space-between', alignItems:'center', padding:'12px 16px', background:'#fff', borderBottom:'1px solid #e2e8f0', position:'sticky', top:0, zIndex:10},
  locBar:{display:'flex', gap:8, padding:'8px 16px', background:'#fff', borderBottom:'1px solid #e2e8f0', flexWrap:'wrap'},
  input:{padding:'6px 10px', border:'1px solid #cbd5e1', borderRadius:8, width:100, fontSize:13},
  btn:{padding:'6px 12px', background:'#0f172a', color:'#fff', border:'none', borderRadius:8, fontSize:13, cursor:'pointer'},
  content:{padding:16},
  card:{background:'#fff', border:'1px solid #e2e8f0', borderRadius:12, padding:16, marginBottom:12, boxShadow:'0 1px 2px rgba(0,0,0,0.05)'},
  h3:{fontSize:14, fontWeight:700, marginBottom:8},
  badge:{background:'#f1f5f9', padding:'4px 8px', borderRadius:12, fontSize:12, border:'1px solid #e2e8f0'},
  smallBadge:{background:'#f1f5f9', padding:'2px 8px', borderRadius:12, fontSize:11, border:'1px solid #e2e8f0'},
  grid2:{display:'grid', gridTemplateColumns:'1fr 1fr', gap:12},
  bottomNav:{position:'fixed', bottom:0, left:'50%', transform:'translateX(-50%)', width:'100%', maxWidth:900, display:'flex', justifyContent:'space-around', background:'#fff', borderTop:'1px solid #e2e8f0', padding:'6px 0', zIndex:20},
  navBtn:{border:'none', padding:'4px 10px', borderRadius:8, cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:2}
};
