from lightgbm import LGBMRegressor

class RevenuePredictor:
    def __init__(self):
        self.model = LGBMRegressor()

    def train(self, x, y):
        self.model.fit(x, y)

    def predict(self, data):
        return self.model.predict([data])[0]