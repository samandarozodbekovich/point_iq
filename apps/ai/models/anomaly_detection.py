

def detect_anomaly(data):
    from sklearn.ensemble import IsolationForest

    model = IsolationForest(contamination=0.05)
    model.fit(data)
    return model.predict(data)  # -1 = anomaly
