"""Main module."""
import os
from datetime import datetime

from abc import ABC, abstractmethod

import quandl
    
    
class FatcatCalculator():
    
    def __init__(self, FXRateConverter):
        self.fx_rate_converter = FXRateConverter('USD')
        
    def _parse_date(self, date_string, date_format='%Y-%m-%d'):
        return datetime.strptime(date_string, date_format)
    
    def _get_rate(self, from_currency, date_string, date_format='%Y-%m-%d'):
        date = self._parse_date(date_string, date_format)
        rate = self.fx_rate_converter.get_rate(from_currency, date)
        return rate


    

class AbsRateConverter(ABC):
    '''Abstract class for currency conversions'''
    def __init__(self, to_currency):
        self.to_currency = to_currency
    

    @abstractmethod
    def get_rate(self, from_currency, date):
        '''Returns exchange rate as a float'''
        pass


    
class QuandlUSDRateConverter(AbsRateConverter):

    def __init__(self):
        self.to_currency = 'USD'
        self._set_key()
        self._set_call()
    
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