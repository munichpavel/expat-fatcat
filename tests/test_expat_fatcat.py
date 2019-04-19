"""Tests for `expat_fatcat` package."""

import pytest
from datetime import datetime

import expat_fatcat



    
@pytest.fixture
def converter_eur():
    return expat_fatcat.FatcatConverter('EUR', 'ECB/EURUSD')

def test_date_conversion(converter_eur):
    assert converter_eur._parse_date('2019-04-19') == datetime(2019, 4, 19)
    
def test_get_rate(converter_eur):
    rate = converter_eur._get_rate2usd('2019-04-19')
    assert rate == 1.12