from lightgbm import LGBMRegressor

class RevenuePredictor:
    def __init__(self):
        self.model = LGBMRegressor()

<<<<<<< HEAD
    def train(self, X, y):
        self.model.fit(X, y)
=======
    def train(self, x, y):
        self.model.fit(x, y)
>>>>>>> 7cb6155 (Initial clean commit)

    def predict(self, data):
        return self.model.predict([data])[0]
