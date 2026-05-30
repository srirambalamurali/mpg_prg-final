from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from pydantic import BaseModel, Field

MODEL_PATH = Path(__file__).resolve().parents[1] / "models" / "model.pkl"


class VehicleRequest(BaseModel):
    car_name: str = Field(..., examples=["ford torino"])
    cylinders: int = Field(..., ge=3, le=12)
    displacement: float = Field(..., gt=0)
    horsepower: float = Field(..., gt=0)
    weight: float = Field(..., gt=0)
    acceleration: float = Field(..., gt=0)
    model_year: int = Field(..., ge=0, le=99)
    origin: int = Field(..., ge=1, le=3)


class VehiclePrediction(BaseModel):
    predicted_mpg: float
    efficiency_band: str
    brand: str
    performance_metrics: dict[str, float]


class ModelPredictor:
    def __init__(self, model_path: Path = MODEL_PATH) -> None:
        self.model_path = model_path
        self.model = self._load_model()
        self.feature_names = list(getattr(self.model, "feature_names_in_", []))
        if not self.feature_names:
            raise RuntimeError("The saved model does not expose feature_names_in_.")

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_model() -> Any:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
        return joblib.load(MODEL_PATH)

    @staticmethod
    def _extract_brand(car_name: str) -> str:
        normalized = car_name.strip().lower()
        if not normalized:
            raise ValueError("car_name cannot be empty.")
        token = re.split(r"\s+", normalized)[0]
        token = re.sub(r"[^a-z0-9\-]+", "", token)
        return token

    def _build_features(self, payload: VehicleRequest) -> pd.DataFrame:
        row = dict.fromkeys(self.feature_names, 0)
        brand = self._extract_brand(payload.car_name)
        brand_column = f"brand_{brand}"
        origin_column = f"origin_{payload.origin}"

        numeric_values = {
            "cylinders": float(payload.cylinders),
            "displacement": float(payload.displacement),
            "horsepower": float(payload.horsepower),
            "weight": float(payload.weight),
            "acceleration": float(payload.acceleration),
            "model_year": float(payload.model_year),
        }

        for key, value in numeric_values.items():
            if key in row:
                row[key] = value

        if brand_column in row:
            row[brand_column] = 1
        if origin_column in row:
            row[origin_column] = 1

        return pd.DataFrame([row], columns=self.feature_names)

    @staticmethod
    def _efficiency_band(predicted_mpg: float) -> str:
        if predicted_mpg >= 30:
            return "Efficient"
        if predicted_mpg >= 22:
            return "Balanced"
        return "Performance"

    def predict(self, payload: VehicleRequest) -> VehiclePrediction:
        features = self._build_features(payload)
        predicted_mpg = float(self.model.predict(features)[0])
        horsepower = max(float(payload.horsepower), 1.0)
        weight = max(float(payload.weight), 1.0)

        performance_metrics = {
            "horsepower_to_weight": round(horsepower / weight, 6),
            "weight_per_horsepower": round(weight / horsepower, 6),
            "acceleration": float(payload.acceleration),
        }

        return VehiclePrediction(
            predicted_mpg=round(predicted_mpg, 2),
            efficiency_band=self._efficiency_band(predicted_mpg),
            brand=self._extract_brand(payload.car_name),
            performance_metrics=performance_metrics,
        )
