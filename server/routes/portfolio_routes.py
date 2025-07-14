"""
Portfolio routes for Flask backend
Add these routes to your Flask application
"""

from flask import Blueprint, request, jsonify, session
from services.portfolio_simulation_service import PortfolioSimulationService
from models.property import Property
from models.user import User
from models.simulation import Simulation
from models import db
from datetime import datetime

portfolio_bp = Blueprint('portfolio', __name__)
portfolio_service = PortfolioSimulationService()


@portfolio_bp.route('/api/portfolio/simulate', methods=['POST'])
def simulate_portfolio():
    """
    Run portfolio-wide simulation across multiple properties
    """
    try:
        # Check if user is authenticated
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        user_id = session['user_id']
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        properties = data.get('properties', [])
        simulation_params = data.get('simulation_params', {})

        if not properties:
            return jsonify({'error': 'No properties provided for simulation'}), 400

        # Validate that all properties belong to the user
        property_ids = [prop.get('id') for prop in properties]
        user_properties = Property.query.filter(
            Property.id.in_(property_ids),
            Property.user_id == user_id
        ).all()

        if len(user_properties) != len(property_ids):
            return jsonify({'error': 'Some properties do not belong to user'}), 403

        # Convert SQLAlchemy objects to dictionaries
        properties_data = []
        for prop in user_properties:
            prop_dict = {
                'id': prop.id,
                'name': prop.name,
                'address': prop.address,
                'city': prop.city,
                'state': prop.state,
                'zip_code': prop.zip_code,
                'purchase_price': float(prop.purchase_price),
                'current_value': float(prop.current_value),
                'down_payment': float(prop.down_payment or 0),
                'closing_costs': float(prop.closing_costs or 0),
                'monthly_rent': float(prop.monthly_rent or 0),
                'monthly_expenses': float(prop.monthly_expenses or 0),
                'appreciation_rate': float(simulation_params.get('appreciation_rate', 0.04)),
                'rent_growth_rate': float(simulation_params.get('rent_growth_rate', 0.03)),
                'expense_growth_rate': float(simulation_params.get('expense_growth_rate', 0.025))
            }
            properties_data.append(prop_dict)

        # Run portfolio simulation
        simulation_results = portfolio_service.simulate_portfolio(properties_data, simulation_params)

        if 'error' in simulation_results:
            return jsonify(simulation_results), 400

        # Save simulation results to database
        simulation_record = Simulation(
            user_id=user_id,
            property_id=None,  # Portfolio simulation - no single property
            simulation_type='portfolio',
            parameters=simulation_params,
            results=simulation_results,
            created_at=datetime.utcnow()
        )

        db.session.add(simulation_record)
        db.session.commit()

        return jsonify(simulation_results), 200

    except Exception as e:
        print(f"Portfolio simulation error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@portfolio_bp.route('/api/portfolio/summary', methods=['GET'])
def get_portfolio_summary():
    """
    Get portfolio summary statistics for the current user
    """
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        user_id = session['user_id']

        # Get all user properties
        properties = Property.query.filter_by(user_id=user_id).all()

        if not properties:
            return jsonify({
                'total_properties': 0,
                'total_investment': 0,
                'total_value': 0,
                'total_equity': 0,
                'monthly_income': 0,
                'monthly_expenses': 0,
                'monthly_cash_flow': 0
            }), 200

        # Calculate summary statistics
        total_properties = len(properties)
        total_investment = sum(float(p.purchase_price) + float(p.closing_costs or 0) for p in properties)
        total_value = sum(float(p.current_value) for p in properties)
        monthly_income = sum(float(p.monthly_rent or 0) for p in properties)
        monthly_expenses = sum(float(p.monthly_expenses or 0) for p in properties)
        monthly_cash_flow = monthly_income - monthly_expenses

        # Estimate total equity (simplified calculation)
        total_equity = 0
        for prop in properties:
            down_payment = float(prop.down_payment or 0)
            purchase_price = float(prop.purchase_price)
            current_value = float(prop.current_value)
            loan_amount = purchase_price - down_payment

            # Simplified equity calculation (assumes some principal paydown)
            estimated_remaining_debt = loan_amount * 0.85  # Rough estimate
            equity = max(0, current_value - estimated_remaining_debt)
            total_equity += equity

        summary = {
            'total_properties': total_properties,
            'total_investment': total_investment,
            'total_value': total_value,
            'total_equity': total_equity,
            'monthly_income': monthly_income,
            'monthly_expenses': monthly_expenses,
            'monthly_cash_flow': monthly_cash_flow,
            'average_property_value': total_value / total_properties if total_properties > 0 else 0,
            'portfolio_return': (
                        (total_value - total_investment) / total_investment * 100) if total_investment > 0 else 0
        }

        return jsonify(summary), 200

    except Exception as e:
        print(f"Portfolio summary error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@portfolio_bp.route('/api/portfolio/simulations', methods=['GET'])
def get_portfolio_simulations():
    """
    Get historical portfolio simulations for the current user
    """
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        user_id = session['user_id']

        # Get portfolio simulations (where property_id is None)
        simulations = Simulation.query.filter_by(
            user_id=user_id,
            simulation_type='portfolio'
        ).order_by(Simulation.created_at.desc()).limit(10).all()

        simulation_list = []
        for sim in simulations:
            simulation_list.append({
                'id': sim.id,
                'created_at': sim.created_at.isoformat(),
                'parameters': sim.parameters,
                'results_summary': {
                    'portfolio_irr': sim.results.get('portfolio_summary', {}).get('portfolioIRR', 0),
                    'total_properties': sim.results.get('portfolio_summary', {}).get('totalProperties', 0),
                    'total_value': sim.results.get('portfolio_summary', {}).get('totalValue', 0)
                }
            })

        return jsonify(simulation_list), 200

    except Exception as e:
        print(f"Get portfolio simulations error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@portfolio_bp.route('/api/portfolio/compare', methods=['POST'])
def compare_properties():
    """
    Compare multiple properties side by side
    """
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401

        user_id = session['user_id']
        data = request.get_json()

        property_ids = data.get('property_ids', [])
        comparison_metrics = data.get('metrics', ['irr', 'npv', 'cash_flow', 'cap_rate'])

        if not property_ids:
            return jsonify({'error': 'No properties specified for comparison'}), 400

        # Get properties
        properties = Property.query.filter(
            Property.id.in_(property_ids),
            Property.user_id == user_id
        ).all()

        if len(properties) != len(property_ids):
            return jsonify({'error': 'Some properties not found or unauthorized'}), 403

        # Run quick simulations for comparison
        comparison_results = []
        for prop in properties:
            prop_dict = {
                'id': prop.id,
                'name': prop.name,
                'purchase_price': float(prop.purchase_price),
                'current_value': float(prop.current_value),
                'monthly_rent': float(prop.monthly_rent or 0),
                'monthly_expenses': float(prop.monthly_expenses or 0)
            }

            # Quick simulation with default parameters
            simulation_params = {
                'analysis_period': 10,
                'discount_rate': 0.08,
                'appreciation_rate': 0.04,
                'rent_growth_rate': 0.03
            }

            # Use single property simulation
            from services.simulation_service import SimulationService
            sim_service = SimulationService()
            result = sim_service.run_simulation(prop_dict, simulation_params)

            comparison_results.append({
                'property': prop_dict,
                'metrics': {
                    'irr': result.get('irr', 0) * 100,
                    'npv': result.get('npv', 0),
                    'cash_flow': (float(prop.monthly_rent or 0) - float(prop.monthly_expenses or 0)) * 12,
                    'cap_rate': ((float(prop.monthly_rent or 0) - float(prop.monthly_expenses or 0)) * 12 / float(
                        prop.current_value)) * 100 if prop.current_value > 0 else 0,
                    'cash_on_cash': result.get('cash_on_cash_return', 0) * 100
                }
            })

        return jsonify({
            'comparison_results': comparison_results,
            'comparison_metrics': comparison_metrics
        }), 200

    except Exception as e:
        print(f"Property comparison error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500