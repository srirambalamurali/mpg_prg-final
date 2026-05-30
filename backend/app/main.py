from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.app.services.predictor import ModelPredictor, VehicleRequest

app = FastAPI(
    title="Auto MPG Predictor",
    version="1.0.0",
    description="FastAPI service for predicting vehicle fuel efficiency.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

predictor = ModelPredictor()


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "model": "loaded"}


@app.post("/api/predict", responses={400: {"description": "Invalid vehicle payload"}})
def predict(payload: VehicleRequest):
    try:
        prediction = predictor.predict(payload)
        return {
            "predicted_mpg": prediction.predicted_mpg,
            "efficiency_band": prediction.efficiency_band,
            "brand": prediction.brand,
            "performance_metrics": prediction.performance_metrics,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# Mount the static frontend so the API and UI share the same origin.
frontend_dir = Path(__file__).resolve().parents[2] / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
