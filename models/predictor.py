from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


@dataclass
class TrafficPredictor:
    """Placeholder predictor for future XGBoost/Random Forest model integration."""

    model_path: str | None = None

    def load_model(self) -> None:
        """Placeholder for loading serialized ML models."""
        return None

    def _congestion_from_features(self, hour: int, rainfall_mm: float) -> tuple[str, float]:
        score = min(1.0, max(0.0, (hour / 24.0) * 0.6 + min(rainfall_mm, 40) / 40.0 * 0.4))
        if score < 0.34:
            level = "Low"
        elif score < 0.67:
            level = "Moderate"
        else:
            level = "Severe"
        return level, round(score, 3)

    def predict(self, segment_ids: list[str], timestamp: str, weather: dict[str, Any]) -> list[dict[str, Any]]:
        rainfall_mm = float(weather.get("rainfall_mm", 0) or 0)
        hour = pd.to_datetime(timestamp, errors="coerce")
        hour_value = int(hour.hour) if not pd.isna(hour) else 12

        predictions: list[dict[str, Any]] = []
        for segment_id in segment_ids:
            level, risk = self._congestion_from_features(hour_value, rainfall_mm)
            predictions.append(
                {
                    "segment_id": segment_id,
                    "congestion_level": level,
                    "bottleneck_risk_score": float(np.clip(risk, 0.0, 1.0)),
                }
            )
        return predictions

    def predict_for_edges(self, edge_ids: list[str], timestamp: str | None, weather: dict[str, Any]) -> dict[str, dict[str, Any]]:
        ts = timestamp or pd.Timestamp.utcnow().isoformat()
        predictions = self.predict(segment_ids=edge_ids, timestamp=ts, weather=weather)
        return {item["segment_id"]: item for item in predictions}
