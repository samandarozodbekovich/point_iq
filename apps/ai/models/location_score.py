
class LocationScorer:
    _model = None

    def __init__(self):
        if not LocationScorer._model:

            import joblib
            LocationScorer._model = joblib.load("apps/ai/models/location_scorer.pkl")

    def predict(self, data):
        model = LocationScorer._model
        # data -> dict -> model input
        X = [[data["population"], data["footfall"], data["competitors"], data["transport"], data["safety"], data["rent"]]]
        return float(model.predict(X)[0])

