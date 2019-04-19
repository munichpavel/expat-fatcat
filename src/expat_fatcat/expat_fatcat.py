"""Main module."""
import os
from datetime import datetime
import quandl

if 'QUANDL_KEY' in os.environ:
    quandl.ApiConfig.api_key = os.environ['QUANDL_KEY']

def get_rate(date, target_currency, original_currency, source):
    '''
    API call to source of exchange rates, e.g quandl
    
    Example usage
    -------------
    >>> get_rate(datetime(2019, 4, 19), 'USD', 'EUR', 'ECB/EURUSC')
    1.12
    
    '''
    return 1.12
    

class FatcatConverter():
    
    def __init__(self, currency, fx_source):
        self.currency = currency
        self.fx_source = fx_source
        
    def _parse_date(self, date_string, date_format='%Y-%m-%d'):
        return datetime.strptime(date_string, date_format)
    
    def _get_rate2usd(self, date_string, date_format='%Y-%m-%d'):
        date = self._parse_date(date_string, date_format)
        rate = get_rate(date, 'USD', self.currency, self.fx_source)
        return rate