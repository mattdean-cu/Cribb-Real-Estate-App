#!/usr/bin/env python3
"""
Test the simulation engine
"""

import requests
import json

BASE_URL = "http://localhost:5000"


def test_simulation():
    """Test the property simulation"""

    print("🧪 Testing Cribb Simulation Engine")
    print("=" * 40)

    # 1. Get properties
    print("1. Fetching properties...")
    response = requests.get(f"{BASE_URL}/api/properties")

    if response.status_code != 200:
        print(f"❌ Failed to get properties: {response.status_code}")
        return

    properties = response.json().get('properties', [])
    if not properties:
        print("❌ No properties found")
        return

    property_data = properties[0]
    property_id = property_data['id']
    property_name = property_data['name']

    print(f"✅ Found property: {property_name}")
    print(f"   Purchase Price: ${property_data['purchase_price']:,.2f}")
    print(f"   Monthly Rent: ${property_data['monthly_rent']:,.2f}")
    print(f"   Cash Flow: ${property_data['monthly_cash_flow']:,.2f}/month")

    # 2. Run simulation
    print(f"\n2. Running 10-year simulation...")

    simulation_data = {
        "years": 10,
        "strategy": "hold"
    }

    response = requests.post(
        f"{BASE_URL}/api/properties/{property_id}/simulate",
        headers={"Content-Type": "application/json"},
        json=simulation_data
    )

    if response.status_code != 200:
        print(f"❌ Simulation failed: {response.status_code}")
        print(f"Error: {response.text}")
        return

    results = response.json()

    # 3. Display results
    print("✅ Simulation completed!")
    print("\n📊 SIMULATION RESULTS:")
    print("=" * 40)

    if 'summary' in results:
        summary = results['summary']
        print(f"Total Investment: ${summary['total_investment']:,.2f}")
        print(f"Total Cash Flow: ${summary['total_cash_flow']:,.2f}")
        print(f"Final Property Value: ${summary['final_property_value']:,.2f}")
        print(f"Final Equity: ${summary['final_equity']:,.2f}")
        print(f"Total Return: ${summary['total_return']:,.2f}")
        print(f"Total Return %: {summary['total_return_percentage']:.2f}%")
        print(f"Average Annual Return: {summary['average_annual_return']:.2f}%")
        print(f"Internal Rate of Return: {summary['internal_rate_of_return']:.2f}%")
        print(f"Net Present Value: ${summary['net_present_value']:,.2f}")
        print(f"Cash-on-Cash Return: {summary['cash_on_cash_return']:.2f}%")

    # 4. Show year-by-year breakdown
    if 'yearly_results' in results:
        yearly = results['yearly_results']
        print(f"\n📈 YEAR-BY-YEAR BREAKDOWN:")
        print("=" * 40)
        print("Year | Cash Flow | Equity    | Property Value")
        print("-" * 45)

        for year_data in yearly[:5]:  # Show first 5 years
            year = year_data['year']
            cash_flow = year_data['net_cash_flow']
            equity = year_data['equity']
            prop_value = year_data['property_value']
            print(f"{year:4d} | ${cash_flow:8,.0f} | ${equity:8,.0f} | ${prop_value:12,.0f}")

        if len(yearly) > 5:
            print("...")
            last_year = yearly[-1]
            year = last_year['year']
            cash_flow = last_year['net_cash_flow']
            equity = last_year['equity']
            prop_value = last_year['property_value']
            print(f"{year:4d} | ${cash_flow:8,.0f} | ${equity:8,.0f} | ${prop_value:12,.0f}")

    print(f"\n🎉 Simulation test completed successfully!")


if __name__ == '__main__':
    try:
        test_simulation()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure it's running on http://localhost:5000")
    except Exception as e:
        print(f"❌ Error: {e}")