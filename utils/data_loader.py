from pathlib import Path
import yaml


BASE_DIR = Path(__file__).resolve().parent.parent


def load_test_data():
    file_path = BASE_DIR / "data" / "test_data.yaml"

    with open(file_path, "r") as file:
        return yaml.safe_load(file)
