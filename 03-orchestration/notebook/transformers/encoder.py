from typing import Tuple

import pandas as pd

from scipy.sparse._csr import csr_matrix
from sklearn.linear_model import LinearRegression
from sklearn.feature_extraction import DictVectorizer
from sklearn.base import BaseEstimator


if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer


@transformer
def transform(
    df: pd.DataFrame, **kwargs
) -> Tuple[
    csr_matrix,
    csr_matrix,
    BaseEstimator,
    DictVectorizer
]:
    categorical = ['PULocationID', 'DOLocationID']
    train_dicts = df[categorical].to_dict(orient='records')

    dv = DictVectorizer()
    X_train = dv.fit_transform(train_dicts)
    y_train =  df['duration'].values

    lr = LinearRegression()
    lr.fit(X_train, y_train)

    print(f"Intercept: {lr.intercept_}")

    return X_train, y_train, lr, dv
