import json
import logging
import os
import base64
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Device base prices (тенге)
# ---------------------------------------------------------------------------
# Base prices in KZT — median market rates for Almaty (sources: 1v.kz, sneginka.kz,
# remont-holodilnikov.kz, rembyt-almaty.kz, profi.kz — May 2026).
# Represents a typical mid-complexity repair including labor + parts.
BASE_PRICES: Dict[str, float] = {
    'fridge':        20_000,
    'washer':        15_000,
    'dryer':         14_000,
    'oven':          10_000,
    'microwave':      8_000,
    'dishwasher':    14_000,
    'tv':            15_000,
    'ac':            22_000,
    'water_heater':  14_000,
    'vacuum':         6_000,
    'coffee_machine':11_000,
    'other':         10_000,
}

# ---------------------------------------------------------------------------
# Keyword profiles per device type
# Each entry: phrase → (price_multiplier, confidence_boost, repair_type)
# Longer phrases must come first so they match before substrings.
# ---------------------------------------------------------------------------
_KW = Dict[str, Tuple[float, float, str]]

REPAIR_PROFILES: Dict[str, _KW] = {
    'fridge': {
        # major
        'электронный модуль': (2.8, 0.15, 'major'),
        'утечка фреона':      (2.0, 0.15, 'major'),
        'компрессор':         (2.5, 0.15, 'major'),
        'испаритель':         (2.2, 0.12, 'major'),
        'конденсатор':        (2.0, 0.12, 'major'),
        'плата управления':   (2.5, 0.12, 'major'),
        'мотор':              (2.0, 0.12, 'major'),
        'фреон':              (1.8, 0.12, 'major'),
        'плата':              (2.3, 0.10, 'major'),
        # medium — real Almaty prices: thermostat 15k-20k, fan 12k-20k
        'не охлаждает':       (1.3, 0.10, 'medium'),
        'не морозит':         (1.3, 0.10, 'medium'),
        'не включается':      (1.2, 0.08, 'medium'),
        'намерзает':          (1.2, 0.08, 'medium'),
        'термостат':          (1.1, 0.10, 'medium'),
        'вентилятор':         (1.1, 0.10, 'medium'),
        'течет':              (1.1, 0.08, 'medium'),
        'шумит':              (1.0, 0.05, 'medium'),
        'вибрирует':          (1.0, 0.05, 'medium'),
        'запах':              (0.9, 0.05, 'medium'),
        'лёд':                (1.0, 0.05, 'medium'),
        # simple — real: bulb ~5k-8k, seal ~8k-12k, handle ~5k-7k
        'уплотнитель':        (0.55, 0.12, 'simple'),
        'дверца':             (0.45, 0.10, 'simple'),
        'лампочка':           (0.30, 0.15, 'simple'),
        'свет':               (0.35, 0.08, 'simple'),
        'полка':              (0.30, 0.12, 'simple'),
        'ручка':              (0.30, 0.12, 'simple'),
        'кнопка':             (0.40, 0.10, 'simple'),
    },
    'washer': {
        # major
        'электронный модуль': (2.8, 0.15, 'major'),
        'подшипник':          (2.2, 0.15, 'major'),
        'барабан':            (2.5, 0.12, 'major'),
        'мотор':              (2.5, 0.12, 'major'),
        'плата управления':   (2.5, 0.12, 'major'),
        'плата':              (2.3, 0.10, 'major'),
        # medium — real: ТЭН 8k-15k, помпа 8k-12k, УБЛ ~8k
        'нагревательный элемент': (0.85, 0.12, 'medium'),
        'не отжимает':        (0.90, 0.10, 'medium'),
        'не нагревает':       (0.80, 0.10, 'medium'),
        'не сливает':         (0.70, 0.10, 'medium'),
        'не включается':      (0.75, 0.08, 'medium'),
        'тэн':                (0.85, 0.12, 'medium'),
        'помпа':              (0.80, 0.12, 'medium'),
        'насос':              (0.75, 0.10, 'medium'),
        'щетки':              (0.75, 0.12, 'medium'),
        'течет':              (0.70, 0.08, 'medium'),
        'вибрирует':          (0.90, 0.08, 'medium'),
        'шумит':              (0.75, 0.05, 'medium'),
        # simple — real: засор 3k-6k, фильтр ~3k-5k, шланг ~4k-6k
        'уплотнитель':        (0.45, 0.10, 'simple'),
        'засор':              (0.30, 0.12, 'simple'),
        'фильтр':             (0.25, 0.12, 'simple'),
        'шланг':              (0.35, 0.12, 'simple'),
        'ручка':              (0.25, 0.12, 'simple'),
    },
    'oven': {
        # major
        'электронный модуль': (2.5, 0.15, 'major'),
        'плата':              (2.3, 0.12, 'major'),
        'тэн':                (1.7, 0.12, 'major'),
        'нагревательный элемент': (1.7, 0.12, 'major'),
        # medium
        'не нагревает':       (1.5, 0.10, 'medium'),
        'не включается':      (1.4, 0.08, 'medium'),
        'термостат':          (1.5, 0.10, 'medium'),
        'горелка':            (1.4, 0.10, 'medium'),
        'не зажигается':      (1.3, 0.10, 'medium'),
        'запах':              (1.2, 0.05, 'medium'),
        # simple
        'ручка':              (0.5, 0.12, 'simple'),
        'дверца':             (0.7, 0.10, 'simple'),
        'уплотнитель':        (0.8, 0.12, 'simple'),
        'лампочка':           (0.4, 0.15, 'simple'),
        'кнопка':             (0.6, 0.10, 'simple'),
    },
    'dishwasher': {
        # major
        'электронный модуль': (2.8, 0.15, 'major'),
        'насос':              (1.8, 0.12, 'major'),
        'помпа':              (1.8, 0.12, 'major'),
        'плата':              (2.5, 0.12, 'major'),
        # medium
        'не моет':            (1.4, 0.10, 'medium'),
        'не сливает':         (1.3, 0.10, 'medium'),
        'течет':              (1.4, 0.08, 'medium'),
        'не нагревает':       (1.5, 0.10, 'medium'),
        'тэн':                (1.5, 0.12, 'medium'),
        'не включается':      (1.3, 0.08, 'medium'),
        'шумит':              (1.2, 0.05, 'medium'),
        # simple
        'засор':              (0.8, 0.12, 'simple'),
        'фильтр':             (0.6, 0.12, 'simple'),
        'уплотнитель':        (0.8, 0.10, 'simple'),
        'ручка':              (0.5, 0.12, 'simple'),
    },
    'microwave': {
        # major
        'магнетрон':          (2.5, 0.15, 'major'),
        'трансформатор':      (2.2, 0.15, 'major'),
        'плата':              (2.0, 0.12, 'major'),
        # medium
        'не греет':           (1.5, 0.10, 'medium'),
        'не включается':      (1.3, 0.08, 'medium'),
        'искрит':             (1.4, 0.10, 'medium'),
        'шумит':              (1.2, 0.05, 'medium'),
        # simple
        'поворотный стол':    (0.5, 0.12, 'simple'),
        'дверца':             (0.7, 0.10, 'simple'),
        'лампочка':           (0.4, 0.15, 'simple'),
        'кнопка':             (0.6, 0.10, 'simple'),
    },
    'tv': {
        # major
        'матрица':            (3.0, 0.15, 'major'),
        'подсветка':          (2.5, 0.15, 'major'),
        'плата':              (2.3, 0.12, 'major'),
        'блок питания':       (2.0, 0.12, 'major'),
        # medium
        'не включается':      (1.4, 0.08, 'medium'),
        'нет изображения':    (1.5, 0.10, 'medium'),
        'нет звука':          (1.3, 0.10, 'medium'),
        'полосы':             (1.5, 0.10, 'medium'),
        'мигает':             (1.3, 0.08, 'medium'),
        # simple
        'пульт':              (0.3, 0.15, 'simple'),
        'кнопка':             (0.5, 0.10, 'simple'),
    },
    'ac': {
        # major
        'компрессор':         (2.8, 0.15, 'major'),
        'фреон':              (1.8, 0.12, 'major'),
        'утечка фреона':      (2.0, 0.15, 'major'),
        'плата':              (2.3, 0.12, 'major'),
        # medium
        'не охлаждает':       (1.5, 0.10, 'medium'),
        'не греет':           (1.5, 0.10, 'medium'),
        'течет':              (1.3, 0.08, 'medium'),
        'не включается':      (1.3, 0.08, 'medium'),
        'шумит':              (1.2, 0.05, 'medium'),
        # simple
        'фильтр':             (0.5, 0.12, 'simple'),
        'пульт':              (0.3, 0.15, 'simple'),
    },
    'water_heater': {
        # major
        'тэн':                (1.7, 0.12, 'major'),
        'термостат':          (1.5, 0.12, 'major'),
        'плата':              (2.0, 0.12, 'major'),
        # medium
        'течет':              (1.4, 0.10, 'medium'),
        'не нагревает':       (1.5, 0.10, 'medium'),
        'не включается':      (1.3, 0.08, 'medium'),
        'запах':              (1.2, 0.05, 'medium'),
        # simple
        'анод':               (0.7, 0.12, 'simple'),
        'клапан':             (0.8, 0.10, 'simple'),
        'шланг':              (0.6, 0.10, 'simple'),
    },
    'vacuum': {
        # major
        'мотор':              (2.0, 0.15, 'major'),
        # medium
        'не всасывает':       (1.3, 0.10, 'medium'),
        'не включается':      (1.3, 0.08, 'medium'),
        'шумит':              (1.2, 0.05, 'medium'),
        # simple
        'засор':              (0.6, 0.15, 'simple'),
        'шланг':              (0.7, 0.12, 'simple'),
        'фильтр':             (0.5, 0.12, 'simple'),
        'щетка':              (0.6, 0.10, 'simple'),
    },
    'dryer': {
        # major
        'тэн':                (1.8, 0.12, 'major'),
        'мотор':              (2.2, 0.12, 'major'),
        'плата':              (2.3, 0.12, 'major'),
        # medium
        'не сушит':           (1.5, 0.10, 'medium'),
        'не греет':           (1.5, 0.10, 'medium'),
        'не включается':      (1.3, 0.08, 'medium'),
        'шумит':              (1.2, 0.05, 'medium'),
        # simple
        'фильтр':             (0.5, 0.12, 'simple'),
        'ручка':              (0.5, 0.12, 'simple'),
        'уплотнитель':        (0.8, 0.10, 'simple'),
    },
    'coffee_machine': {
        # major
        'помпа':              (2.0, 0.12, 'major'),
        'бойлер':             (2.2, 0.15, 'major'),
        'плата':              (2.3, 0.12, 'major'),
        # medium
        'не варит':           (1.4, 0.10, 'medium'),
        'не нагревает':       (1.4, 0.10, 'medium'),
        'течет':              (1.3, 0.08, 'medium'),
        'не включается':      (1.3, 0.08, 'medium'),
        # simple
        'засор':              (0.7, 0.12, 'simple'),
        'клапан':             (0.8, 0.10, 'simple'),
        'уплотнитель':        (0.7, 0.10, 'simple'),
    },
}

