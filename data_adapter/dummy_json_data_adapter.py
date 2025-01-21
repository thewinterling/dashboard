#!/usr/bin/env python3

import pandas as pd
from pathlib import Path
import json

from data_adapter import data_adapter


class DummyJsonDataAdapter(data_adapter.DataAdapter):
    def __init__(self, file_path: Path):
        """Example Json Data Adapter. This is just a toy example.
        More complex data structures might be better of divided into a dedicated
        reader and a data adapter. For this example, reading is simply a one-liner
        thus it doesn't make sense to overcomplicate things here.
        Also the 'adapter' part, is just to provide class properties for the data access.
        """
        assert file_path.is_file()
        with open(file_path) as jf:
            self._data = json.load(jf)

        self._columns = [
            "timestamp",
            "echo_distance",
            "significance",
            "amplitude",
            "points",
        ]
        self._name = "Dummy Data"
        assert all([e in self._data for e in self._columns])

    @property
    def data(self) -> dict:
        """Returns all the data.t"""
        return self._data

    @property
    def timestamps(self, numpy=False):
        """Returns the timestamps (of the respective echo)."""
        return self._data["timestamp"]

    @property
    def echoes(self):
        """Returns the raw echoes."""
        tmp = {
            "echo_distance": self._data["echo_distance"],
            "significance": self._data["significance"],
            "amplitude": self._data["amplitude"],
        }
        return pd.DataFrame(tmp)

    @property
    def points(self):
        "Returns the points laterated out of the raw echoes."
        return self._data["points"]
