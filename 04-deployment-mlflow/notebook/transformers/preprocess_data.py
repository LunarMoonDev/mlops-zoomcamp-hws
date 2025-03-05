from typing import Dict
from pandas import DataFrame

import ast

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

# default values
CATEGORICAL_COLS = ['PULocationID', 'DOLocationID']

@transformer
def transform(load_data: DataFrame, *args, **kwargs) -> Dict:
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block (Expecting Dataframe)
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    data, year, month = load_data

    categorical = ast.literal_eval(kwargs.get('CATEGORICAL_COLS', CATEGORICAL_COLS))

    data['duration'] = data.tpep_dropoff_datetime - data.tpep_pickup_datetime
    data['duration'] = data.duration.dt.total_seconds() / 60

    data = data[(data.duration >= 1) & (data.duration <= 60)].copy()
    data[categorical] = data[categorical].fillna(-1).astype('int').astype('str')

    return data[categorical].to_dict(orient='records'), year, month


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'