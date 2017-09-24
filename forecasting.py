import pandas as pd
import numpy as np
from datetime import datetime
from fbprophet import Prophet



# def forecast(data):
data = pd.read_csv('insights.csv', header=None, names=['ds', 'y'])
m = Prophet()
m.add_seasonality(name='monthly', period=30.5, fourier_order=5)
m.fit(data)
    # return m

def get_seasonality(periods, season):
    """

    :param int periods:
    :param str season: {'weekly', 'monthly', 'yearly'}
    :return:
    """
    days = pd.date_range(start='2017-01-01', periods=periods)
    df_w = m.seasonality_plot_df(days)
    week = m.predict_seasonal_components(df_w)[season].reset_index()
    week['index'] = days
    week.columns = ['date', 'value']
    return week.to_json(orient='records', date_format='iso', double_precision=2)


def weekly():
    return get_seasonality(7, 'weekly')

def monthly():
    return get_seasonality(30.5, 'monthly')

def yearly():
    return get_seasonality(365, 'yearly')


