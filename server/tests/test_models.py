import unittest
from unittest.mock import patch


# from models.property import Property  # Uncomment when you create your models
# from models.user import User

class TestPropertyModel(unittest.TestCase):

    def setUp(self):
        """Set up test data"""
        self.sample_property_data = {
            'address': '123 Test St',
            'purchase_price': 200000,
            'monthly_rent': 1500,
            'down_payment': 40000
        }

    def test_property_creation(self):
        """Test that a property can be created"""
        # TODO: Implement when Property model is created
        pass

    def test_property_validation(self):
        """Test property data validation"""
        # TODO: Implement when Property model is created
        pass


class TestUserModel(unittest.TestCase):

    def test_user_creation(self):
        """Test that a user can be created"""
        # TODO: Implement when User model is created
        pass


if __name__ == '__main__':
    unittest.main()