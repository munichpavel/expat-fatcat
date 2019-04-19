"""Tests for `expat_fatcat` package."""

import pytest
import expat_fatcat

def test_get_rate():
    rate = get_rate2usd('GBP', '2019-04-19')
    assert rate == 1.12