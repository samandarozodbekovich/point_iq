from apps.ai.logger import logger


def score_location(region_stats: dict) -> float:
    """Lokatsiyani bahoslash (0-10)"""
    try:
        if not region_stats:
            return 0.0

        weights = {
            "towers_count": 0.2,
            "population": 0.25,
            "education_centers": 0.2,
            "competitors": -0.15,
            "gov_bodies": 0.1
        }

        total_score = 0.0
        for key, weight in weights.items():
            value = region_stats.get(key, 0)
            if isinstance(value, (int, float)):
                normalized = min(float(value) / 100, 1.0)
                total_score += normalized * weight * 10

        return round(max(0, min(total_score, 10)), 2)
    except Exception as e:
        logger.error(f"score_location xatosi: {str(e)}")
        return 0.0
