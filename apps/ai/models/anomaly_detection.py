from sklearn.ensemble import IsolationForest

def detect_anomaly(data):
    model = IsolationForest(contamination=0.05)
    model.fit(data)
    return model.predict(data)  # -1 = anomaly
