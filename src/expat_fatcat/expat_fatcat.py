"""Main module."""
import os
from datetime import datetime

from abc import ABC, abstractmethod

import quandl
    
    
class FatcatConverter():
    
    def __init__(self, currency, FXRateConverter):
        self.currency = currency
        self.fx_rate_converter = FXRateConverter(currency)
        
    def _parse_date(self, date_string, date_format='%Y-%m-%d'):
        return datetime.strptime(date_string, date_format)
    
    def _get_rate2usd(self, date_string, date_format='%Y-%m-%d'):
        date = self._parse_date(date_string, date_format)
        rate = self.fx_rate_converter.get_rate(date, 'USD', self.currency)
        return rate


    

class RateConverter(ABC):
    '''Abstract class for currency conversions'''
    def __init__(self, currency):
        self.currency = currency


    @abstractmethod
    def get_rate(self, date, target_currency, original_currency):
        '''Returns exchange rate as a float'''
        pass
    
    
class QuandlConverter(ABC):

    def __init__(self, currency):
        
    #    self.currency = currency
        self._set_key()
        self._set_call()
    
    def _set_key(self):
        if 'QUANDL_KEY' in os.environ:
            quandl.ApiConfig.api_key = os.environ['QUANDL_KEY']    
            
    def _set_call(self):
        if self.currency == 'EUR':
            self.call_str = 'ECB/EURUSD'
        elif self.currency == 'GBP':
            self.call_str = 'FRED/DEXUSUK'
        else:
            raise NotImplementedError('Only EUR and GBP to USD rates are implemented')
            
    def get_rate(self, date, target_currency, original_currency):
        '''Returns quandl sourced exchange rate. Note that quandl returns dataframes.'''
        res = quandl.get(self.call_str, 
                             start_date=date, end_date=date)
        return res.iloc[0]['Value']