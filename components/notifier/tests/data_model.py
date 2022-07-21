"""Import the data model from the shared data model component."""

import json

from shared_data_model import DATA_MODEL_JSON

DATA_MODEL = json.loads(DATA_MODEL_JSON)
