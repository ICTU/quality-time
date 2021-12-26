"""Load the data model."""

import json
import pathlib
import sys

MODULE_DIR = pathlib.Path(__file__).resolve().parent
SERVER_SRC_PATH = MODULE_DIR.parent.parent / "server" / "src"
sys.path.insert(0, str(SERVER_SRC_PATH))
from external.data_model import DATA_MODEL_JSON  # pylint: disable=import-error,wrong-import-order,wrong-import-position

DATA_MODEL = json.loads(DATA_MODEL_JSON)
