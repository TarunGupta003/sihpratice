import React, { useState } from 'react';
import { BASE } from '../services/api';

export default function AdvancedPanel({ lat, lon }){
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  async function call(path){
    setLoading(true);
    try{
      const r = await fetch(`${BASE}${path}`);
      const j = await r.json();
      setData(j);
    }catch(e){ setData({error: String(e)}); }
    setLoading(false);
  }

  return (
    <div style={{background:'#fff', border:'1px solid #e2e8f0', borderRadius:12, padding:16, marginTop:12}}>
      <h3 style={{fontSize:14, fontWeight:700, marginBottom:8}}>🚀 Ultra Advanced — Beyond Both Repos</h3>
      <div style={{display:'flex', gap:6, flexWrap:'wrap', marginBottom:12}}>
        <button onClick={()=>call(`/api/v1/blockchain/chain`)} style={btn}>⛓️ Blockchain Chain</button>
        <button onClick={()=>call(`/api/v1/drone/search?last_lat=${lat}&last_lon=${lon}&drift_lat=${lat+0.02}&drift_lon=${lon+0.02}`)} style={btn}>🚁 Drone SAR</button>
        <button onClick={()=>call(`/api/v1/lora/propagate?lat=${lat}&lon=${lon}&message=SOS`)} style={btn}>📡 LoRa Mesh</button>
        <button onClick={()=>call(`/api/v1/routing/weather?from_lat=${lat}&from_lon=${lon}&to_lat=${lat+0.2}&to_lon=${lon+0.2}`)} style={btn}>🧭 Weather Routing</button>
        <button onClick={()=>call(`/api/v1/sar/oil-spill?lat=${lat}&lon=${lon}`)} style={btn}>🛢️ Oil Spill SAR</button>
        <button onClick={()=>call(`/api/v1/edge/models`)} style={btn}>🤖 Edge AI ONNX</button>
        <button onClick={()=>call(`/api/v1/bhashini/tts?text=Good to go, sea is calm&lang=hi`)} style={btn}>🔊 Bhashini Hindi TTS</button>
        <button onClick={()=>call(`/api/v1/digital-twin/boat-123?lat=${lat}&lon=${lon}`)} style={btn}>🚤 Digital Twin</button>
        <button onClick={()=>call(`/api/v1/bathymetry?lat=${lat}&lon=${lon}`)} style={btn}>🌊 Bathymetry 3D</button>
      </div>
      {loading && <div style={{fontSize:12}}>Loading...</div>}
      {data && <pre style={{background:'#0f172a', color:'#e2e8f0', padding:10, borderRadius:8, fontSize:11, maxHeight:300, overflow:'auto'}}>{JSON.stringify(data, null, 2).slice(0,3000)}</pre>}
      <div style={{fontSize:11, color:'#64748b', marginTop:8}}>
        These endpoints are NEW — not in prabhbani nor Sangam repos. Blockchain traceability, drone SAR spiral search, LoRa mesh DTN offline SOS, weather routing isochrone fuel optimization, Sentinel-1 oil spill SAR, Edge AI ONNX 5MB offline, Bhashini Telugu/Hindi/Gujarati TTS, digital twin predictive maintenance.
      </div>
    </div>
  );
}
const btn = {padding:'6px 10px', background:'#0f172a', color:'#fff', border:'none', borderRadius:8, fontSize:12, cursor:'pointer'};
