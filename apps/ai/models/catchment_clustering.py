

def cluster_customers(locations):
    from sklearn.cluster import DBSCAN

    model = DBSCAN(eps=0.01, min_samples=5)
    labels = model.fit_predict(locations)
    return labels
