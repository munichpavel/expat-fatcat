#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `expat_fatcat` package."""

import pytest

import quandl

from datetime import datetime

from expat_fatcat import expat_fatcat as fatcat
from expat_fatcat import cli

@pytest.fixture
def input_fx_call():
    
    return fatcat.quandl_calls['GBP']['FRED']
    
    
@pytest.fixture
def input_trading_day():
    return datetime(2018,1,18)


@pytest.fixture
def input_trading_day_before():
    return datetime(2018, 1, 17)


@pytest.fixture
def input_trading_day_after():
    return datetime(2018, 1, 19)


@pytest.fixture
def expected_smoothed_fx(input_trading_day_before, input_trading_day_after, input_fx_call):
    rate_before = quandl.get(input_fx_call, 
                start_date=input_trading_day_before, end_date=input_trading_day_before)['Value'][0]
    rate_after = quandl.get(input_fx_call, 
                start_date=input_trading_day_after, end_date=input_trading_day_after)['Value'][0]
        
    return (rate_before + rate_after)/2.0
    

def test_smooth_fx_rate(input_trading_day, input_fx_call, expected_smoothed_fx):
    
    assert fatcat.smooth_fx_rate(input_trading_day, input_fx_call) == expected_smoothed_fx