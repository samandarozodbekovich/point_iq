import os
import json
import logging
from openai import OpenAI
from ..library.models_loader import get_model_and_index
from apps.networks.models import CellTower
from apps.competitors.competitor.models import Competitor
from apps.citizens.people_consume.models import PeopleConsume
from apps.citizens.people_education.models import PeopleEducation
from apps.government_bodies.models import GovernmentBody

logger = logging.getLogger(__name__)

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=OPENAI_KEY)

#  Intent aniqlash
def detect_intent(query: str) -> str:
    """Foydalanuvchining niyatini aniqlash"""
    q = query.lower()
    if any(word in q for word in ["cafe", "business", "biznes", "ochmoq", "oching"]):
        return "business_advice"
    elif any(word in q for word in ["qaysi", "qanday", "nima", "kim"]):
        return "info_request"
    return "general_chat"

#  Region va biznes turi aniqlash
def extract_region_and_business(query):
    return "Mirobod", "kafe"

#  RAG retrieval - ✅ TUZATILDI
def rag_retrieve(query, top_k=5):
    try:
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

# Region stats
def get_region_stats(region_coords, radius=0.2):
    try:
        if not region_coords:
            return {}
        lat, lon = region_coords
        towers = CellTower.objects.filter(
            latitude__gte=lat - radius,
            latitude__lte=lat + radius,
            longitude__gte=lon - radius,
            longitude__lte=lon + radius
        )
        nearest = list(towers.values("id", "latitude", "longitude"))
        return {
            "nearest_towers": nearest,
            "population": PeopleConsume.objects.count(),
            "education": PeopleEducation.objects.count(),
            "competitors": Competitor.objects.count(),
            "gov_body": GovernmentBody.objects.count(),
        }
    except Exception as e:
        logger.error(f"get_region_stats xatosi: {str(e)}")
        return {}

# LLM bilan kontekstli AI tavsiya
def call_llm_with_context(query, docs, region_stats=None, business_type=None):
    try:
        prompt = f"""
Siz professional biznes va hudud bo'yicha AI modelsiz.
Savol: {query}
Hujjatlar konteksti: {docs}
Region stats: {region_stats}
Business type: {business_type}
Iltimos, JSON formatda tavsiya bering:
"""
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        raw_text = resp.choices[0].message.content
        try:
            return json.loads(raw_text)
        except:
            return {
                "ai_response": raw_text,
                "rationale": "JSON parse failed",
                "sources": [d["text"] for d in docs]
            }
    except Exception as e:
        logger.error(f"LLM call xatosi: {str(e)}")
        return {"error": str(e)}

# Oddiy chatbot
def ask_chatbot_response(query):
    return f"Chatbot javobi: {query}"

# Location score
def score_location(region_stats):
    try:
        if not region_stats:
            return 0
        total, count = 0, 0
        for k, v in region_stats.items():
            if k != "coordinates" and isinstance(v, (int, float)):
                total += v
                count += 1
            elif k != "coordinates" and isinstance(v, list):
                total += len(v)
                count += 1
        return round(total / count, 2) if count else 0
    except Exception as e:
        logger.error(f"score_location xatosi: {str(e)}")
        return 0