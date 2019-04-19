"""Main module."""
from datetime import datetime

class FatcatConverter():
    
    def __init__(self, currency):
        self.currency = 'EUR'
        
    def _parse_date(self, date_string, date_format='%Y-%m-%d'):
        return datetime.strptime(date_string, date_format)
    
    def _get_rate2usd(self, date_string):
        return 1.12