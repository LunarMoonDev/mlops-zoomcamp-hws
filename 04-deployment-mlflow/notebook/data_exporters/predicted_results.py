if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

# default value
OUTPUT_FILE_PATH = 'outputs'

@data_exporter
def export_data(data, *args, **kwargs):
    """
    Exports data to some source.

    Args:
        data: The output from the upstream parent block
        args: The output from any additional upstream blocks (if applicable)

    Output (optional):
        Optionally return any object and it'll be logged and
        displayed when inspecting the block run.
    """

    output_file_path = kwargs.get('OUTPUT_FILE_PATH', OUTPUT_FILE_PATH)
    output_file = f'{output_file_path}/output.parquet'

    data.to_parquet(output_file, engine='pyarrow', compression=None, index=False)
