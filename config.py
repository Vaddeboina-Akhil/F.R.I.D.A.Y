class Config:
    ASSISTANT_NAME = "FRIDAY"
    WAKE_WORDS = ["friday", "edith"]
    OLLAMA_MODEL = "qwen2.5:7b"
    OLLAMA_URL = "http://localhost:11434/api/generate"
    VOICE_RATE = 175
    VOICE_VOLUME = 1.0
    MEMORY_PATH = "memory/memory.json"
    WORLD_MONITOR_URL = "https://www.worldmonitor.app/?lat=20.0000&lon=0.0000&zoom=1.57&view=mena&timeRange=7d&layers=conflicts,hotspots,sanctions,weather,outages,natural,iranAttacks"
