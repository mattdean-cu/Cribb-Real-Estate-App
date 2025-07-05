from utils.calculations import calculate_monthly_mortgage_payment, calculate_annual_roi


class ROISimulator:
    def simulate(self, property_data):
        """Simulate ROI using factory-prepared data"""

        # The factory has already validated and prepared the data
        property_type = property_data['property_type']
        calculation_rules = property_data['calculation_rules']

        # Use different calculation logic based on property type
        if property_type == 'single_family_rental':
            return self._simulate_rental(property_data)
        elif property_type == 'multifamily':
            return self._simulate_multifamily(property_data)
        elif property_type == 'commercial':
            return self._simulate_commercial(property_data)

    def _simulate_rental(self, data):
        """Rental-specific simulation logic"""
        # All the validation and defaults are already applied by factory
        purchase_price = data['purchase_price']
        monthly_rent = data['monthly_rent']
        down_payment_percent = data['down_payment_percent']  # Factory provided default

        # Calculate mortgage payment
        loan_amount = purchase_price * (1 - down_payment_percent / 100)
        monthly_payment = calculate_monthly_mortgage_payment(
            loan_amount,
            data['interest_rate'],
            data['loan_term']
        )

        # Factory provided calculation rules
        rules = data['calculation_rules']
        # ... rest of simulation logic