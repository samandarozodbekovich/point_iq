# apps/networks/management/commands/build_location_score.py
from django.core.management.base import BaseCommand
from django.db import models

from apps.areas.districts.models import District
from apps.citizens.population.models import Population
from  apps.citizens.age_groups.models import  AgeGroupPopulation
from apps.dictionary.cars.car_traffic.models import CarTraffic
from apps.dictionary.devices.footfall_event.models import  FootfallEvent
from apps.competitors.competitor.models import Competitor
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib

class Command(BaseCommand):
    help = "Build LocationScore model and save predictions for districts"

    def handle(self, *args, **kwargs):
        # ----- STEP 1: Collect features -----
        districts = District.objects.all()
        data = []

        for d in districts:
            pop = Population.objects.filter(district=d).first()
            total_pop = (pop.count_male + pop.count_female) if pop else 0
            age_groups = AgeGroupPopulation.objects.filter(population__district=d)
            traffic = CarTraffic.objects.filter(district=d).first()
            footfall = FootfallEvent.objects.filter(location=d).first()
            competitors_count = Competitor.objects.filter(address__icontains=d.name_uz).count()

            # Simple feature engineering
            # total_pop = pop.total if pop else 0   <-- BU QATOR O'CHIRILADI
            avg_age = np.mean([ag.count for ag in age_groups]) if age_groups else 0
            traffic_score = traffic.score if traffic else 0
            footfall_score = footfall.score if footfall else 0

            data.append({
                "district_id": d.id,
                "total_pop": total_pop,
                "avg_age": avg_age,
                "traffic_score": traffic_score,
                "footfall_score": footfall_score,
                "competitors_count": competitors_count
            })

        df = pd.DataFrame(data)

        # ----- STEP 2: Synthetic target (0-100) for hackathon/demo -----
        # LocationScore = weighted sum of features (normalize later)
        df["score_raw"] = (
            df.total_pop * 0.4 +
            df.footfall_score * 0.3 +
            df.traffic_score * 0.2 +
            (100 - df.competitors_count) * 0.1
        )

        # Normalize to 0-100
        score_range = df["score_raw"].max() - df["score_raw"].min()
        if score_range == 0:
            df["location_score"] = 100  # yoki 0, istalgan default
        else:
            df["location_score"] = 100 * (df["score_raw"] - df["score_raw"].min()) / score_range

        # ----- STEP 3: Train simple XGBoost model -----
        feature_cols = ["total_pop", "avg_age", "traffic_score", "footfall_score", "competitors_count"]
        X = df[feature_cols]
        y = df["location_score"]

        model = xgb.XGBRegressor(objective="reg:squarederror", n_estimators=50)
        model.fit(X, y)

        # Save model
        joblib.dump(model, "location_score_model.pkl")
        self.stdout.write(self.style.SUCCESS("LocationScore model trained and saved!"))

        # Save predictions
        df[["district_id", "location_score"]].to_csv("district_location_scores.csv", index=False)
        self.stdout.write(self.style.SUCCESS("District scores saved to CSV!"))
