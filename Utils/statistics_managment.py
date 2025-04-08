from Utils.singleton_management import SingletonManager
from collections import defaultdict

class StatisticsCounter:
    def __init__(self):
        self._counters = defaultdict(int)

    def increment(self, key, amount=1):
        self._counters[key] += amount

    def get(self, key):
        return self._counters[key]

    def all(self):
        return dict(self._counters)

    def reset(self, key=None):
        if key:
            self._counters[key] = 0
        else:
            self._counters.clear()


def get_statistics_manager() -> StatisticsCounter:
    # Access or initialize the singleton variable
    statistics_manager_instance = SingletonManager.get("statistics_manager_instance", default=None)
    if statistics_manager_instance is None:
        statistics_manager_instance = StatisticsCounter()
        SingletonManager.set("statistics_manager_instance", statistics_manager_instance)
    return statistics_manager_instance