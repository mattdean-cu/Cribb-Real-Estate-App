from flask import Blueprint, request, jsonify
from factories import PropertyTemplateFactory
from services.simulator import ROISimulator  # You'll create this later

property_bp = Blueprint('property', __name__)


@property_bp.route('/api/v1/property-types', methods=['GET'])
def get_property_types():
    """Get available property types for the frontend dropdown"""
    try:
        types = PropertyTemplateFactory.get_available_types()
        type_info = PropertyTemplateFactory.get_template_info()

        return jsonify({
            'success': True,
            'property_types': types,
            'template_info': type_info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@property_bp.route('/api/v1/simulate', methods=['POST'])
def simulate_property():
    """Main simulation endpoint - this is where the factory shines"""
    try:
        # Get data from frontend
        raw_data = request.json
        property_type = raw_data.get('property_type')

        if not property_type:
            return jsonify({'success': False, 'error': 'Property type required'}), 400

        # HERE'S THE FACTORY IN ACTION:
        # 1. The factory validates the input and applies defaults
        prepared_data = PropertyTemplateFactory.prepare_property_data(
            property_type=property_type,
            raw_data=raw_data
        )

        # 2. Now you have clean, validated data ready for simulation
        simulator = ROISimulator()
        results = simulator.simulate(prepared_data)

        return jsonify({
            'success': True,
            'simulation_results': results,
            'property_data': prepared_data
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@property_bp.route('/api/v1/template-info/<property_type>', methods=['GET'])
def get_template_requirements(property_type):
    """Get requirements for a specific property type"""
    try:
        template_info = PropertyTemplateFactory.get_template_info(property_type)
        return jsonify({
            'success': True,
            'template_info': template_info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500