# Fallback keywords that work for any device type
_GENERIC_KEYWORDS: _KW = {
    'электронный модуль': (2.5, 0.12, 'major'),
    'плата управления':   (2.3, 0.12, 'major'),
    'мотор':              (2.0, 0.10, 'major'),
    'плата':              (2.0, 0.10, 'major'),
    'не включается':      (1.3, 0.08, 'medium'),
    'течет':              (1.3, 0.08, 'medium'),
    'шумит':              (1.1, 0.05, 'medium'),
    'запах':              (1.1, 0.05, 'medium'),
    'ручка':              (0.5, 0.10, 'simple'),
    'кнопка':             (0.6, 0.10, 'simple'),
    'лампочка':           (0.4, 0.12, 'simple'),
}

# Map repair type → price range spread
_RANGE_SPREAD = {
    'major':   0.35,
    'medium':  0.30,
    'simple':  0.20,
    'unknown': 0.50,
}


_CACHE_TTL = 5 * 60  # 5 minutes


def _load_base_prices() -> Dict[str, float]:
    """Load base prices from DB with cache fallback to hardcoded values."""
    from django.core.cache import cache
    cached = cache.get('pricing:base_prices')
    if cached is not None:
        return cached

    try:
        from back.models.pricing_models import DeviceBasePrice
        prices = {row.device_type: float(row.base_price)
                  for row in DeviceBasePrice.objects.all()}
        if prices:
            cache.set('pricing:base_prices', prices, _CACHE_TTL)
            return prices
    except Exception as e:
        logger.warning("Could not load base prices from DB: %s", e)

    # Fallback to hardcoded values
    return BASE_PRICES


