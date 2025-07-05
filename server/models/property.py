from . import db
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from enum import Enum
import uuid


class PropertyType(Enum):
    SINGLE_FAMILY = "single_family"
    MULTI_FAMILY = "multi_family"
    CONDO = "condo"
    TOWNHOUSE = "townhouse"
    COMMERCIAL = "commercial"
    LAND = "land"


class PropertyStatus(Enum):
    ACTIVE = "active"
    UNDER_CONTRACT = "under_contract"
    SOLD = "sold"
    ARCHIVED = "archived"


class Property(db.Model):
    __tablename__ = 'properties'

    # Primary Key
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Basic Information
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.Enum(PropertyStatus), default=PropertyStatus.ACTIVE)

    # Location
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(20), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    country = db.Column(db.String(50), default='US')

    # Property Details
    property_type = db.Column(db.Enum(PropertyType), nullable=False)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Numeric(3, 1))
    square_feet = db.Column(db.Integer)
    lot_size = db.Column(db.Numeric(10, 2))  # in square feet
    year_built = db.Column(db.Integer)

    # Financial Details - Purchase
    purchase_price = db.Column(db.Numeric(12, 2), nullable=False)
    down_payment = db.Column(db.Numeric(12, 2), nullable=False)
    loan_amount = db.Column(db.Numeric(12, 2), nullable=False)
    interest_rate = db.Column(db.Numeric(5, 4), nullable=False)  # 4.5% stored as 0.0450
    loan_term_years = db.Column(db.Integer, nullable=False, default=30)
    closing_costs = db.Column(db.Numeric(10, 2), default=0)

    # Rental Information
    monthly_rent = db.Column(db.Numeric(10, 2))
    security_deposit = db.Column(db.Numeric(10, 2))
    pet_deposit = db.Column(db.Numeric(10, 2))
    application_fee = db.Column(db.Numeric(8, 2))

    # Operating Expenses (Monthly)
    property_taxes = db.Column(db.Numeric(10, 2), default=0)
    insurance = db.Column(db.Numeric(10, 2), default=0)
    hoa_fees = db.Column(db.Numeric(10, 2), default=0)
    property_management = db.Column(db.Numeric(10, 2), default=0)
    maintenance_reserve = db.Column(db.Numeric(10, 2), default=0)
    utilities = db.Column(db.Numeric(10, 2), default=0)
    advertising = db.Column(db.Numeric(10, 2), default=0)
    legal_accounting = db.Column(db.Numeric(10, 2), default=0)
    other_expenses = db.Column(db.Numeric(10, 2), default=0)

    # Growth Assumptions
    vacancy_rate = db.Column(db.Numeric(5, 4), default=0.05)  # 5% default
    annual_rent_increase = db.Column(db.Numeric(5, 4), default=0.03)  # 3% default
    annual_expense_increase = db.Column(db.Numeric(5, 4), default=0.02)  # 2% default
    property_appreciation = db.Column(db.Numeric(5, 4), default=0.03)  # 3% default

    # Ownership
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)

    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    purchased_date = db.Column(db.Date)

    # Relationships
    owner = db.relationship('User', back_populates='properties')
    simulations = db.relationship('Simulation', back_populates='property', lazy='dynamic',
                                  cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Property {self.name} - {self.address}>'

    @property
    def full_address(self):
        """Get formatted full address"""
        return f"{self.address}, {self.city}, {self.state} {self.zip_code}"

    @property
    def total_monthly_expenses(self):
        """Calculate total monthly operating expenses"""
        expenses = [
            self.property_taxes or 0,
            self.insurance or 0,
            self.hoa_fees or 0,
            self.property_management or 0,
            self.maintenance_reserve or 0,
            self.utilities or 0,
            self.advertising or 0,
            self.legal_accounting or 0,
            self.other_expenses or 0
        ]
        return sum(expenses)

    @property
    def monthly_mortgage_payment(self):
        """Calculate monthly mortgage payment (Principal & Interest)"""
        if not self.loan_amount or self.loan_amount == 0 or not self.interest_rate:
            return Decimal('0')

        principal = float(self.loan_amount)
        monthly_rate = float(self.interest_rate) / 12
        num_payments = self.loan_term_years * 12

        if monthly_rate == 0:
            payment = principal / num_payments
        else:
            payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
                      ((1 + monthly_rate) ** num_payments - 1)

        return Decimal(str(round(payment, 2)))

    @property
    def effective_monthly_rent(self):
        """Calculate effective monthly rent after vacancy"""
        if not self.monthly_rent:
            return Decimal('0')

        vacancy_factor = 1 - (self.vacancy_rate or 0)
        return self.monthly_rent * Decimal(str(vacancy_factor))

    @property
    def monthly_cash_flow(self):
        """Calculate monthly cash flow before taxes"""
        return self.effective_monthly_rent - self.monthly_mortgage_payment - self.total_monthly_expenses

    @property
    def annual_cash_flow(self):
        """Calculate annual cash flow"""
        return self.monthly_cash_flow * 12

    @property
    def cash_on_cash_return(self):
        """Calculate cash-on-cash return percentage"""
        if not self.down_payment or self.down_payment == 0:
            return Decimal('0')

        return (self.annual_cash_flow / self.down_payment) * 100

    @property
    def one_percent_rule(self):
        """Check if property meets 1% rule (monthly rent >= 1% of purchase price)"""
        if not self.monthly_rent or not self.purchase_price:
            return False

        one_percent = self.purchase_price * Decimal('0.01')
        return self.monthly_rent >= one_percent

    @property
    def cap_rate(self):
        """Calculate capitalization rate (annual rent / purchase price)"""
        if not self.monthly_rent or not self.purchase_price or self.purchase_price == 0:
            return Decimal('0')

        annual_rent = self.effective_monthly_rent * 12
        return (annual_rent / self.purchase_price) * 100

    def validate_financial_data(self):
        """Validate financial consistency"""
        errors = []

        # Check down payment vs purchase price
        if self.down_payment > self.purchase_price:
            errors.append("Down payment cannot exceed purchase price")

        # Check loan amount calculation
        expected_loan = self.purchase_price - self.down_payment
        if abs(self.loan_amount - expected_loan) > Decimal('0.01'):
            errors.append("Loan amount should equal purchase price minus down payment")

        # Check interest rate is reasonable
        if self.interest_rate and (self.interest_rate < 0 or self.interest_rate > 1):
            errors.append("Interest rate should be between 0 and 100% (expressed as decimal)")

        # Check year built is reasonable
        current_year = datetime.now().year
        if self.year_built and (self.year_built < 1800 or self.year_built > current_year + 5):
            errors.append("Year built seems unrealistic")

        return errors

    def to_dict(self, include_calculations=True):
        """Convert to dictionary for JSON serialization"""
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code,
            'country': self.country,
            'full_address': self.full_address,
            'property_type': self.property_type.value,
            'bedrooms': self.bedrooms,
            'bathrooms': float(self.bathrooms) if self.bathrooms else None,
            'square_feet': self.square_feet,
            'lot_size': float(self.lot_size) if self.lot_size else None,
            'year_built': self.year_built,
            'purchase_price': float(self.purchase_price),
            'down_payment': float(self.down_payment),
            'loan_amount': float(self.loan_amount),
            'interest_rate': float(self.interest_rate),
            'loan_term_years': self.loan_term_years,
            'closing_costs': float(self.closing_costs) if self.closing_costs else 0,
            'monthly_rent': float(self.monthly_rent) if self.monthly_rent else None,
            'security_deposit': float(self.security_deposit) if self.security_deposit else None,
            'property_taxes': float(self.property_taxes),
            'insurance': float(self.insurance),
            'hoa_fees': float(self.hoa_fees),
            'property_management': float(self.property_management),
            'maintenance_reserve': float(self.maintenance_reserve),
            'utilities': float(self.utilities),
            'other_expenses': float(self.other_expenses),
            'vacancy_rate': float(self.vacancy_rate),
            'annual_rent_increase': float(self.annual_rent_increase),
            'annual_expense_increase': float(self.annual_expense_increase),
            'property_appreciation': float(self.property_appreciation),
            'owner_id': self.owner_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'purchased_date': self.purchased_date.isoformat() if self.purchased_date else None,
        }

        # Add calculated fields if requested
        if include_calculations:
            data.update({
                'total_monthly_expenses': float(self.total_monthly_expenses),
                'monthly_mortgage_payment': float(self.monthly_mortgage_payment),
                'effective_monthly_rent': float(self.effective_monthly_rent),
                'monthly_cash_flow': float(self.monthly_cash_flow),
                'annual_cash_flow': float(self.annual_cash_flow),
                'cash_on_cash_return': float(self.cash_on_cash_return),
                'cap_rate': float(self.cap_rate),
                'one_percent_rule': self.one_percent_rule,
            })

        # Add simulation count
        data['simulations_count'] = self.simulations.count()

        return data