import datetime
import time
from collections import OrderedDict
from typing import Union


class TimeSeries:
    def __init__(self, interpolate=False):
        self.data = OrderedDict()

    def update(self, value, time=None):
        if time is None:
            time = datetime.datetime.now()
            self.data[time] = value

    def get_timestamps(self):
        return list(self.data.keys())

    def __getitem__(self, idx: Union[datetime.datetime, int]):
        if isinstance(idx, int):
            return list(self.data.values())[idx]
        time = idx
        if not self.data:
            return None
        timestamps = self.get_timestamps()
        if time < timestamps[0]:
            return None
        min = 0
        max = len(self.data)
        while max - min > 1:
            checked = int((min + max)/2)
            if timestamps[checked] > idx:
                max = checked
            else:
                min = checked
        return self[min]
