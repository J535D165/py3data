import json
from pathlib import Path

from py3data import Repositories


def test_data_dump(tmpdir):
    export_f = Path(tmpdir, "datadump.json")

    all_data = [Repositories()[x["id"]] for x in Repositories().get()[0:5]]

    with open(export_f, "w") as f:
        json.dumps(all_data, f)
