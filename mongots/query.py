from datetime import datetime

from mongots.utils import get_day_count

AGGREGATION_MONTH_KEY = 'months'
AGGREGATION_DAY_KEY = 'days'
AGGREGATION_HOUR_KEY = 'hours'
AGGREGATION_KEYS = [
    '',
    'months.{month}.',
    'months.{month}.days.{day}.',
    'months.{month}.days.{day}.hours.{hour}.',
]
DATETIME_KEY = 'datetime'


def _build_empty_aggregate_document():
    return {
        'count': 0,
        'sum': 0,
        'sum2': 0,
    }

def _build_empty_one_hour_document(year, month, day, hour):
    base = _build_empty_aggregate_document()
    base[DATETIME_KEY] = datetime(year, month, day, hour)

    return base

def _build_empty_one_day_document(year, month, day):
    base = _build_empty_aggregate_document()
    base[DATETIME_KEY] = datetime(year, month, day)
    base[AGGREGATION_HOUR_KEY] = [
        _build_empty_one_hour_document(year, month, day, hour)
        for hour in range(0, 24)
    ]

    return base

def _build_empty_one_month_document(year, month):
    day_count = get_day_count(year, month)

    base = _build_empty_aggregate_document()
    base[DATETIME_KEY] = datetime(year, month, 1)
    base[AGGREGATION_DAY_KEY] = [
        _build_empty_one_day_document(year, month, day)
        for day in range(1, day_count+1)
    ]

    return base

def _build_empty_one_year_document(year):
    base = _build_empty_aggregate_document()
    base[DATETIME_KEY] = datetime(year, 1, 1)
    base[AGGREGATION_MONTH_KEY] = [
        _build_empty_one_month_document(year, month)
        for month in range(1, 13)
    ]

    return base

def build_empty_document(timestamp):
    return _build_empty_one_year_document(timestamp.year)

def build_filter_query(timestamp, tags=None):
    filters = tags or {}

    filters[DATETIME_KEY] = datetime(timestamp.year, 1, 1)

    return filters


def build_update_query(value, timestamp):
    inc_values = {
        'count': 1,
        'sum': value,
        'sum2': value**2,
    }

    datetime_args = {
        'month': str(timestamp.month - 1), # Array index: range from 0 to 11
        'day': str(timestamp.day - 1),     # Array index: range from 0 to 27 / 28 / 29 or 30
        'hour': str(timestamp.hour),       # range from 0 to 23
    }

    inc_keys = [
        key.format(**datetime_args)
        for key in AGGREGATION_KEYS
    ]

    inc_update = {
        '%s%s' % (inc_key, aggregate_type): inc_values[aggregate_type]
        for inc_key in inc_keys
        for aggregate_type in inc_values
    }

    return {
        '$inc': inc_update,
    }

def _get_keys_from_interval(interval):
    try:
        int_interval = {
            '1y': 0,
            'year': 0,
            '1m': 1,
            'month': 1,
            '1d': 2,
            'day': 2,
            '1h': 3,
            'hour': 3,
        }[interval]

        return [AGGREGATION_MONTH_KEY, AGGREGATION_DAY_KEY, AGGREGATION_HOUR_KEY][0:int_interval]
    except Exception:
        raise Exception('Bad interval {interval}'.format(interval=interval))
