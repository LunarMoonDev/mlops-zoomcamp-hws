import click
import pickle
import pandas as pd
import logging

# Configuration
logging.basicConfig(
    filename='logs/app.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Constants and global variables
logging.info('Preparing model...')
with open('model.bin', 'rb') as f_in:
    dv, model = pickle.load(f_in)

CATEGORICAL = ['PULocationID', 'DOLocationID']

# Utility functions
def read_data(filename):
    df = pd.read_parquet(filename)
    
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[CATEGORICAL] = df[CATEGORICAL].fillna(-1).astype('int').astype('str')
    
    return df

def save_parquet(dataframe, year, month):
    output_file = f's3://homework/{year:04d}/{month:02d}/output.parquet'
    dataframe.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )

@click.command()
@click.option('--year', required=True, help='Year of the data')
@click.option('--month', required=True, help='Month of the data with the given year')
def predict(year, month):
    click.echo(f'Year: {year}')
    click.echo(f'Month: {month}')

    year = int(year)
    month = int(month)


    logging.info('Downloading input parquet file...')
    parquet_file_uri = f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet'
    df = read_data(parquet_file_uri)

    logging.info('Transforming input parquet...')
    dicts = df[CATEGORICAL].to_dict(orient='records')
    X_val = dv.transform(dicts)

    logging.info('Predicting with model...')
    y_pred = model.predict(X_val)

    
    logging.debug(f'Mean of the predicted durations: {y_pred.mean()}')
    logging.debug(f'Std of the predicted durations: {y_pred.std()}')
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')

    df['predicted_result'] = y_pred
    df_result = df[['ride_id', 'predicted_result']].copy()

    save_parquet(df_result, year, month)


if __name__ == '__main__':
    predict()