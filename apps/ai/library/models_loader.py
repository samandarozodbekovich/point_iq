import logging
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

OPENAI_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")

client = OpenAI(api_key=OPENAI_KEY)


def get_model_and_index(docs):

    try:
        logger.info("OpenAI model loaded successfully")
        return client, None, docs
    except Exception as e:
        logger.error(f"Model loading error: {str(e)}")
        raise


def simple_rag_retrieve(query: str, docs: list, top_k: int = 5) -> list:
    """
    Sodda RAG retrieval - OpenAI yordamida relevantsiya aniqlash

    Args:
        query (str): Qidiruv so'rovi
        docs (list): Qidirilayotgan hujjatlar
        top_k (int): Qaytarish uchun top hujjatlar soni

    Returns:
        list: Relevantsii hujjatlar
    """
    try:
        if not docs:
            return []

        # Hujjatlarni string ga o'girish
        docs_str = "\n".join([f"- {doc}" for doc in docs])

        prompt = f"""Quyidagi hujjatlardan "{query}" savoli uchun eng relevantsii {top_k} tani tanlang.

Hujjatlar:
{docs_str}

Javobda FAQAT relevantsii hujjatlarni ro'yxat shaklida qaytaring (hech qanday izoh yo'q):"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )

        # Response ni parse qilish
        result_text = response.choices[0].message.content.strip()

        # Hujjatlarni ajratib olish
        relevant_docs = []
        for doc in docs:
            if doc in result_text:
                relevant_docs.append({"text": doc})

        # Agar topilmasa, hamma hujjatni qaytarish
        if not relevant_docs:
            relevant_docs = [{"text": doc} for doc in docs[:top_k]]

        logger.info(f"Retrieved {len(relevant_docs)} relevant documents")
        return relevant_docs

    except Exception as e:
        logger.error(f"RAG retrieval xatosi: {str(e)}")
        return [{"text": doc} for doc in docs[:top_k]] if docs else []