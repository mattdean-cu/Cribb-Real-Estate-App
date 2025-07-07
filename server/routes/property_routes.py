# server/routes/property_routes.py - Updated with Authentication
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.property import Property, PropertyType
from models.user import User
from models import db
from middleware.auth_middleware import require_auth, require_property_owner
from decimal import Decimal

property_bp = Blueprint('properties', __name__, url_prefix='/properties')


@property_bp.route('', methods=['GET'])
@login_required
def get_properties():
    """Get all properties for the current user"""
    try:
        properties = Property.query.filter_by(owner_id=current_user.id).all()
        return jsonify([prop.to_dict() for prop in properties]), 200
    except Exception as e:
        return jsonify({'error': 'Failed to fetch properties'}), 500


@property_bp.route('', methods=['POST'])
@login_required
def create_property():
    """Create a new property for the current user"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        required_fields = ['name', 'address', 'city', 'state', 'zip_code',
                           'property_type', 'purchase_price', 'down_payment', 'loan_amount']

        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Convert property_type string to enum
        try:
            property_type_enum = PropertyType(data['property_type'])
        except ValueError:
            return jsonify({'error': f'Invalid property type: {data["property_type"]}'}), 400

        # Create property for the current user
        property_obj = Property(
            name=data['name'],
            address=data['address'],
            city=data['city'],
            state=data['state'],
            zip_code=data['zip_code'],
            property_type=property_type_enum,

            # Financial Details
            purchase_price=Decimal(str(data['purchase_price'])),
            down_payment=Decimal(str(data['down_payment'])),
            loan_amount=Decimal(str(data['loan_amount'])),
            interest_rate=Decimal(str(data.get('interest_rate', 0.045))),
            loan_term_years=data.get('loan_term_years', 30),
            closing_costs=Decimal(str(data.get('closing_costs', 0))),

            # Property Details
            bedrooms=data.get('bedrooms'),
            bathrooms=Decimal(str(data['bathrooms'])) if data.get('bathrooms') else None,
            square_feet=data.get('square_feet'),
            year_built=data.get('year_built'),

            # Rental Information
            monthly_rent=Decimal(str(data['monthly_rent'])) if data.get('monthly_rent') else None,
            security_deposit=Decimal(str(data['security_deposit'])) if data.get('security_deposit') else None,

            # Operating Expenses
            property_taxes=Decimal(str(data.get('property_taxes', 0))),
            insurance=Decimal(str(data.get('insurance', 0))),
            hoa_fees=Decimal(str(data.get('hoa_fees', 0))),
            property_management=Decimal(str(data.get('property_management', 0))),
            maintenance_reserve=Decimal(str(data.get('maintenance_reserve', 0))),
            utilities=Decimal(str(data.get('utilities', 0))),
            other_expenses=Decimal(str(data.get('other_expenses', 0))),

            # Growth Assumptions
            vacancy_rate=Decimal(str(data.get('vacancy_rate', 0.05))),
            annual_rent_increase=Decimal(str(data.get('annual_rent_increase', 0.03))),
            annual_expense_increase=Decimal(str(data.get('annual_expense_increase', 0.02))),
            property_appreciation=Decimal(str(data.get('property_appreciation', 0.03))),

            owner_id=current_user.id  # Automatically set to current user
        )

        db.session.add(property_obj)
        db.session.commit()

        return jsonify(property_obj.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to create property: {str(e)}'}), 500


@property_bp.route('/<int:property_id>', methods=['GET'])
@login_required
@require_property_owner
def get_property(property_id):
    """Get a specific property"""
    try:
        property_obj = Property.query.get_or_404(property_id)
        return jsonify(property_obj.to_dict()), 200
    except Exception as e:
        return jsonify({'error': 'Property not found'}), 404


@property_bp.route('/<int:property_id>', methods=['PUT'])
@login_required
@require_property_owner
def update_property(property_id):
    """Update a property"""
    try:
        property_obj = Property.query.get_or_404(property_id)
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Convert property_type string to enum if provided
        if 'property_type' in data:
            try:
                property_type_enum = PropertyType(data['property_type'])
                property_obj.property_type = property_type_enum
            except ValueError:
                return jsonify({'error': f'Invalid property type: {data["property_type"]}'}), 400

        # Update basic information
        string_fields = ['name', 'address', 'city', 'state', 'zip_code']
        for field in string_fields:
            if field in data:
                setattr(property_obj, field, data[field])

        # Update financial details
        decimal_fields = [
            'purchase_price', 'down_payment', 'loan_amount', 'interest_rate',
            'closing_costs', 'monthly_rent', 'security_deposit', 'property_taxes',
            'insurance', 'hoa_fees', 'property_management', 'maintenance_reserve',
            'utilities', 'other_expenses', 'vacancy_rate', 'annual_rent_increase',
            'annual_expense_increase', 'property_appreciation'
        ]

        for field in decimal_fields:
            if field in data and data[field] is not None:
                setattr(property_obj, field, Decimal(str(data[field])))

        # Update integer fields
        integer_fields = ['bedrooms', 'square_feet', 'year_built', 'loan_term_years']
        for field in integer_fields:
            if field in data:
                setattr(property_obj, field, data[field])

        # Handle bathrooms (can be decimal)
        if 'bathrooms' in data and data['bathrooms'] is not None:
            property_obj.bathrooms = Decimal(str(data['bathrooms']))

        db.session.commit()
        return jsonify(property_obj.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to update property: {str(e)}'}), 500


@property_bp.route('/<int:property_id>', methods=['DELETE'])
@login_required
@require_property_owner
def delete_property(property_id):
    """Delete a property"""
    try:
        property_obj = Property.query.get_or_404(property_id)
        property_name = property_obj.name

        db.session.delete(property_obj)
        db.session.commit()

        return jsonify({'message': f'Property "{property_name}" deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Failed to delete property: {str(e)}'}), 500


@property_bp.route('/<int:property_id>/simulate', methods=['POST'])
@login_required
@require_property_owner
def simulate_property(property_id):
    """Run simulation on a property"""
    try:
        property_obj = Property.query.get_or_404(property_id)
        data = request.get_json() or {}

        years = data.get('years', 10)
        strategy_type = data.get('strategy', 'hold')

        # Import here to avoid circular imports
        from services.simulation_service import run_property_simulation

        # Run simulation
        results = run_property_simulation(property_obj, years, strategy_type)

        # TODO: Save simulation to database with current_user.id
        # You can extend this to save simulation results

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': f'Simulation failed: {str(e)}'}), 500


# Portfolio-level routes
@property_bp.route('/portfolio/stats', methods=['GET'])
@login_required
def get_portfolio_stats():
    """Get portfolio statistics for the current user"""
    try:
        properties = Property.query.filter_by(owner_id=current_user.id).all()

        if not properties:
            return jsonify({
                'total_properties': 0,
                'total_investment': 0,
                'total_equity': 0,
                'monthly_income': 0,
                'monthly_expenses': 0,
                'monthly_cash_flow': 0,
                'annual_cash_flow': 0,
                'average_cap_rate': 0,
                'average_cash_on_cash': 0
            }), 200

        # Calculate portfolio statistics
        stats = {
            'total_properties': len(properties),
            'total_investment': sum(float(prop.purchase_price) for prop in properties),
            'total_equity': sum(float(prop.purchase_price - prop.loan_amount) for prop in properties),
            'monthly_income': sum(float(prop.monthly_rent or 0) for prop in properties),
            'monthly_expenses': sum(float(prop.total_monthly_expenses) for prop in properties),
        }

        stats['monthly_cash_flow'] = stats['monthly_income'] - stats['monthly_expenses']
        stats['annual_cash_flow'] = stats['monthly_cash_flow'] * 12

        # Calculate averages
        stats['average_cap_rate'] = sum(float(prop.cap_rate) for prop in properties) / len(properties)
        stats['average_cash_on_cash'] = sum(float(prop.cash_on_cash_return) for prop in properties) / len(properties)

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': 'Failed to get portfolio stats'}), 500