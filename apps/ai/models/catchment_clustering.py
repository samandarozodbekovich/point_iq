from sklearn.cluster import DBSCAN

def cluster_customers(locations):
    model = DBSCAN(eps=0.01, min_samples=5)
    labels = model.fit_predict(locations)
    return labels