def _load_keywords(device_type: str) -> Dict[str, Tuple[float, float, str]]:
    """Load keywords from DB for a device type + generic, with cache."""
    from django.core.cache import cache
    cache_key = f'pricing:keywords:{device_type}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        from back.models.pricing_models import RepairKeyword
        rows = RepairKeyword.objects.filter(
            device_type__in=[device_type, '__generic__'],
            is_active=True,
        ).values('phrase', 'price_multiplier', 'confidence_boost', 'repair_type', 'device_type')

        # Device-specific keywords override generic ones with the same phrase
        result: Dict[str, Tuple[float, float, str]] = {}
        generic: Dict[str, Tuple[float, float, str]] = {}
        for row in rows:
            entry = (row['price_multiplier'], row['confidence_boost'], row['repair_type'])
            if row['device_type'] == '__generic__':
                generic[row['phrase']] = entry
            else:
                result[row['phrase']] = entry

        merged = {**generic, **result}
        if merged:
            cache.set(cache_key, merged, _CACHE_TTL)
            return merged
    except Exception as e:
        logger.warning("Could not load keywords from DB: %s", e)

    # Fallback to hardcoded values (device-specific overrides generic, matching DB merge order)
    return {**_GENERIC_KEYWORDS, **REPAIR_PROFILES.get(device_type, {})}


