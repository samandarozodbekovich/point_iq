import os
import hashlib
import json
import logging
from django.core.cache import cache
from apps.ai.models import QueryHistory
from openai import OpenAI

from ..services import detect_intent, get_region_stats, score_location

logger = logging.getLogger(__name__)

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_KEY:
    logger.error("OPENAI_API_KEY not set in environment variables")
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=OPENAI_KEY)


def rag_retrieve(query: str, region_docs=None, top_k=5) -> list:
    """OpenAI yordamida sodda RAG retrieval"""
    try:
        if region_docs is None:
            region_docs = [
                "Hududdagi café ochish bo'yicha maslahatlar",
                "Raqobatchilar va joylashuv tahlili",
                "Aholi va transport holati statistikasi",
                "Biznes muvaffaqiyati uchun tavsiyalar",
                "Moliyaviy tavsiyalar va rentabellik",
                "Huquq va ro'yxatdan o'tish jarayoni",
                "Marketing va reklama strategiyasi",
                "Xodim tanlash va o'qitish",
                "Operatsion boshqaruv va ish rejasi",
                "Pelanggan xizmati va feedback jarayoni"
            ]

        # OpenAI embedding dan foydalanib relevantsii hujjatlarni topish
        prompt = f"""Quyidagi hujjatlardan "{query}" savoli uchun eng relevantsii {top_k} tani tanlang.

Hujjatlar:
{chr(10).join([f'- {doc}' for doc in region_docs])}

Javobda FAQAT relevantsii hujjatlarni ro'yxat shaklida qaytaring (hech qanday izoh yo'q):"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )

        result_text = response.choices[0].message.content.strip()

        # Hujjatlarni ajratib olish
        results = []
        for doc in region_docs:
            if doc in result_text:
                results.append({"text": doc})

        # Agar topilmasa, birinchi top_k hujjatni qaytarish
        if not results:
            results = [{"text": doc} for doc in region_docs[:top_k]]

        return results[:top_k]
    except Exception as e:
        logger.error(f"RAG retrieval xatosi: {str(e)}")
        return [{"text": doc} for doc in region_docs[:top_k]] if region_docs else []


# Business type detect
def detect_business_type(query: str) -> str:
    q = query.lower()
    business_keywords = {
        "market": ["market", "supermarket", "do'kon", "savdo"],
        "kafe": ["kafe", "coffee", "restaurant", "restoran"],
        "clinic": ["clinic", "klinika", "hospital", "shifoxona"],
        "servis": ["servis", "auto", "avto", "ta'mir"],
        "education": ["kurs", "education", "study", "o'qish"],
        "fitnes": ["fitnes", "gym", "sport", "training"],
    }
    for b, keys in business_keywords.items():
        if any(k in q for k in keys):
            return b
    return "umumiy biznes"


# AI tavsiya olish
def ask_ai_real(user_query: str, region_coords=None, business_type=None) -> dict:
    """
    Asosiy AI funksiyasi - OpenAI + RAG + Statistics
    """
    try:
        # Intent va Business Type aniqlash
        intent = detect_intent(user_query)
        if not business_type:
            business_type = detect_business_type(user_query)

        # Cache tekshirish
        cache_key = hashlib.md5(f"{user_query}-{region_coords}-{business_type}".encode()).hexdigest()
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for query: {user_query}")
            return cached

        # RAG retrieval
        context_docs = rag_retrieve(user_query)
        docs_text = "\n".join([d['text'] for d in context_docs])

        # Region Statistics
        region_stats = get_region_stats(region_coords) if region_coords else {}
        location_score = score_location(region_stats)

        # OpenAI Prompt
        prompt = f"""Siz professional iqtisodiy va biznes analitik AI modelsiz.

Foydalanuvchi Savoli: {user_query}
Biznes Turi: {business_type}
Intent: {intent}
Lokatsiya: {region_coords}
Lokatsiya Baho: {location_score}/10

Hudud Statistikasi:
- Telekommunikatsiya Minarlari: {region_stats.get('towers_count', 0)}
- Aholisi: {region_stats.get('population', 0)}
- Ta'lim Markazlari: {region_stats.get('education_centers', 0)}
- Raqobatchilar: {region_stats.get('competitors', 0)}
- Davlat Organlari: {region_stats.get('gov_bodies', 0)}

Kontekst Hujjatlar:
{docs_text}

Iltimos, FAQAT JSON formatda javobini bering:

{{
    "business_type": "{business_type}",
    "intent": "{intent}",
    "region_score": {location_score},
    "business_summary": "Biznes haqida qisqa malumat",
    "scores": {{
        "location_score": 7,
        "competition_score": 6,
        "population_score": 8,
        "growth_potential": 7,
        "success_probability": 7
    }},
    "business_suggestions": [
        "Tavsiya 1",
        "Tavsiya 2",
        "Tavsiya 3"
    ],
    "risks": [
        "Risk 1",
        "Risk 2"
    ],
    "investment_estimate": "Taxminan $10,000-50,000",
    "payback_period": "12-18 oy",
    "final_recommendation": "Asosiy tavsiya"
}}"""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=1500
        )

        raw_text = resp.choices[0].message.content.strip()

        # Markdown code block o'chirish
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {str(e)}")
            parsed = {
                "business_type": business_type,
                "intent": intent,
                "region_score": location_score,
                "business_summary": "Tahlil yuborildi",
                "scores": {"success_probability": 5},
                "business_suggestions": ["Tahlil kerakli"],
                "risks": ["API xatosi"],
                "final_recommendation": raw_text[:200]
            }

        # Final Response
        ai_response = {
            "intent": intent,
            "business_type": parsed.get("business_type", business_type),
            "region_score": location_score,
            "region_stats": region_stats,
            "business_summary": parsed.get("business_summary", ""),
            "scores": parsed.get("scores", {}),
            "business_suggestions": parsed.get("business_suggestions", []),
            "risks": parsed.get("risks", []),
            "investment_estimate": parsed.get("investment_estimate", ""),
            "payback_period": parsed.get("payback_period", ""),
            "ai_response": parsed.get("final_recommendation", ""),
            "sources": [d['text'] for d in context_docs],
            "context_docs": context_docs,
            "status": "success"
        }

        # DB saqlash
        try:
            QueryHistory.objects.create(
                user_query=user_query,
                business_type=business_type,
                region=str(region_coords),
                response_json=ai_response,
                status="done"
            )
        except Exception as e:
            logger.error(f"Database save xatosi: {str(e)}")

        cache.set(cache_key, ai_response, 3600)
        logger.info(f"AI response successfully generated")
        return ai_response

    except Exception as e:
        error_response = {
            "error": str(e),
            "status": "failed",
            "ai_response": None,
            "sources": [],
            "context_docs": [],
        }
        logger.error(f"ask_ai_real xatosi: {str(e)}")
        return error_response