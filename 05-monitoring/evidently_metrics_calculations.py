import datetime
import time
import random
import pandas as pd
import psycopg
import joblib

from prefect import task, flow
from prefect.logging import get_run_logger

from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric, ColumnQuantileMetric

# constants
SEND_TIMEOUT = 10
BEGIN = datetime.datetime(2024, 3, 1, 0, 0)
NUM_FEATURES = ['passenger_count', 'trip_distance', 'fare_amount', 'total_amount']
CAT_FEATUERS = ['PULocationID', 'DOLocationID']
POSTGRES_URI = 'host=localhost port=5432 dbname=test user=postgres password=example'

# vars
reference_data = pd.read_parquet('data/reference.parquet')
raw_data = pd.read_parquet('data/green_tripdata_2024-03.parquet')
column_mapping = ColumnMapping(
    prediction='prediction',
    numerical_features=NUM_FEATURES,
    categorical_features=CAT_FEATUERS,
    target=None
)

with open('models/lin_reg.bin', 'rb') as f_in:
    model = joblib.load(f_in)

report = Report(metrics = [
    ColumnDriftMetric(column_name='prediction'),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric(),
    ColumnQuantileMetric(column_name='fare_amount', quantile=0.5)
])

# functions
@task
def prep_db():
    create_table_statement="""
        DROP table IF EXISTS model_metrics;
        CREATE table model_metrics(
            timestamp timestamp,
            prediction_drift float,
            num_drifted_columns integer,
            share_missing_values float,
            fare_amount_50th_quantile_metric float
        );
    """
    logger = get_run_logger()

    with psycopg.connect('host=localhost port=5432 user=postgres password=example', autocommit=True) as conn:
        res = conn.execute("SELECT 1 FROM pg_database WHERE datname='test'")
        if len(res.fetchall()) == 0:
            logger.info('creating database...')
            conn.execute('CREATE DATABASE test')

    with psycopg.connect(POSTGRES_URI, autocommit=True) as conn:
        logger.info('creating table...')
        conn.execute(create_table_statement)

@task
def calculate_metrics_postgresql(i):
    logger = get_run_logger()

    current_data = raw_data[(raw_data.lpep_pickup_datetime >= (BEGIN + datetime.timedelta(i))) & 
                            (raw_data.lpep_pickup_datetime < (BEGIN + datetime.timedelta(i + 1)))]
    
    logger.info('predicting durations...')
    current_data['prediction'] = model.predict(current_data[NUM_FEATURES + CAT_FEATUERS].fillna(0))

    logger.info('creating reports...')
    report.run(reference_data = reference_data, current_data = current_data, column_mapping=column_mapping)
    result = report.as_dict()

    prediction_drift = result['metrics'][0]['result']['drift_score']
    num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
    share_missing_values = result['metrics'][2]['result']['current']['share_of_missing_values']
    fare_amount_50th_quantile_metric = result['metrics'][3]['result']['current']['value']

    return prediction_drift, num_drifted_columns, share_missing_values, fare_amount_50th_quantile_metric

@task
def save_report_metric(metrics, i):
    logger = get_run_logger()

    prediction_drift, num_drifted_columns, share_missing_values, fare_amount_50th_quantile_metric = metrics

    logger.info('saving reports...')
    with psycopg.connect(POSTGRES_URI, autocommit=True) as conn:
        conn.execute(
            "INSERT into model_metrics(timestamp, prediction_drift, num_drifted_columns, share_missing_values, fare_amount_50th_quantile_metric) values (%s, %s, %s, %s, %s)",
            (BEGIN + datetime.timedelta(i), prediction_drift, num_drifted_columns, share_missing_values, fare_amount_50th_quantile_metric))

@flow
def batch_monitoring_backfill():
    logger = get_run_logger()

    # prepare the database
    prep_db()

    last_send = datetime.datetime.now()
    for i in range(0, 31):
        metrics = calculate_metrics_postgresql(i)
        save_report_metric(metrics, i)

        # simulation of delays
        new_send = datetime.datetime.now()
        random_sec = random.randint(1, 3)
        seconds_elapsed = (new_send - last_send).total_seconds()
        if seconds_elapsed < SEND_TIMEOUT:
            time.sleep(SEND_TIMEOUT + (random_sec * 2))
        last_send = new_send

        logger.info('data sent...')
        

if __name__ == '__main__':
    batch_monitoring_backfill()