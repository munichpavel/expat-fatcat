# -*- coding: utf-8 -*-

"""Main module."""
import os
import pandas as pd

from datetime import datetime
from datetime import timedelta

import quandl

if 'QUANDL_KEY' in os.environ:
    quandl.ApiConfig.api_key = os.environ['QUANDL_KEY']
    
eur_quandl_calls = {
    'ECB': 'ECB/EURUSD',
    'FRED': 'FRED/DEXUSEU',
    'BOE': 'BOE/XUDLSER'
    }

gbp_quandl_calls = {
     'FRED': 'FRED/DEXUSUK',
     'BOE': 'BOE/XUDLUSS'
}

quandl_calls = {'EUR': eur_quandl_calls,
               'GBP': gbp_quandl_calls}


def convert_payments(payment_path, date_col = 'Date', amount_col='Amount', 
                       currency='EUR', source='ECB', pd_parse_args={}, date_str_format='%Y-%m-%d'):
    '''Reads in payment as data frame (csv or excel) and passes to convert_payment_df'''
    try:
        payment_df = pd.read_csv(payment_path, **pd_parse_args)
    except:
        #print(err)
        payment_df = pd.read_excel(payment_path, **pd_parse_args)
    
    return convert_payment_df(payment_df, amount_col, date_col, currency, source, date_str_format)


def convert_payment_df(payment_df, amount_col, date_col,
                       currency, source, date_str_format):
    ''''''
    fx_call_code = quandl_calls[currency][source]
    
    payment_df['fx_rate'] = payment_df[date_col].apply(lambda date: 
                                          get_fx_rate_smoothed(date, fx_call_code, date_str_format))
    
    payment_df['amount_usd'] = payment_df[amount_col]*payment_df['fx_rate']

    return payment_df


def get_fx_rate_smoothed(date, fx_call_code, date_str_format='%Y-%m-%d'):
    '''
    Gets fx rate for date according to fx call code, if missing, takes the average
    of fx rates before and after
    '''
    
    try:
        date_stamp = datetime.strptime(date, '%Y-%m-%d')
    except TypeError as err:
        date_stamp = date.to_pydatetime()
    
    try:
        fx_rate = quandl.get(fx_call_code, 
                             start_date=date_stamp, end_date=date_stamp + timedelta(days=1))
    except quandl.errors.quandl_error.NotFoundError as err:
        print(err)
        return
    
    if len(fx_rate) != 0:
        return fx_rate['Value'][0]
    else:
        return smooth_fx_rate(date_stamp, fx_call_code)
    
    
def smooth_fx_rate(date_stamp, quandl_call_code):
    ''''''
    fx_rate_before = quandl.get(quandl_call_code, 
                                    start_date = date_stamp - timedelta(days=7),
                                    end_date = date_stamp - timedelta(days=1))
    fx_rate_after = quandl.get(quandl_call_code, start_date=date_stamp + timedelta(days=1), 
                                         end_date=date_stamp + timedelta(days=7))
        
    return (fx_rate_before['Value'][-1] + fx_rate_after['Value'][0])/2


#############################################################
# Calculate specific lines of f2555 by summing up payments
#############################################################


def sum_payments_usd(payment_path, date_col = 'Date', amount_col='Amount', 
                       currency='EUR', source='ECB', pd_parse_args={}, date_str_format='%Y-%m-%d'):
    '''Sum payments in a foreign currency to USD'''
    payments_df = convert_payments(payment_path, date_col, amount_col, 
                                        currency, source, pd_parse_args, date_str_format)
    
    return payments_df['amount_usd'].sum()