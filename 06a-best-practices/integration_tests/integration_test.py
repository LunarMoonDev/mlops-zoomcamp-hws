import os
from datetime import datetime 
import pandas as pd
from pandas.testing import assert_frame_equal
import logging

from batch import main

# CONFIG
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s]: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# HELPERS
def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

def get_output_dataframe(year, month):
    output_pattern = os.getenv('OUTPUT_FILE_PATTERN')
    output_file_path = output_pattern.format(year=year, month=month)

    s3_endpoint_url = os.getenv('S3_ENDPOINT_URL')

    logging.info('Grabbing actual output datafram from filepath: %s', output_file_path)
    return pd.read_parquet(output_file_path, storage_options={
        'client_kwargs': {
            'endpoint_url': s3_endpoint_url
        }
    })

def create_expected_data(data, columns):
    logging.info('Preparing expected dataframe...')
    expected = pd.DataFrame(data, columns=columns)
    return expected

# CONSTANTS
YEAR = 2023
MONTH = 1
COLUMNS = ['ride_id', 'predicted_duration']
EXPECTED_DATA = [
    ('2023/01_0', 23.20),
    ('2023/01_1', 13.08),
]

logging.info('Calling main method of batch model...')
# run the main function that needs testing
main(year=YEAR, month=MONTH)

actual_df = get_output_dataframe(year=YEAR, month=MONTH)
logging.info('Actual dataframe: \n%s', actual_df)
actual_df = actual_df.round(2)

expected_df = create_expected_data(data=EXPECTED_DATA, columns=COLUMNS)
logging.info('Expected dataframe: \n%s', expected_df)

assert_frame_equal(actual_df, expected_df)