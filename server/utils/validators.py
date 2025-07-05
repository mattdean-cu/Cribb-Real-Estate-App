from .exceptions import ValidationError


def validate_positive_number(value, field_name):
    """Validate that a value is a positive number"""
    if not isinstance(value, (int, float)) or value <= 0:
        raise ValidationError(f"{field_name} must be a positive number")
    return True


def validate_percentage(value, field_name):
    """Validate that a value is a valid percentage (0-100)"""
    if not isinstance(value, (int, float)) or value < 0 or value > 100:
        raise ValidationError(f"{field_name} must be between 0 and 100")
    return True


def validate_property_data(data):
    """Validate property input data"""
    required_fields = ['purchase_price', 'monthly_rent']

    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")

    validate_positive_number(data['purchase_price'], 'Purchase price')
    validate_positive_number(data['monthly_rent'], 'Monthly rent')

    return True