class KeywordAnalyzer:
    """Keyword-based price estimation — reads from DB, falls back to hardcoded."""

    @staticmethod
    def analyze(device_type: str, description: str) -> Dict:
        desc = description.lower()
        all_keywords = _load_keywords(device_type)

        matched: List[Dict] = []
        # Longer phrases checked first so "электронный модуль" beats "модуль"
        for phrase, (multiplier, conf_boost, repair_type) in sorted(
            all_keywords.items(), key=lambda x: len(x[0]), reverse=True
        ):
            if phrase in desc:
                matched.append({
                    'keyword': phrase,
                    'multiplier': multiplier,
                    'confidence_boost': conf_boost,
                    'repair_type': repair_type,
                })

        if not matched:
            return {
                'matched_keywords': [],
                'price_multiplier': 1.0,
                'confidence': 0.15,
                'dominant_repair_type': 'unknown',
            }

        total_weight = sum(m['confidence_boost'] for m in matched)
        avg_multiplier = sum(m['multiplier'] * m['confidence_boost'] for m in matched) / total_weight
        confidence = min(0.20 + total_weight, 0.65)
        dominant = max(matched, key=lambda m: m['multiplier'])['repair_type']

        return {
            'matched_keywords': [m['keyword'] for m in matched],
            'price_multiplier': avg_multiplier,
            'confidence': round(confidence, 2),
            'dominant_repair_type': dominant,
        }


class PhotoAnalyzer:
    """Analyzes a repair photo via Claude Vision API."""

    _PROMPT_TEMPLATE = (
        "You are a home appliance repair expert. Analyze this photo of a broken {device_type}.\n"
        "Respond with valid JSON only — no markdown, no explanation:\n"
        "{{\n"
        '  "damage_severity": "low|medium|high",\n'
        '  "visible_issues": ["list of observed problems"],\n'
        '  "repair_complexity": "simple|moderate|complex|major",\n'
        '  "price_multiplier": <float 0.5–3.0>,\n'
        '  "confidence_boost": <float 0.05–0.20>,\n'
        '  "notes": "<one sentence>"\n'
        "}}"
    )

    @staticmethod
    def analyze(image_bytes: bytes, media_type: str, device_type: str) -> Optional[Dict]:
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            logger.debug("ANTHROPIC_API_KEY not set — skipping photo analysis")
            return None

        try:
            import anthropic
        except ImportError:
            logger.warning("anthropic package not installed — skipping photo analysis")
            return None

        try:
            client = anthropic.Anthropic(api_key=api_key)
            image_b64 = base64.standard_b64encode(image_bytes).decode('utf-8')

            message = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=400,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": PhotoAnalyzer._PROMPT_TEMPLATE.format(device_type=device_type),
                        },
                    ],
                }],
            )

            raw = message.content[0].text.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```", 2)[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.rsplit("```", 1)[0].strip()
            result = json.loads(raw)
            # Clamp values to safe ranges
            result['price_multiplier'] = max(0.5, min(float(result.get('price_multiplier', 1.0)), 3.0))
            result['confidence_boost'] = max(0.05, min(float(result.get('confidence_boost', 0.10)), 0.20))
            return result

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            logger.warning("Photo analysis JSON parse error: %s", e)
            return None
        except Exception as e:
            logger.warning("Photo analysis failed: %s", e)
            return None


