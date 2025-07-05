from abc import ABC, abstractmethod
from typing import Dict, Any, List
import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ExportStrategy(ABC):
    """Abstract base class for export strategies"""

    @abstractmethod
    def export(self, data: Dict[str, Any], filename: str) -> str:
        """Export data to specified format"""
        pass


class PDFExporter(ExportStrategy):
    """Strategy for exporting reports to PDF format"""

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
        self.styles = getSampleStyleSheet()

    def export(self, data: Dict[str, Any], filename: str = None) -> str:
        """Export simulation results to PDF"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"property_report_{timestamp}.pdf"

        if not filename.endswith('.pdf'):
            filename += '.pdf'

        filepath = os.path.join(self.output_dir, filename)

        # Create PDF document
        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []

        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2E86AB')
        )
        story.append(Paragraph("Property Investment Report", title_style))
        story.append(Spacer(1, 20))

        # Property Information
        if 'property_data' in data:
            story.extend(self._create_property_section(data['property_data']))

        # Simulation Results
        if 'simulation_results' in data:
            story.extend(self._create_results_section(data['simulation_results']))

        # Financial Breakdown
        if 'financial_breakdown' in data:
            story.extend(self._create_financial_breakdown(data['financial_breakdown']))

        # Build PDF
        doc.build(story)

        print(f"📄 PDF report exported to: {filepath}")
        return filepath

    def _create_property_section(self, property_data: Dict[str, Any]) -> List:
        """Create property information section"""
        elements = []

        # Section title
        elements.append(Paragraph("Property Information", self.styles['Heading2']))
        elements.append(Spacer(1, 10))

        # Property details table
        property_info = [
            ['Address', property_data.get('address', 'N/A')],
            ['Property Type', property_data.get('property_type', 'N/A').replace('_', ' ').title()],
            ['Purchase Price', f"${property_data.get('purchase_price', 0):,.2f}"],
            ['Monthly Rent', f"${property_data.get('monthly_rent', 0):,.2f}"],
            ['Down Payment', f"{property_data.get('down_payment_percent', 0)}%"],
        ]

        if property_data.get('num_units'):
            property_info.append(['Number of Units', str(property_data['num_units'])])

        table = Table(property_info, colWidths=[2 * inch, 3 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _create_results_section(self, results: Dict[str, Any]) -> List:
        """Create simulation results section"""
        elements = []

        # Section title
        elements.append(Paragraph("Investment Analysis", self.styles['Heading2']))
        elements.append(Spacer(1, 10))

        # Key metrics
        metrics = [
            ['Metric', 'Value'],
            ['Annual ROI', f"{results.get('annual_roi', 0):.2f}%"],
            ['Cap Rate', f"{results.get('cap_rate', 0):.2f}%"],
            ['Monthly Cash Flow', f"${results.get('monthly_cash_flow', 0):,.2f}"],
            ['Annual Cash Flow', f"${results.get('annual_cash_flow', 0):,.2f}"],
            ['Cash-on-Cash Return', f"{results.get('cash_on_cash_return', 0):.2f}%"],
        ]

        table = Table(metrics, colWidths=[2.5 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _create_financial_breakdown(self, breakdown: Dict[str, Any]) -> List:
        """Create financial breakdown section"""
        elements = []

        elements.append(Paragraph("Financial Breakdown", self.styles['Heading2']))
        elements.append(Spacer(1, 10))

        # Monthly breakdown
        monthly_data = [
            ['Item', 'Monthly Amount'],
            ['Rental Income', f"${breakdown.get('monthly_income', 0):,.2f}"],
            ['Mortgage Payment', f"${breakdown.get('mortgage_payment', 0):,.2f}"],
            ['Property Taxes', f"${breakdown.get('property_taxes', 0):,.2f}"],
            ['Insurance', f"${breakdown.get('insurance', 0):,.2f}"],
            ['Maintenance', f"${breakdown.get('maintenance', 0):,.2f}"],
            ['Property Management', f"${breakdown.get('property_mgmt', 0):,.2f}"],
            ['Net Cash Flow', f"${breakdown.get('net_cash_flow', 0):,.2f}"],
        ]

        table = Table(monthly_data, colWidths=[3 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        elements.append(table)
        elements.append(Spacer(1, 10))

        # Footer
        elements.append(Paragraph(
            f"Report generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            self.styles['Normal']
        ))

        return elements

    def export_portfolio(self, portfolio_data: List[Dict[str, Any]], filename: str = None) -> str:
        """Export multiple properties to PDF portfolio report"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"portfolio_report_{timestamp}.pdf"

        if not filename.endswith('.pdf'):
            filename += '.pdf'

        filepath = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        story = []

        # Portfolio title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2E86AB')
        )
        story.append(Paragraph("Real Estate Portfolio Report", title_style))
        story.append(Spacer(1, 20))

        # Portfolio summary
        total_value = sum(prop.get('purchase_price', 0) for prop in portfolio_data)
        total_income = sum(prop.get('monthly_rent', 0) for prop in portfolio_data)

        summary = [
            ['Portfolio Summary', ''],
            ['Total Properties', str(len(portfolio_data))],
            ['Total Investment', f"${total_value:,.2f}"],
            ['Total Monthly Income', f"${total_income:,.2f}"],
            ['Average Property Value', f"${total_value / len(portfolio_data):,.2f}" if portfolio_data else "$0"],
        ]

        table = Table(summary, colWidths=[3 * inch, 2 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('SPAN', (0, 0), (1, 0)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))

        story.append(table)
        story.append(Spacer(1, 30))

        # Individual property sections
        for i, property_data in enumerate(portfolio_data):
            story.append(Paragraph(f"Property {i + 1}: {property_data.get('address', 'Unknown')}",
                                   self.styles['Heading2']))
            story.extend(self._create_property_section(property_data))

            if 'simulation_results' in property_data:
                story.extend(self._create_results_section(property_data['simulation_results']))

            if i < len(portfolio_data) - 1:  # Add page break except for last property
                story.append(Spacer(1, 50))

        doc.build(story)
        print(f"📄 Portfolio PDF report exported to: {filepath}")
        return filepath