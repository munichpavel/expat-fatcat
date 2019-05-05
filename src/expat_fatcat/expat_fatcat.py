"""Main module."""
import os
from datetime import datetime

from abc import ABC, abstractmethod

import quandl


def f2555(rate_converter, data):
    '''
    Calculate total payments in USD
    
    Example usage
    -------------
    >>> converter = DummyRateConverterTo('USD')
    >>> data = [
    ...     {'tag': 'salary', 'currency': 'FOO', 
    ...      'payments':  [
    ...          {'date': '2017-01-20', 'amount': 1000},
    ...          {'date': '2017-02-20', 'amount': 1500}
    ...      ]},
    ...     {'tag': 'dividends', 'currency': 'BAR', 
    ...      'payments': [
    ...          {'date': '2017-01-01', 'amount': 10},
    ...          {'date': '2017-02-01', 'amount': 50}
    ...      ]}
    ... ]
    >>> f2555(converter, data)
    {'salary': {'currency': 'FOO', 'amount': 2812.5}, 'dividends': {'currency': 'BAR', 'amount': 67.5}}
    '''
    calculator = FatcatCalculator(rate_converter)
    res = {}
    for d in data:
         res[d['tag']] = {
            'currency': d['currency'],
            'amount': calculator(d['currency'], d['payments'])
        }

    return res


class FatcatCalculator():
    '''Calculate fx rates and other tax related quantities for FATCA compliance'''
    def __init__(self, rate_converter):
        self.rate_converter = rate_converter
        self._check_converter()
        
    def _check_converter(self):
        if self.rate_converter.to_currency != 'USD':
            raise ValueError('invalid "to_currency": Fatcat only converts to USD')
        
    def _parse_date(self, date_string, date_format='%Y-%m-%d'):
        return datetime.strptime(date_string, date_format)
    
    def _get_rate(self, from_currency, date_string, date_format='%Y-%m-%d'):
        date = self._parse_date(date_string, date_format)
        rate = self.rate_converter.get_rate(from_currency, date)
        return rate
    
    
    def _get_converted_amount(self, from_currency, amount, date_string, date_format='%Y-%m-%d'):
        return self._get_rate(from_currency, date_string, date_format) * amount
    
    def __call__(self, from_currency, payments):

        converted_payments = [
            self._get_converted_amount(from_currency, payment.get('amount'), payment.get('date'))
            for payment in payments
        ]
        
        return sum(converted_payments)
    

class AbsRateConverterTo(ABC):
    '''Abstract class for conversions to a given currency'''
    def __init__(self, to_currency):
        self.to_currency = to_currency
    

    @abstractmethod
    def get_rate(self, from_currency, date):
        '''Returns exchange rate as a float'''
        pass


class DummyRateConverterTo(AbsRateConverterTo):
    '''Dummy fx rate converter for testing and development'''
    def __init__(self, to_currency, dates_rates=None):
        self.to_currency = to_currency
        self._set_dates_rates(dates_rates)
        
        
    def _set_dates_rates(self, dates_rates):
        if dates_rates is None:
            self._dates_rates = [(None, 1.125)]
        else:
            self._dates_rates = dates_rates


    def _get_call_str(self, from_currency):
        if from_currency == 'FOO':
            return 'ECB/FOO' + self.to_currency
        elif from_currency == 'BAR':
            return 'ECB/BAR' + self.to_currency
        else:
            raise NotImplementedError('Only FOO or BAR to {} rates are implemented'.format(self.to_currency))


    def _dummy_api_call(self, call_str, date):
        '''Returns dummy value for all argument values'''
        return 1.125


    def get_rate(self, from_currency, date):
        '''Returns dummy exchange rate'''
        call_str = self._get_call_str(from_currency)
        return self._dummy_api_call(call_str, date)


class QuandlUSDRateConverterTo(AbsRateConverterTo):
    '''Get conversion rates to USD from the QUANDL python api'''
    def __init__(self):
        self.to_currency = 'USD'
        self._set_key()
    
    def _set_key(self):
        if 'QUANDL_KEY' in os.environ:
            quandl.ApiConfig.api_key = os.environ['QUANDL_KEY']    
            
    def _get_call_str(self, from_currency):
        if from_currency == 'EUR':
            return 'ECB/EURUSD'
        elif from_currency == 'GBP':
            return 'FRED/DEXUSUK'
        else:
            raise NotImplementedError('Only EUR and GBP to USD rates are implemented')
            
    def get_rate(self, from_currency, date):
        '''Returns quandl sourced exchange rate. Note that quandl returns dataframes.'''
        res = quandl.get(self._get_call_str(from_currency), 
                             start_date=date, end_date=date)
        return res.iloc[0]['Value']