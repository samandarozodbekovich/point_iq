from sklearn.neighbors import NearestNeighbors
from ..library.models_loader import get_model_and_index

def find_similar_business(descriptions, query_desc, top_k=5):
<<<<<<< HEAD
    model, _ = get_model_and_index()  # Lazy-loading bilan modelni olamiz
=======
    model, _ = get_model_and_index()
>>>>>>> 7cb6155 (Initial clean commit)
    embeddings = model.encode(descriptions + [query_desc])
    nbrs = NearestNeighbors(n_neighbors=top_k, metric='cosine').fit(embeddings[:-1])
    distances, indices = nbrs.kneighbors([embeddings[-1]])
    return indices[0], distances[0]
