import os
import hashlib
import json
import logging
from django.core.cache import cache
from apps.ai.models import QueryHistory
from ..library.models_loader import get_model_and_index
from openai import OpenAI

logger = logging.getLogger(__name__)

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_KEY:
    logger.error("OPENAI_API_KEY not set in environment variables")
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=OPENAI_KEY)


# Simple RAG retrieval
def rag_retrieve(query, region_docs=None, top_k=5):
    """
    FAISS + SentenceTransformer asosida RAG retrieval
    """
    try:
        if region_docs is None:
            region_docs = [
                "Hududdagi café ochish bo'yicha maslahatlar",
                "Raqobatchilar va joylashuv tahlili",
                "Aholi va transport holati statistikasi",
                "Biznes muvaffaqiyati uchun tavsiyalar",
                "Moliyaviy tavsiyalar va rentabellik"
            ]

        MODEL, FAISS_INDEX, DOCS = get_model_and_index(region_docs)
        query_emb = MODEL.encode([query])
        D, I = FAISS_INDEX.search(query_emb, top_k)
        results = [{"text": region_docs[i]} for i in I[0] if i < len(region_docs)]
        return results
    except Exception as e:
        logger.error(f"RAG retrieval xatosi: {str(e)}")
        return []


# Business type detect
def detect_business_type(query: str) -> str:
    q = query.lower()
    business_keywords = {
        "market": ["market", "supermarket", "do'kon"],
        "kafe": ["kafe", "coffee", "restaurant"],
        "clinic": ["clinic", "klinika", "hospital"],
        "servis": ["servis", "auto", "avto"],
        "education": ["kurs", "education", "study"],
    }
    for b, keys in business_keywords.items():
        if any(k in q for k in keys):
            return b
    return "umumiy biznes"


# AI tavsiya olish
def ask_ai_real(user_query, region_coords=None):
    try:
        business_type = detect_business_type(user_query)

        # Caching
        cache_key = hashlib.md5(f"{user_query}-{region_coords}".encode()).hexdigest()
        cached = cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for query: {user_query}")
            return cached

        # RAG
        context_docs = rag_retrieve(user_query)

        # OpenAI prompt - ✅ YANGILANDI: Aniqroq JSON format
        docs_text = "\n".join([d['text'] for d in context_docs])

        prompt = f"""Siz professional iqtisodiy va biznes analitik AI modelsiz.

Foydalanuvchi savoli: {user_query}
Biznes turi: {business_type}
Region koordinatalari: {region_coords}

Kontekst hujjatlar:
{docs_text}

Iltimos, FAQAT JSON formatda javobi bering. Hech qanday boshqa text yozmanig:

{{
    "business_type": "{business_type}",
    "region_summary": "Region tahlili",
    "scores": {{
        "location_score": 7,
        "competition_score": 6,
        "population_score": 8,
        "success_probability": 7
    }},
    "business_suggestions": [
        "Tavsiya 1",
        "Tavsiya 2",
        "Tavsiya 3"
    ],
    "communication_quality": "Yaxshi",
    "final_recommendation": "Cafe ochish uchun bu hudud yaxshi tanlash"
}}"""

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        # ✅ TUZATILDI: message.content (message['content'] emas)
        raw_text = resp.choices[0].message.content

        try:
            # JSON'dan oldin/keyin bo'sh joylarni o'chirish
            raw_text = raw_text.strip()

            # Agar markdown code block ichida bo'lsa, o'chirish
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]

            parsed = json.loads(raw_text)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed: {str(e)}, raw response: {raw_text}")
            # Fallback default response
            parsed = {
                "business_type": business_type,
                "region_summary": "Tahlil yuborildi",
                "scores": {
                    "location_score": 5,
                    "competition_score": 5,
                    "population_score": 5,
                    "success_probability": 5
                },
                "business_suggestions": ["Tahlil kerakli"],
                "communication_quality": "API xatosi",
                "final_recommendation": raw_text[:200]  # Raw javobni saqlash
            }

        # ✅ TUZATILDI: Barcha kerakli fieldlar qo'shildi
        ai_json = {
            "business_type": parsed.get("business_type", business_type),
            "region_summary": parsed.get("region_summary", ""),
            "scores": parsed.get("scores", {}),
            "business_suggestions": parsed.get("business_suggestions", []),
            "ai_response": parsed.get("final_recommendation", ""),
            "rationale": parsed.get("communication_quality", ""),
            "sources": [d['text'] for d in context_docs],
            "context_docs": context_docs,
        }

        # DB saqlash
        try:
            QueryHistory.objects.create(
                user_query=user_query,
                business_type=business_type,
                region=str(region_coords),
                response_json=ai_json,
                status="done"
            )
        except Exception as e:
            logger.error(f"Database save xatosi: {str(e)}")

        cache.set(cache_key, ai_json, 3600)
        logger.info(f"AI response successfully generated for query: {user_query}")
        return ai_json

    except Exception as e:
        error_response = {
            "error": str(e),
            "ai_response": None,
            "rationale": None,
            "sources": [],
            "context_docs": [],
        }
        logger.error(f"ask_ai_real xatosi: {str(e)}")
        return error_response
