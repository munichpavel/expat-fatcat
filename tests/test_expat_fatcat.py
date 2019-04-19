"""Tests for `expat_fatcat` package."""

import pytest
import expat_fatcat

def test_get_rate():
    rate = expat_fatcat.get_rate2usd('GBP', '2019-04-19')
    assert rate == 1.12