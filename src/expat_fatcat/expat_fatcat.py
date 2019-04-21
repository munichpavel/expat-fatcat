"""Main module."""
import os
from datetime import datetime

from abc import ABC, abstractmethod

import quandl
    
    
class FatcatCalculator():
    '''Calculate fx rates and other tax related quantities for FATCA compliance'''
    def __init__(self, fx_rate_converter, from_currency, payments):
        self.fx_rate_converter = fx_rate_converter
        self.from_currency = from_currency
        self.payments = payments
        self._check_converter()
        
    def _check_converter(self):
        if self.fx_rate_converter.to_currency != 'USD':
            raise ValueError('invalid "to_currency": Fatcat only converts to USD')
        
    def _parse_date(self, date_string, date_format='%Y-%m-%d'):
        return datetime.strptime(date_string, date_format)
    
    def _get_rate(self, date_string, date_format='%Y-%m-%d'):
        date = self._parse_date(date_string, date_format)
        rate = self.fx_rate_converter.get_rate(self.from_currency, date)
        return rate
    
    
    def _get_converted_amount(self, amount, date_string, date_format='%Y-%m-%d'):
        return self._get_rate(date_string, date_format) * amount
    
    def __call__(self):

        converted_payments = [
            self._get_converted_amount(payment.get('amount'), payment.get('date'))
            for payment in self.payments
        ]
        
        return sum(converted_payments)
            


    

class AbsRateConverter(ABC):
    '''Abstract class for currency conversions'''
    def __init__(self, to_currency):
        self.to_currency = to_currency
    

    @abstractmethod
    def get_rate(self, from_currency, date):
        '''Returns exchange rate as a float'''
        pass


class DummyRateConverter(AbsRateConverter):
    '''Dummy fx rate converter for testing and development'''
    def __init__(self, to_currency):
        self.to_currency = to_currency


    def _get_call_str(self, from_currency):
        if from_currency == 'FOO':
            return 'ECB/FOO' + self.to_currency
        else:
            raise NotImplementedError('Only FOO to {} rates are implemented'.format(self.to_currency))


    def _dummy_api_call(self, call_str, date):
        '''Returns dummy value for all argument values'''
        return 1.125


    def get_rate(self, from_currency, date):
        '''Returns dummy exchange rate'''
        call_str = self._get_call_str(from_currency)
        return self._dummy_api_call(call_str, date)


class QuandlUSDRateConverter(AbsRateConverter):
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