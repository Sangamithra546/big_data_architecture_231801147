import os
import logging
from pyspark.sql import SparkSession
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

# Suppress verbose PySpark logs
os.environ['PYSPARK_SUBMIT_ARGS'] = '--conf spark.ui.showConsoleProgress=false pyspark-shell'
logging.getLogger("py4j").setLevel(logging.ERROR)

def run_forecast(file_path, n_forecast=6, sample_rows=1000):
    spark = SparkSession.builder.appName("EnergyForecast").getOrCreate()
    df = spark.read.csv(file_path, header=True, inferSchema=True)
    # Downsample large datasets for fast demo
    total_rows = df.count()
    if total_rows > sample_rows:
        fraction = sample_rows / total_rows
        df = df.sample(withReplacement=False, fraction=fraction, seed=42)
    df_pd = df.toPandas()
    timestamp_col = df_pd.columns[0]
    df_pd[timestamp_col] = pd.to_datetime(df_pd[timestamp_col], errors='coerce')
    df_pd = df_pd.sort_values(by=timestamp_col).reset_index(drop=True)
    numeric_cols = df_pd.select_dtypes(include='number').columns
    forecast_result = {}
    future_df = pd.DataFrame({timestamp_col: pd.date_range(
        start=df_pd[timestamp_col].iloc[-1],
        periods=n_forecast+1, freq=pd.infer_freq(df_pd[timestamp_col])
    )[1:]})
    for col in numeric_cols:
        series = df_pd[col].fillna(method='ffill')
        try:
            model = ARIMA(series, order=(1,1,1))
            fit = model.fit()
            forecast = fit.forecast(steps=n_forecast)
        except:
            forecast = [series.iloc[-1]] * n_forecast
        forecast_result[col] = [round(x,2) for x in forecast]
        future_df[col] = forecast.round(2)
    return forecast_result, future_df
