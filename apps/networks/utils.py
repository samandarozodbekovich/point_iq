from openai import OpenAI

<<<<<<< HEAD
client = OpenAI(
  api_key="***REMOVED***"
=======
from django.conf import settings

client = OpenAI(
  api_key=settings.OPENAI_API_KEY
>>>>>>> 7cb6155 (Initial clean commit)
)

response = client.responses.create(
  model="gpt-5-nano",
  input="write a haiku about ai",
  store=True,
)

print(response.output_text)

import requests
<<<<<<< HEAD
import json
import time
import logging
from django.conf import settings
from typing import List, Tuple, Dict, Optional
=======
import time
import logging
from django.conf import settings
from typing import List, Tuple, Dict
>>>>>>> 7cb6155 (Initial clean commit)

logger = logging.getLogger(__name__)

# Your free API key from OpenCellID
OPENCELLID_KEY = getattr(settings, 'OPENCELLID_KEY', '***REMOVED***')

# Tashkent area coordinates
MIN_LAT, MAX_LAT = 41.2, 41.4
MIN_LON, MAX_LON = 69.1, 69.3

# Step size for grid (smaller = more detail but more API calls)
LAT_STEP, LON_STEP = 0.02, 0.02  # Reduced to stay within free tier limits

OUTPUT_FILE = "tashkent_cells.json"


def generate_bboxes(min_lat: float, max_lat: float, min_lon: float, max_lon: float,
                    lat_step: float, lon_step: float) -> List[Tuple[float, float, float, float]]:
    """
    Generate bounding boxes covering the specified area.
    """
    bboxes = []
    lat = min_lat
    while lat < max_lat:
        lon = min_lon
        while lon < max_lon:
            bboxes.append([
                lat, lon,
                min(lat + lat_step, max_lat),
                min(lon + lon_step, max_lon)
            ])
            lon += lon_step
        lat += lat_step

    logger.info(f"Generated {len(bboxes)} bounding boxes")
    return bboxes


def fetch_cells_for_bbox(bbox: Tuple[float, float, float, float],
                         retry_count: int = 3) -> List[Dict]:
    """
    Fetch cell data for a single bounding box from OpenCellID API.
    Includes retry logic for rate limiting.
    """
    min_lat, min_lon, max_lat, max_lon = bbox

    # Format: minLat,minLon,maxLat,maxLon
    bbox_str = f"{min_lat},{min_lon},{max_lat},{max_lon}"

    url = "https://opencellid.org/cell/getInArea"
    params = {
        'key': OPENCELLID_KEY,
        'bbox': bbox_str,
        'format': 'json',
        'limit': 100  # Free tier limit
    }

    for attempt in range(retry_count):
        try:
            logger.debug(f"Fetching cells for bbox {bbox_str} (attempt {attempt + 1})")

            response = requests.get(url, params=params, timeout=30)

            if response.status_code == 200:
                data = response.json()

                # Check if response contains error
                if isinstance(data, dict):
                    if data.get('stat') == 'fail':
                        error_code = data.get('err', {}).get('code')
                        error_info = data.get('err', {}).get('info', 'Unknown error')

                        if error_code == 401:
                            logger.error(f"API key error: {error_info}")
                            return []
                        elif error_code == 429:
                            logger.warning(f"Rate limit hit. Waiting {60 * (attempt + 1)} seconds...")
                            time.sleep(60 * (attempt + 1))
                            continue
                        else:
                            logger.warning(f"API error for bbox {bbox_str}: {error_info}")
                            return []

                # Successful response
                if isinstance(data, list):
                    logger.debug(f"Found {len(data)} cells in bbox {bbox_str}")
                    return data
                else:
                    logger.warning(f"Unexpected response format for bbox {bbox_str}")
                    return []

            elif response.status_code == 429:
                wait_time = 60 * (attempt + 1)
                logger.warning(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue

            else:
                logger.error(f"HTTP {response.status_code} for bbox {bbox_str}: {response.text[:100]}")
                if attempt < retry_count - 1:
                    time.sleep(5)
                    continue
                return []

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout for bbox {bbox_str}")
            if attempt < retry_count - 1:
                time.sleep(5)
                continue
            return []

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for bbox {bbox_str}: {str(e)}")
            if attempt < retry_count - 1:
                time.sleep(5)
                continue
            return []

    return []


def check_api_key_status() -> Dict:
    """
    Check if API key is valid and return account status.
    """
    test_bbox = (41.31, 69.27, 41.32, 69.28)

    logger.info("Checking API key status...")

    # First test with getInArea
    cells = fetch_cells_for_bbox(test_bbox)

    if cells:
        return {
            'valid': True,
            'message': f"API key is valid. Found {len(cells)} cells in test area.",
            'has_getInArea_access': True
        }

    # If getInArea fails, try a simpler request
    try:
        # Check API key using stats endpoint (usually available in free tier)
        stats_url = "https://opencellid.org/cell/dashboard"
        params = {'key': OPENCELLID_KEY}

        response = requests.get(stats_url, params=params, timeout=10)

        if response.status_code == 200:
            return {
                'valid': True,
                'message': "API key is valid but getInArea may require whitelisting.",
                'has_getInArea_access': False,
                'suggestion': "Contact [email protected] for getInArea whitelisting"
            }
        else:
            return {
                'valid': False,
                'message': f"API key is invalid. Status code: {response.status_code}",
                'has_getInArea_access': False
            }

    except Exception as e:
        return {
            'valid': False,
            'message': f"API key check failed: {str(e)}",
            'has_getInArea_access': False
        }


def remove_duplicates(cells: List[Dict]) -> List[Dict]:
    """
    Remove duplicate cells based on unique identifier.
    """
    seen = set()
    unique_cells = []

    for cell in cells:
        # Create a unique identifier
        identifier = (
            str(cell.get('radio', '')),
            str(cell.get('mcc', '')),
            str(cell.get('mnc', '')),
            str(cell.get('lac', '') or cell.get('tac', '')),
            str(cell.get('cellid', '') or cell.get('cid', ''))
        )

        identifier_str = '|'.join(identifier)

        if identifier_str not in seen:
            seen.add(identifier_str)
            unique_cells.append(cell)

    logger.info(f"Removed {len(cells) - len(unique_cells)} duplicates")
    return unique_cells


def calculate_coverage(bboxes_count: int, cells_found: int) -> Dict:
    """
    Calculate coverage statistics.
    """
    # Approximate area of Tashkent in square degrees
    total_area = (MAX_LAT - MIN_LAT) * (MAX_LON - MIN_LON)
    bbox_area = (LAT_STEP * LON_STEP)
    covered_area = min(bboxes_count * bbox_area, total_area)

    return {
        'total_area_sq_deg': round(total_area, 4),
        'covered_area_sq_deg': round(covered_area, 4),
        'coverage_percentage': round((covered_area / total_area) * 100, 2) if total_area > 0 else 0,
        'cells_per_sq_deg': round(cells_found / covered_area, 2) if covered_area > 0 else 0
    }


def validate_cell_data(cell: Dict) -> bool:
    """
    Validate cell data structure.
    """
    required_fields = ['lat', 'lon', 'radio', 'mcc', 'mnc']

    for field in required_fields:
        if field not in cell or cell[field] is None:
            return False

    # Check if we have either lac/tac and cellid/cid
    if not any(key in cell for key in ['lac', 'tac']):
        return False

    if not any(key in cell for key in ['cellid', 'cid']):
        return False

    return True