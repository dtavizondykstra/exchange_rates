import csv
import sys
from pathlib import Path

# Add src directory to Python path - go up one level from tests/ to project root
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src"))

from data_utilities import save_to_csv


def test_save_to_csv(tmp_path):
    rows = [
        {"a": 1, "b": "x"},
        {"a": 2, "b": "y"},
    ]
    out_dir = tmp_path / "out"
    fp = save_to_csv(rows, out_dir, "test.csv")
    assert fp.exists()

    # verify contents
    with fp.open() as f:
        reader = csv.DictReader(f)
        data = list(reader)
    assert data == [{"a": "1", "b": "x"}, {"a": "2", "b": "y"}]
