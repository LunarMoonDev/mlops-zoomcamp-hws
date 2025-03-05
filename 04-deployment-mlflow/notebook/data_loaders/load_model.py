import pickle

if 'data_loader' not in globals():
    from mage_ai.data_preparation.decorators import data_loader
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

# default values
MODEL_FILE = 'model.bin'
MODEL_FILE_PATH = 'models'

@data_loader
def load_data(*args, **kwargs):
    """
    Template code for loading data from any source.

    Returns:
        Anything (e.g. data frame, dictionary, array, int, str, etc.)
    """
    model_file = kwargs.get('MODEL_FILE', MODEL_FILE)
    model_path = kwargs.get('MODEL_FILE_PATH', MODEL_FILE_PATH)

    with open(f'{model_path}/{model_file}', 'rb') as f_in:
        dv, model = pickle.load(f_in)

    return dv, model


@test
def test_output(output, *args) -> None:
    """
    Template code for testing the output of the block.
    """
    assert output is not None, 'The output is undefined'