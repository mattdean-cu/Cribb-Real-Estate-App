from . import db
from datetime import datetime, timezone
from enum import Enum
import uuid


class SimulationStatus(Enum):
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"


class Simulation(db.Model):
    __tablename__ = 'simulations'

    # Primary Key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Basic Information
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    # Simulation Parameters
    analysis_period_years = db.Column(db.Integer, nullable=False, default=10)
    exit_strategy = db.Column(db.String(50), default='hold')  # 'hold', 'sell', 'refinance'

    # Results Storage (JSON as text)
    results_json = db.Column(db.Text)

    # Summary Results for quick access
    total_return = db.Column(db.Numeric(15, 2))
    total_return_percentage = db.Column(db.Numeric(8, 4))
    average_annual_return = db.Column(db.Numeric(8, 4))
    internal_rate_of_return = db.Column(db.Numeric(8, 4))
    net_present_value = db.Column(db.Numeric(15, 2))
    cash_on_cash_return = db.Column(db.Numeric(8, 4))

    # Status and Metadata
    status = db.Column(db.Enum(SimulationStatus), default=SimulationStatus.DRAFT)
    error_message = db.Column(db.Text)  # Store error if simulation fails

    # Foreign Keys
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.String(36), db.ForeignKey('properties.id'), nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', back_populates='simulations')
    property = db.relationship('Property', back_populates='simulations')

    def __repr__(self):
        return f'<Simulation {self.name} - {self.status.value}>'

    def to_dict(self, include_results=False):
        """Convert to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'analysis_period_years': self.analysis_period_years,
            'exit_strategy': self.exit_strategy,
            'status': self.status.value,
            'error_message': self.error_message,
            'user_id': self.user_id,
            'property_id': self.property_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }

        # Add financial results if they exist
        if self.status == SimulationStatus.COMPLETED:
            data.update({
                'total_return': float(self.total_return) if self.total_return else None,
                'total_return_percentage': float(
                    self.total_return_percentage) if self.total_return_percentage else None,
                'average_annual_return': float(self.average_annual_return) if self.average_annual_return else None,
                'internal_rate_of_return': float(
                    self.internal_rate_of_return) if self.internal_rate_of_return else None,
                'net_present_value': float(self.net_present_value) if self.net_present_value else None,
                'cash_on_cash_return': float(self.cash_on_cash_return) if self.cash_on_cash_return else None,
            })

        # Include detailed results if requested
        if include_results and self.results_json:
            import json
            try:
                data['results'] = json.loads(self.results_json)
            except json.JSONDecodeError:
                data['results'] = None

        return data

    def mark_running(self):
        """Mark simulation as running"""
        self.status = SimulationStatus.RUNNING
        self.started_at = datetime.now(timezone.utc)
        self.error_message = None

    def mark_completed(self, results_data):
        """Mark simulation as completed with results"""
        self.status = SimulationStatus.COMPLETED
        self.completed_at = datetime.now(timezone.utc)
        self.error_message = None

        # Store results
        import json
        self.results_json = json.dumps(results_data)

        # Extract summary data for quick access
        if 'summary' in results_data:
            summary = results_data['summary']
            self.total_return = summary.get('total_return')
            self.total_return_percentage = summary.get('total_return_percentage')
            self.average_annual_return = summary.get('average_annual_return')
            self.internal_rate_of_return = summary.get('internal_rate_of_return')
            self.net_present_value = summary.get('net_present_value')
            self.cash_on_cash_return = summary.get('cash_on_cash_return')

    def mark_failed(self, error_message):
        """Mark simulation as failed"""
        self.status = SimulationStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now(timezone.utc)