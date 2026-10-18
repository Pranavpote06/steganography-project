import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .core.config import TEMP_DIR
from .api.routes_health import router as health_router
from .api.routes_stats import router as stats_router
from .api.routes_audio import router as audio_router
from .api.routes_video import router as video_router
from .api.routes_security import router as security_router

app = FastAPI(
    title="Audio & Video Steganography API",
    description="Cybersecurity Educational Steganography Platform - Secure LSB Embedding and AES-256-GCM Extraction",
    version="1.0.0"
)

# Enable CORS for frontend Vite development server and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(stats_router, prefix="/api", tags=["Statistics"])
app.include_router(audio_router, prefix="/api/audio", tags=["Audio Steganography"])
app.include_router(video_router, prefix="/api/video", tags=["Video Steganography"])
app.include_router(security_router, prefix="/api/security", tags=["Security & Biometrics"])

@app.get("/")
def root():
    return {
        "message": "Audio and Video Steganography API is active.",
        "documentation": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
