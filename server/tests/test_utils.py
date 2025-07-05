import unittest
from utils.validators import validate_positive_number, validate_percentage, validate_property_data
from utils.calculations import calculate_monthly_mortgage_payment, calculate_annual_roi, calculate_cap_rate
from utils.exceptions import ValidationError


class TestValidators(unittest.TestCase):

    def test_validate_positive_number_valid(self):
        """Test that positive numbers pass validation"""
        self.assertTrue(validate_positive_number(100, "test_field"))
        self.assertTrue(validate_positive_number(0.5, "test_field"))

    def test_validate_positive_number_invalid(self):
        """Test that non-positive numbers fail validation"""
        with self.assertRaises(ValidationError):
            validate_positive_number(-1, "test_field")
        with self.assertRaises(ValidationError):
            validate_positive_number(0, "test_field")

    def test_validate_percentage_valid(self):
        """Test that valid percentages pass"""
        self.assertTrue(validate_percentage(50, "test_field"))
        self.assertTrue(validate_percentage(0, "test_field"))
        self.assertTrue(validate_percentage(100, "test_field"))

    def test_validate_percentage_invalid(self):
        """Test that invalid percentages fail"""
        with self.assertRaises(ValidationError):
            validate_percentage(-1, "test_field")
        with self.assertRaises(ValidationError):
            validate_percentage(101, "test_field")

    def test_validate_property_data_valid(self):
        """Test that valid property data passes"""
        valid_data = {
            'purchase_price': 200000,
            'monthly_rent': 1500
        }
        self.assertTrue(validate_property_data(valid_data))

    def test_validate_property_data_missing_field(self):
        """Test that missing required fields fail"""
        invalid_data = {'purchase_price': 200000}
        with self.assertRaises(ValidationError):
            validate_property_data(invalid_data)


class TestCalculations(unittest.TestCase):

    def test_calculate_monthly_mortgage_payment(self):
        """Test mortgage payment calculation"""
        # $200,000 loan, 4% annual rate, 30 years
        payment = calculate_monthly_mortgage_payment(200000, 4, 30)
        self.assertAlmostEqual(payment, 954.83, places=2)

    def test_calculate_monthly_mortgage_payment_zero_rate(self):
        """Test mortgage payment with 0% interest"""
        payment = calculate_monthly_mortgage_payment(120000, 0, 30)
        expected = 120000 / (30 * 12)  # Just principal divided by months
        self.assertAlmostEqual(payment, expected, places=2)

    def test_calculate_annual_roi(self):
        """Test ROI calculation"""
        roi = calculate_annual_roi(18000, 8000, 100000)  # 10% ROI
        self.assertAlmostEqual(roi, 10.0, places=2)

    def test_calculate_cap_rate(self):
        """Test cap rate calculation"""
        cap_rate = calculate_cap_rate(10000, 200000)  # 5% cap rate
        self.assertAlmostEqual(cap_rate, 5.0, places=2)


if __name__ == '__main__':
    unittest.main()