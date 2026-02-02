from apps.ai.services import client
from apps.ai.logger import logger


def ask_chatbot_response(query: str, context_docs: list = None) -> str:
    try:
        if context_docs:
            docs_text = "\n".join([d.get("text", "") for d in context_docs])
            prompt = f"""Siz yordamchi chatbot-siz. Savollarga qisqacha va foydali javoblar bering.

Kontekst: {docs_text}
Savol: {query}

Javob:"""
        else:
            prompt = f"Savol: {query}\n\nQisqacha va foydali javob bering:"

        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        return resp.choices[0].message.content
    except Exception as e:
        logger.error(f"Chatbot response xatosi: {str(e)}")
        return "Kechirasiz, javobni berolmadim. Iltimos, qaytadan urinib ko'ring."