MongoTS
======

[![Build Status](https://travis-ci.org/AntoineToubhans/MongoTs.svg?branch=master)](https://travis-ci.org/AntoineToubhans/MongoTs)
[![Coverage Status](https://coveralls.io/repos/github/AntoineToubhans/MongoTs/badge.svg?branch=master)](https://coveralls.io/github/AntoineToubhans/MongoTs?branch=master)

A fast python API for storing time series in MongoDb

## Requirements

- python >= 3.3
- MongoDb 3.4

## Install

1. Clone this repo
2. install dependencies: `pip install -r requirements.txt`

## Usage

You can instanciate client, database, collection just like you would
do with pymongo:

```python
import mongots
client = mongots.MongoTSClient()
db = client.MyDatabase
collection = db.temperatures
```

### Insert

```
collection.insert_one(value, datetime, tags=tags)
```

Arguments:
- `value` (float): the value to be inserted
- `timestamp` (ddatemie.datetime): the timestamp for the value
- `tags` (dict, default=None): tags for the value; can be use the search/filter the value later on.

Return (bool): `True` if the insertion succeeded, `False` otherwise.

### Query

```
query(self, start, end, interval=interval, tags=tags, groupby=groupby)
```

Arguments:
- `start` (datetime): filters values after the start datetime
- `end` (datetime): filters values before the end datetime
- `aggregateby` (str): aggregates value per interval:
  - years: '1y', '2y', ...
  - month '1M', '2M', ...
  - days: '1d', '2d', ...
  - hours: '1h', '2h', ...
- `tags` (dict, default=None): similar to a mongo filter
- `groupby` (array): return statistics grouped by a list of tags (string)

Return (pandas.DataFrame): dataframe containing the statistics and indexed by datetimes.


## Run tests

Integration test requires a MongoDb to be up (run docker-compose up).

Launch all tests:

```bash
pytest
```

Launch only unit test:

```bash
python -m unittest -v test
```
