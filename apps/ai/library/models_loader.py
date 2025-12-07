# apps/ai/library/models_loader.py
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

MODEL = None
FAISS_INDEX = None
DOCS = None

def get_model_and_index(docs):
    global MODEL, FAISS_INDEX, DOCS
    if MODEL is None or FAISS_INDEX is None:
        MODEL = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = MODEL.encode(docs)
        dim = embeddings.shape[1]
        FAISS_INDEX = faiss.IndexFlatL2(dim)
        FAISS_INDEX.add(np.array(embeddings))
        DOCS = docs
        print("AI model va FAISS index yuklandi")
    return MODEL, FAISS_INDEX, DOCS
