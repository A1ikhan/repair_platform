import logging
import os
from typing import Optional, Dict

import joblib
import numpy as np

logger = logging.getLogger(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'ml_models', 'price_model.pkl')
MODEL_PATH = os.path.abspath(MODEL_PATH)

DEVICE_TYPES = [
    'fridge', 'washer', 'dryer', 'oven', 'microwave',
    'dishwasher', 'tv', 'ac', 'water_heater', 'vacuum',
    'coffee_machine', 'other',
]


def extract_features(device_type: str, description: str) -> np.ndarray:
    """
    Extracts a fixed-length feature vector from a repair case.

    Features:
      [0..11] device_type one-hot (12 values)
      [12]    major keyword count
      [13]    medium keyword count
      [14]    simple keyword count
      [15]    weighted price multiplier (from rule-based analyzer)
      [16]    description length (chars), capped at 500
    """
    from back.services.price_estimation_service import _load_keywords

    # One-hot encode device type
    device_vec = [1.0 if device_type == dt else 0.0 for dt in DEVICE_TYPES]

    desc = description.lower()
    keywords = _load_keywords(device_type)

    major_count = medium_count = simple_count = 0
    total_weight = weighted_mult = 0.0

    for phrase, (mult, boost, repair_type) in sorted(
        keywords.items(), key=lambda x: len(x[0]), reverse=True
    ):
        if phrase in desc:
            if repair_type == 'major':
                major_count += 1
            elif repair_type == 'medium':
                medium_count += 1
            else:
                simple_count += 1
            total_weight += boost
            weighted_mult += mult * boost

    avg_multiplier = (weighted_mult / total_weight) if total_weight > 0 else 1.0
    desc_len = min(len(description), 500) / 500.0

    features = device_vec + [
        float(major_count),
        float(medium_count),
        float(simple_count),
        avg_multiplier,
        desc_len,
    ]
    return np.array(features, dtype=np.float32)


class MLPriceEstimator:
    _model = None
    _model_loaded = False

    @classmethod
    def _load_model(cls):
        if cls._model_loaded:
            return cls._model
        cls._model_loaded = True
        if os.path.exists(MODEL_PATH):
            try:
                cls._model = joblib.load(MODEL_PATH)
                logger.info("ML price model loaded from %s", MODEL_PATH)
            except Exception as e:
                logger.warning("Failed to load ML model: %s", e)
                cls._model = None
        return cls._model

    @classmethod
    def reload(cls):
        cls._model = None
        cls._model_loaded = False
        return cls._load_model()

    @classmethod
    def predict(cls, device_type: str, description: str) -> Optional[Dict]:
        model = cls._load_model()
        if model is None:
            return None
        try:
            features = extract_features(device_type, description).reshape(1, -1)
            predicted = float(model.predict(features)[0])
            predicted = max(1_000, round(predicted, -2))  # round to nearest 100 ₸

            # Estimate confidence from out-of-bag score stored at training time
            oob_r2 = getattr(model, '_oob_r2', None)
            if oob_r2 is not None:
                confidence = min(0.50 + oob_r2 * 0.40, 0.90)
            else:
                confidence = 0.60

            return {
                'predicted_price': predicted,
                'confidence': round(confidence, 2),
                'source': 'ml',
            }
        except Exception as e:
            logger.warning("ML prediction failed: %s", e)
            return None
