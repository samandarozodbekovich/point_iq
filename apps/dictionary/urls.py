from django.urls import path

from .population_traffic.views.traffic_analysis import TrafficAnalysisPointView
from .population_traffic.views.traffic_heatmap import TrafficHeatmapView
from .population_traffic.views.business_intelligence import BusinessIntelligenceView

urlpatterns = [
    path('analysis/', TrafficAnalysisPointView.as_view()),
    path('heatmap/', TrafficHeatmapView.as_view()),
    path('business-intelligence/', BusinessIntelligenceView.as_view()),
]
