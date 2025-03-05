import pandas as pd

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@transformer
def transform(load_model, load_data, *args, **kwargs):
    """
    Template code for a transformer block.

    Add more parameters to this function if this block has multiple parent blocks.
    There should be one parameter for each output variable from each parent block.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    dv, model = load_model
    data, year, month = load_data

    X_val = dv.transform(data)
    y_pred = model.predict(X_val)
    
    ride_ids = [f'{year:04d}/{month:02d}_{i}' for i in range(len(data)) ]

    df = pd.DataFrame()

    df['ride_id'] = ride_ids
    df['pred_duration'] = y_pred

    return df


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'