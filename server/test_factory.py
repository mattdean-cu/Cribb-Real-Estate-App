#!/usr/bin/env python3
"""Test the property factory"""

from factories import PropertyTemplateFactory, create_property_template


def test_factory():
    print("🏭 Testing Property Template Factory")

    # Test available types
    types = PropertyTemplateFactory.get_available_types()
    print(f"Available property types: {types}")

    # Test creating templates
    for property_type in types:
        print(f"\n--- Testing {property_type} ---")
        template = create_property_template(property_type)
        info = template.get_template_info()
        print(f"Description: {info['description']}")
        print(f"Required fields: {info['required_fields']}")

        # Test with sample data
        if property_type == 'single_family_rental':
            sample_data = {
                'purchase_price': 200000,
                'monthly_rent': 1500,
                'address': '123 Test St'
            }
        elif property_type == 'multifamily':
            sample_data = {
                'purchase_price': 400000,
                'monthly_rent': 3000,
                'address': '456 Multi St',
                'num_units': 4
            }
        else:  # commercial
            sample_data = {
                'purchase_price': 800000,
                'annual_rent': 60000,
                'address': '789 Commercial Blvd',
                'lease_term': 5
            }

        try:
            prepared_data = template.prepare_simulation_data(sample_data)
            print(f"✅ Template validation passed")
            print(f"Property type: {prepared_data['property_type']}")
        except Exception as e:
            print(f"❌ Template validation failed: {e}")


if __name__ == "__main__":
    test_factory()