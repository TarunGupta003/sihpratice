"""
ORCA Ultimate - Ollama Client
Thin httpx client for Qwen3:8b local LLM with graceful fallback
"""
import os
import httpx
from typing import Dict, Any, Optional

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
OLLAMA_TIMEOUT = float(os.getenv("OLLAMA_TIMEOUT_S", "12"))

class OllamaClient:
    def __init__(self, host=OLLAMA_HOST, model=OLLAMA_MODEL, timeout=OLLAMA_TIMEOUT):
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout

    def health(self) -> Dict[str, Any]:
        try:
            with httpx.Client(timeout=3) as client:
                r = client.get(f"{self.host}/api/tags")
                if r.status_code == 200:
                    tags = r.json()
                    models = [m.get("name","") for m in tags.get("models",[])]
                    has_model = any(self.model in m for m in models) or len(models)>0
                    return {
                        "status": "OK" if has_model else "MODEL_NOT_FOUND",
                        "host": self.host,
                        "model": self.model,
                        "models_available": models[:5],
                        "timeout_s": self.timeout
                    }
                else:
                    return {"status": f"HTTP_{r.status_code}", "host": self.host}
        except Exception as e:
            return {"status": f"UNREACHABLE: {type(e).__name__}: {str(e)[:80]}", "host": self.host, "model": self.model, "fallback": "Deterministic agents will be used"}

    def generate(self, prompt: str, timeout: Optional[float]=None) -> Dict[str, Any]:
        t = timeout or self.timeout
        try:
            with httpx.Client(timeout=t) as client:
                r = client.post(f"{self.host}/api/generate", json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 200}
                })
                if r.status_code == 200:
                    data = r.json()
                    return {"response": data.get("response",""), "model": self.model}
                else:
                    return {"response": "", "error": f"HTTP {r.status_code}"}
        except Exception as e:
            return {"response": "", "error": f"{type(e).__name__}: {e}"}

ollama = OllamaClient()
