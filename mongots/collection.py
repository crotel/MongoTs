import pandas as pd

from mongots.constants import DATETIME_KEY
from mongots.constants import COUNT_KEY
from mongots.constants import SUM_KEY
from mongots.constants import SUM2_KEY
from mongots.constants import MIN_KEY
from mongots.constants import MAX_KEY
from mongots.constants import MEAN_KEY
from mongots.constants import STD_KEY

from mongots.insert import build_empty_document
from mongots.insert import build_filter
from mongots.insert import build_update
from mongots.interval import parse_interval
from mongots.query import build_initial_match
from mongots.query import build_project
from mongots.query import build_sort
from mongots.query import build_unwind_and_match


class MongoTSCollection():
    def __init__(self, mongo_collection):
        self._collection = mongo_collection

    def insert_one(self, value, timestamp, tags=None):
        """Insert one timestamped value into the MongoDb collection.

        Args:
            value (float): the value to be inserted
            timestamp (datetime): the timestamp for the value
            tags (dict, default=None):
                tags for the value;
                can be use the search/filter the value later.

        Return (bool): True if the insertion succeeded, False otherwise.
        """
        filters = build_filter(timestamp, tags)
        update = build_update(value, timestamp)

        result = self._collection.update_one(filters, update, upsert=False)

        if result.modified_count == 0:
            empty_document = build_empty_document(timestamp)
            empty_document.update(filters)

            self._collection.insert_one(empty_document)

            result = self._collection.update_one(filters, update, upsert=False)

        return 1 == result.modified_count

    def query(self, start, end, interval=None, tags=None, groupby=None):
        """Query the MongoDb database for various statistics about values
        after `start` and before `end` timestamps.
        Available statistics are: count / mean / std / min / max.

        Args:
            start (datetime): filters values after the start datetime
            end (datetime): filters values before the end datetime
            interval (str):
                bucket statistics for each interval in the time range.
                Interval options are:
                - '1y', '2y', ... : one year, two years, ...
                - '1M', '2M', ... : one month, two months, ...
                - '1d', '2d', ... : one day, two days, ...
                - '1h', '2h', ... : one hour, two hours, ...
                - '1m', '2m', ... : one minute, two minutes, ...
                - '1s', '2s', ... : one second, two seconds, ...
            tags (dict, default=None):
                Filters the queried values.
                Similar to a filter when you do a find query in MongoDb.
            groupby (array): return statistics grouped by tags (string)

        Return (pandas.DataFrame):
            dataframe containing the statistics and indexed by datetimes
            and groupby tags (if any)
        """
        if interval is None:
            raise NotImplementedError(
                'Queries without interval are not supported yet.',
            )
        parsed_interval = parse_interval(interval)

        if groupby is None:
            groupby = []

        pipeline = []

        pipeline.append(build_initial_match(start, end, tags))
        pipeline.extend(build_unwind_and_match(start, end, parsed_interval))
        pipeline.append(build_project(parsed_interval, groupby))
        pipeline.append(build_sort())

        raw_result = list(self._collection.aggregate(pipeline))

        if 0 == len(raw_result):
            return pd.DataFrame(
                data=[],
                columns=[COUNT_KEY, MIN_KEY, MAX_KEY, MEAN_KEY, STD_KEY],
            )

        base_columns = [
            DATETIME_KEY,
            COUNT_KEY,
            SUM_KEY,
            SUM2_KEY,
            MIN_KEY,
            MAX_KEY,
        ]
        columns = base_columns + groupby

        df = pd.DataFrame(
            data=raw_result,
            columns=columns
        ).groupby([DATETIME_KEY] + groupby).aggregate({
            COUNT_KEY: 'sum',
            SUM_KEY: 'sum',
            SUM2_KEY: 'sum',
            MIN_KEY: 'min',
            MAX_KEY: 'max',
        })

        df[MEAN_KEY] = df[SUM_KEY] / df[COUNT_KEY]
        df[STD_KEY] = pd.np.sqrt(
            (df[SUM2_KEY] / df[COUNT_KEY]) - df[MEAN_KEY]**2,
        )

        return df[[COUNT_KEY, MIN_KEY, MAX_KEY, MEAN_KEY, STD_KEY]]