class PriceEstimationService:
    """Main price estimation service.

    Priority:
      1. ML model (if trained) — blended with keyword result
      2. Keyword rule-based estimator — always available
      3. Photo analysis via Claude Vision — optional boost
    """

    @staticmethod
    def estimate(
        device_type: str,
        description: str,
        image_bytes: Optional[bytes] = None,
        media_type: str = "image/jpeg",
    ) -> Dict:
        from back.services.ml_price_estimator import MLPriceEstimator
        from back.services.rag_price_service import RAGPriceService

        prices = _load_base_prices()
        base = prices.get(device_type, prices.get('other', 10_000))

        keyword_result = KeywordAnalyzer.analyze(device_type, description)
        rule_price = base * keyword_result['price_multiplier']
        confidence = keyword_result['confidence']
        repair_type = keyword_result['dominant_repair_type']

        # Layer 2a — RAG: find similar completed repairs
        rag_result = RAGPriceService.estimate(device_type, description)

        # Layer 2b — ML model (if trained)
        ml_result = MLPriceEstimator.predict(device_type, description)

        if ml_result and rag_result:
            # All three layers: ML 50% + RAG 25% + rules 25%
            predicted_price = (
                ml_result['predicted_price'] * 0.50
                + rag_result['predicted_price'] * 0.25
                + rule_price * 0.25
            )
            confidence = max(confidence, ml_result['confidence'], rag_result['confidence'])
            source = 'ml+rag+rules'
        elif ml_result:
            predicted_price = ml_result['predicted_price'] * 0.6 + rule_price * 0.4
            confidence = max(confidence, ml_result['confidence'])
            source = 'ml+rules'
        elif rag_result:
            # RAG 55% + rules 45%
            predicted_price = rag_result['predicted_price'] * 0.55 + rule_price * 0.45
            confidence = max(confidence, rag_result['confidence'])
            source = 'rag+rules'
        else:
            predicted_price = rule_price
            source = 'rules'

        photo_analysis = None
        if image_bytes:
            photo_analysis = PhotoAnalyzer.analyze(image_bytes, media_type, device_type)
            if photo_analysis:
                predicted_price = predicted_price * 0.7 + (base * photo_analysis['price_multiplier']) * 0.3
                confidence = min(confidence + photo_analysis['confidence_boost'], 0.92)
                source += '+photo'

        predicted_price = round(predicted_price, -2)  # round to nearest 100 ₸
        spread = _RANGE_SPREAD.get(repair_type, 0.50)

        return {
            'predicted_price': predicted_price,
            'confidence': round(confidence, 2),
            'price_range': {
                'min': round(predicted_price * (1 - spread), -2),
                'max': round(predicted_price * (1 + spread), -2),
            },
            'keywords_matched': keyword_result['matched_keywords'],
            'repair_type': repair_type,
            'photo_analysis': photo_analysis,
            'estimation_source': source,
            'message': PriceEstimationService._build_message(confidence, keyword_result['matched_keywords'], source),
        }

    @staticmethod
    def _build_message(confidence: float, keywords: List[str], source: str = 'rules') -> str:
        if 'ml' in source and 'rag' in source and confidence >= 0.70:
            return "Высокая точность: ML-модель + похожие заявки + ключевые слова"
        if 'ml' in source and confidence >= 0.75:
            return "Высокая точность: ML-модель + ключевые слова"
        if 'ml' in source:
            return "ML-модель обучена на реальных данных Алматы"
        if 'rag' in source and confidence >= 0.50:
            return "Оценка по похожим завершённым ремонтам в Алматы"
        if 'rag' in source:
            return "Найдены похожие заявки — оценка на основе реальных цен"
        if confidence >= 0.50:
            kw = ", ".join(keywords[:3])
            return f"Средняя уверенность. Выявлено: {kw}"
        if confidence >= 0.30:
            return "Базовая оценка по типу устройства и ключевым словам"
        return "Минимальная оценка — опишите проблему подробнее для точного расчёта"
