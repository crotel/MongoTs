from parse import parse

from mongots.constants import AGGREGATION_MONTH_KEY
from mongots.constants import AGGREGATION_DAY_KEY
from mongots.constants import AGGREGATION_HOUR_KEY

YEAR = 0
MONTH = 1
DAY = 2
HOUR = 3
MINUTE = 4
SECOND = 5
MILISECOND = 6

AGGREGATION_KEYS = [
    None,  # year
    AGGREGATION_MONTH_KEY,
    AGGREGATION_DAY_KEY,
    AGGREGATION_HOUR_KEY,
    None,  # minute
    None,  # second
    None,  # milisecond
]

INTERVAL_STR = ['y', 'M', 'd', 'h', 'm', 's']
STR_INTERVAL = {s: idx for idx, s in enumerate(INTERVAL_STR)}


def parse_aggregateby(str):
    try:
        coef, str_interval = parse('{:d}{:w}', str)

        interval = STR_INTERVAL[str_interval]
    except Exception:
        raise Exception('Bad interval {}'.format(str_interval))

    return Aggregateby(interval, coef=coef)


class Aggregateby:
    def __init__(
        self,
        interval,
        coef=1,
        min_interval=HOUR,
        max_interval=MONTH,
    ):
        self._interval = interval
        self._coef = coef
        self._min_interval = min_interval
        self._max_interval = max_interval

        self._aggregation_keys = AGGREGATION_KEYS[
            self._max_interval:(self._interval+1)
        ]

        self._str__repr = '{}{}'.format(
            self._coef,
            INTERVAL_STR[self._interval]
        )

    @property
    def aggregation_keys(self):
        return self._aggregation_keys

    @property
    def str(self):
        return self._str__repr
