import pytest
import os
import sys

# Add the server directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture
def sample_property_data():
    """Sample property data for testing"""
    return {
        'address': '123 Test St',
        'purchase_price': 200000,
        'monthly_rent': 1500,
        'down_payment': 40000,
        'interest_rate': 4.0,
        'loan_term': 30
    }