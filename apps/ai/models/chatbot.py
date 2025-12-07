from openai import OpenAI
from django.conf import settings

OPENAI_API_KEY = settings.OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def ask_chatbot(question, context_docs=[]):
    prompt = f"Context: {context_docs}\nQuestion: {question}"
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content
