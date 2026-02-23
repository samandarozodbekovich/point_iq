import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

def remove_duplicates(cells: List[Dict]) -> List[Dict]:
    seen = set()
    unique_cells = []
    for cell in cells:
        identifier = f"{cell.get('mcc')}-{cell.get('mnc')}-{cell.get('lac') or cell.get('tac')}-{cell.get('cellid') or cell.get('cid')}"
        if identifier not in seen:
            seen.add(identifier)
            unique_cells.append(cell)
    return unique_cells

def validate_cell_data(cell: Dict) -> bool:

    required = ['lat', 'lon', 'radio', 'mcc', 'mnc']
    return all(cell.get(field) is not None for field in required)