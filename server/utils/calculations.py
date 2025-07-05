def calculate_monthly_mortgage_payment(principal, annual_rate, years):
    """Calculate monthly mortgage payment using standard formula"""
    if annual_rate == 0:
        return principal / (years * 12)

    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12

    payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
              ((1 + monthly_rate) ** num_payments - 1)

    return payment


def calculate_annual_roi(annual_income, annual_expenses, initial_investment):
    """Calculate Return on Investment as a percentage"""
    if initial_investment == 0:
        return 0

    net_income = annual_income - annual_expenses
    roi = (net_income / initial_investment) * 100

    return roi


def calculate_cap_rate(net_operating_income, property_value):
    """Calculate capitalization rate"""
    if property_value == 0:
        return 0

    return (net_operating_income / property_value) * 100