from typing import Tuple

from sklearn.base import BaseEstimator
from sklearn.feature_extraction import DictVectorizer
from scipy.sparse._csr import csr_matrix

import mlflow

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

EXPERIMENT_NAME = "nyc-yellow-taxi"
TRACKING_URI = "http://mlflow:5000"

mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)
mlflow.sklearn.autolog()

@data_exporter
def export_data(
    data: Tuple[
        csr_matrix,
        csr_matrix,
        BaseEstimator,
        DictVectorizer],
    *args,
    **kwargs
):
    _, _, model, dv = data

    mlflow.sklearn.log_model(model, "linear_model")
    mlflow.sklearn.log_model(dv, "encoder_matrix")


