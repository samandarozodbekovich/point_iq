
from ..library.models_loader import get_model_and_index

def find_similar_business(descriptions, query_desc, top_k=5):
    from sklearn.neighbors import NearestNeighbors

    model, _ = get_model_and_index()
    embeddings = model.encode(descriptions + [query_desc])
    nbrs = NearestNeighbors(n_neighbors=top_k, metric='cosine').fit(embeddings[:-1])
    distances, indices = nbrs.kneighbors([embeddings[-1]])
    return indices[0], distances[0]