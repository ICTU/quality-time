"""Import the data model from the shared python code."""

import json

from shared_data_model import DATA_MODEL_JSON

DATA_MODEL = json.loads(DATA_MODEL_JSON)
