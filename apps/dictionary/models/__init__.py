from apps.dictionary.crimes.crime_statistics import models as crime_statistics_models
from apps.dictionary.crimes.crime_types import models as crime_types_model

from apps.dictionary.cars.car_type import models as car_type_models
from apps.dictionary.cars.car_traffic import models as car_traffic_models
from apps.dictionary.cars.registered_cars import models as registered_cars_models

from apps.dictionary.devices.device_data import models as device_data_models
from apps.dictionary.devices.footfall_event import models as footfall_event_models

from apps.dictionary.population_traffic.models import traffic_note
from apps.dictionary.population_traffic.models import traffic_segment
from apps.dictionary.population_traffic.models import point_of_interest


__all__ = [
    'crime_types_model',
    'crime_statistics_models',

    'car_traffic_models',
    'car_type_models',
    'registered_cars_models',

    'device_data_models',
    'footfall_event_models',

    'traffic_note',
    'traffic_segment',
    'point_of_interest',

]