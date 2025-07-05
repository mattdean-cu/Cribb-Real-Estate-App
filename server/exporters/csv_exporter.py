import csv
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from exporters.pdf_exporter import ExportStrategy


class CSVExporter(ExportStrategy):
    """Strategy for exporting data to CSV format"""

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            # Default to static/exports directory
            current_dir = os.path.dirname(os.path.abspath(__file__))
            server_dir = os.path.dirname(current_dir)
            self.output_dir = os.path.join(server_dir, 'static', 'exports')
        else:
            self.output_dir = output_dir

        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)

    def export(self, data: Dict[str, Any], filename: str = None) -> str:
        """Export simulation results to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"property_data_{timestamp}.csv"

        if not filename.endswith('.csv'):
            filename += '.csv'

        filepath = os.path.join(self.output_dir, filename)

        # Flatten the nested data structure for CSV
        flattened_data = self._flatten_data(data)

        # Write to CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if flattened_data:
                fieldnames = flattened_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(flattened_data)

        print(f"📊 CSV report exported to: {filepath}")
        return filepath

    def _flatten_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Flatten nested data structure for CSV export"""
        flattened = []

        # Handle single property data
        if 'property_data' in data and 'simulation_results' in data:
            row = {}

            # Add property data
            property_data = data['property_data']
            for key, value in property_data.items():
                if not isinstance(value, dict):
                    row[f"property_{key}"] = value

            # Add simulation results
            sim_results = data['simulation_results']
            for key, value in sim_results.items():
                if not isinstance(value, dict):
                    row[f"result_{key}"] = value

            # Add financial breakdown if present
            if 'financial_breakdown' in data:
                breakdown = data['financial_breakdown']
                for key, value in breakdown.items():
                    if not isinstance(value, dict):
                        row[f"financial_{key}"] = value

            # Add export metadata
            row['export_date'] = datetime.now().isoformat()

            flattened.append(row)

        # Handle portfolio data
        elif isinstance(data, list):
            for property_data in data:
                flattened.extend(self._flatten_data(property_data))

        return flattened

    def export_portfolio(self, portfolio_data: List[Dict[str, Any]], filename: str = None) -> str:
        """Export portfolio data to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"portfolio_data_{timestamp}.csv"

        return self.export(portfolio_data, filename)

    def export_comparison(self, comparison_data: List[Dict[str, Any]], filename: str = None) -> str:
        """Export property comparison data to CSV"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"property_comparison_{timestamp}.csv"

        if not filename.endswith('.csv'):
            filename += '.csv'

        filepath = os.path.join(self.output_dir, filename)

        # Create comparison table
        if not comparison_data:
            return filepath

        # Get all possible fields from all properties
        all_fields = set()
        for prop in comparison_data:
            flattened = self._flatten_data(prop)
            if flattened:
                all_fields.update(flattened[0].keys())

        # Create comparison rows
        comparison_rows = []
        for prop in comparison_data:
            flattened = self._flatten_data(prop)
            if flattened:
                row = {field: flattened[0].get(field, '') for field in all_fields}
                comparison_rows.append(row)

        # Write comparison CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            if comparison_rows:
                fieldnames = sorted(all_fields)
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(comparison_rows)

        print(f"📊 Property comparison CSV exported to: {filepath}")
        return filepath