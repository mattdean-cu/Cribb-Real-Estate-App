# Cribb Development Guide

This guide covers everything you need to know to contribute to the Cribb codebase effectively.

## 🚀 Getting Started

### Development Environment Setup

1. **Clone and Setup** (see [Setup Guide](setup.md))
2. **Install Development Tools**
3. **Configure IDE/Editor**
4. **Run Tests**
5. **Make Your First Contribution**

### Required Development Tools

```bash
# Python development
pip install black isort flake8 mypy pytest pytest-cov

# JavaScript development
npm install -g eslint prettier

# Documentation
pip install mkdocs mkdocs-material
```

### IDE Configuration

**VS Code Extensions:**
- Python
- Pylance
- Black Formatter
- ES7+ React/Redux/React-Native snippets
- Prettier - Code formatter

**PyCharm Configuration:**
- Enable Black formatting on save
- Configure Python interpreter to use virtual environment
- Set up run configurations for Flask app

## 📝 Code Style Guidelines

### Python Style (Backend)

**Follow PEP 8** with these specific guidelines:

```python
# Import organization
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

from flask import Flask, request
from sqlalchemy import Column, Integer

from utils.validators import validate_positive_number
from models.property import Property

# Class naming
class PropertyTemplateFactory:
    """Factory for creating property templates."""
    
    def create_template(self, property_type: str) -> BasePropertyTemplate:
        """Create template with proper docstring."""
        pass

# Function naming  
def calculate_monthly_payment(principal: float, rate: float, years: int) -> float:
    """Calculate monthly mortgage payment.
    
    Args:
        principal: Loan amount in dollars
        rate: Annual interest rate as percentage
        years: Loan term in years
        
    Returns:
        Monthly payment amount
        
    Raises:
        ValueError: If any parameter is negative
    """
    pass

# Variable naming
purchase_price = 200000  # Use descriptive names
monthly_rent = 1500      # Avoid abbreviations
roi_percentage = 12.5    # Clear units/context
```

**Type Hints:**
```python
# Always use type hints
from typing import Dict, List, Optional, Union

def process_property_data(
    data: Dict[str, Any], 
    property_type: str
) -> Optional[Dict[str, float]]:
    """Process property data with proper typing."""
    pass
```

### JavaScript Style (Frontend)

**Use Prettier and ESLint** with these conventions:

```javascript
// Component naming (PascalCase)
const PropertySimulator = () => {
  // Hook usage
  const [propertyData, setPropertyData] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  
  // Function naming (camelCase)
  const handlePropertySubmit = async (formData) => {
    try {
      setIsLoading(true);
      const response = await simulateProperty(formData);
      setResults(response.data);
    } catch (error) {
      console.error('Simulation failed:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="property-simulator">
      {/* JSX with proper formatting */}
    </div>
  );
};

// Export default
export default PropertySimulator;
```

### File Naming Conventions

```
# Python files (snake_case)
property_factory.py
rental_template.py
performance_watcher.py

# JavaScript files (camelCase for components, kebab-case for utilities)
PropertyForm.jsx
SimulationResults.jsx
api-client.js
property-utils.js

# Test files
test_property_factory.py
PropertyForm.test.jsx
```

## 🧪 Testing Guidelines

### Backend Testing

**Test Structure:**
```python
# tests/test_property_factory.py
import unittest
from unittest.mock import patch, MagicMock

from factories import PropertyTemplateFactory
from factories.exceptions import UnknownPropertyTypeException

class TestPropertyTemplateFactory(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.factory = PropertyTemplateFactory()
        self.sample_data = {
            'purchase_price': 200000,
            'monthly_rent': 1500,
            'address': '123 Test St'
        }
    
    def test_create_rental_template_success(self):
        """Test successful rental template creation."""
        template = self.factory.create_template('single_family_rental')
        self.assertEqual(template.property_type, 'single_family_rental')
    
    def test_create_unknown_template_raises_exception(self):
        """Test that unknown property type raises exception."""
        with self.assertRaises(UnknownPropertyTypeException):
            self.factory.create_template('unknown_type')
    
    @patch('factories.property_factory.validate_property_data')
    def test_prepare_data_calls_validation(self, mock_validate):
        """Test that data preparation includes validation."""
        template = self.factory.create_template('single_family_rental')
        template.prepare_simulation_data(self.sample_data)
        mock_validate.assert_called_once()

if __name__ == '__main__':
    unittest.main()
```

**Test Categories:**

1. **Unit Tests** - Test individual functions/methods
2. **Integration Tests** - Test component interactions
3. **API Tests** - Test Flask routes end-to-end
4. **Database Tests** - Test SQLAlchemy models and queries

### Frontend Testing

```javascript
// PropertyForm.test.jsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import PropertyForm from './PropertyForm';

describe('PropertyForm', () => {
  const mockOnSubmit = jest.fn();
  
  beforeEach(() => {
    mockOnSubmit.mockClear();
  });
  
  test('renders form fields correctly', () => {
    render(<PropertyForm onSubmit={mockOnSubmit} />);
    
    expect(screen.getByLabelText(/purchase price/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/monthly rent/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /simulate/i })).toBeInTheDocument();
  });
  
  test('submits form with valid data', async () => {
    const user = userEvent.setup();
    render(<PropertyForm onSubmit={mockOnSubmit} />);
    
    await user.type(screen.getByLabelText(/purchase price/i), '200000');
    await user.type(screen.getByLabelText(/monthly rent/i), '1500');
    await user.click(screen.getByRole('button', { name: /simulate/i }));
    
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        purchase_price: 200000,
        monthly_rent: 1500
      });
    });
  });
});
```

### Running Tests

```bash
# Backend tests
cd server
python -m pytest tests/ -v --cov=. --cov-report=html

# Frontend tests
cd client
npm test

# Run specific test files
python -m pytest tests/test_property_factory.py -v
npm test -- PropertyForm.test.jsx
```

## 🏗️ Architecture Patterns

### Adding New Features

When adding features, follow these patterns:

**1. Factory Pattern (New Property Types):**
```python
# 1. Create template
class VacationRentalTemplate(BasePropertyTemplate):
    def get_property_type(self) -> str:
        return "vacation_rental"
    
    def get_required_fields(self) -> List[str]:
        return ["purchase_price", "nightly_rate", "occupancy_rate"]

# 2. Register in factory
PropertyTemplateFactory._templates['vacation_rental'] = VacationRentalTemplate

# 3. Add frontend form support
# 4. Update API documentation
```

**2. Observer Pattern (New Notifications):**
```python
# 1. Create observer
class SlackNotifier(AlertObserver):
    def notify(self, alert: PropertyAlert):
        # Send to Slack webhook
        pass

# 2. Register observer
watcher.add_observer(SlackNotifier(webhook_url))
```

**3. Strategy Pattern (New Export Formats):**
```python
# 1. Create strategy
class ExcelExporter(ExportStrategy):
    def export(self, data: Dict[str, Any], filename: str) -> str:
        # Generate Excel file
        pass

# 2. Register in routing
# 3. Add frontend download option
```

### Database Changes

**1. Model Changes:**
```python
# models/property.py
class Property(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Add new field
    property_manager = db.Column(db.String(100), nullable=True)
```

**2. Migration:**
```bash
# Generate migration
flask db migrate -m "Add property manager field"

# Review generated migration file
# Apply migration
flask db upgrade
```

**3. Update DAO:**
```python
# dao/property_dao.py
class PropertyDAO:
    def create(self, property_data: Dict[str, Any]) -> Property:
        # Handle new field
        property_manager = property_data.get('property_manager')
        # ... rest of creation logic
```

## 🔧 Development Workflow

### Git Workflow

**Branch Naming:**
```bash
feature/property-comparison-tool
bugfix/calculation-rounding-error
hotfix/security-vulnerability
docs/api-documentation-update
```

**Commit Messages:**
```bash
feat: add property comparison functionality
fix: correct ROI calculation for multifamily properties
docs: update API documentation for new endpoints
test: add unit tests for property factory
refactor: extract common validation logic
```

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature-name
   ```

2. **Develop and Test**
   - Write code following style guidelines
   - Add comprehensive tests
   - Update documentation

3. **Pre-commit Checks**
   ```bash
   # Run linting
   black .
   isort .
   flake8 .
   
   # Run tests
   python -m pytest tests/ -v
   npm test
   ```

4. **Create Pull Request**
   - Clear description of changes
   - Link to relevant issues
   - Include screenshots for UI changes

5. **Code Review**
   - Address reviewer feedback
   - Ensure CI passes
   - Update documentation if needed

### Code Review Guidelines

**As a Reviewer:**
- Check for adherence to style guidelines
- Verify test coverage for new features
- Look for security vulnerabilities
- Ensure documentation is updated
- Test the changes locally

**Review Checklist:**
- [ ] Code follows style guidelines
- [ ] Tests are comprehensive and pass
- [ ] Documentation is updated
- [ ] No security vulnerabilities
- [ ] Performance impact considered
- [ ] Backward compatibility maintained

## 📊 Performance Guidelines

### Backend Performance

**Database Queries:**
```python
# Good: Efficient query with specific fields
properties = Property.query.with_entities(
    Property.id, Property.address, Property.monthly_rent
).filter(Property.user_id == user_id).all()

# Bad: Loading full objects when not needed
properties = Property.query.filter(Property.user_id == user_id).all()
```

**API Response Optimization:**
```python
# Use pagination for large datasets
@property_bp.route('/portfolio')
def get_portfolio():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    properties = Property.query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'properties': [p.to_dict() for p in properties.items],
        'pagination': {
            'page': page,
            'pages': properties.pages,
            'total': properties.total
        }
    })
```

### Frontend Performance

**Component Optimization:**
```javascript
// Use React.memo for expensive components
const PropertyCard = React.memo(({ property, onUpdate }) => {
  return (
    <div className="property-card">
      {/* Component content */}
    </div>
  );
});

// Use useMemo for expensive calculations
const SimulationResults = ({ propertyData }) => {
  const calculations = useMemo(() => {
    return calculateROI(propertyData);
  }, [propertyData]);
  
  return <div>{/* Results display */}</div>;
};

// Use useCallback for event handlers
const PropertyForm = ({ onSubmit }) => {
  const handleSubmit = useCallback((formData) => {
    onSubmit(formData);
  }, [onSubmit]);
  
  return <form onSubmit={handleSubmit}>{/* Form content */}</form>;
};
```

**API Call Optimization:**
```javascript
// Implement request debouncing
const useDebounce = (value, delay) => {
  const [debouncedValue, setDebouncedValue] = useState(value);
  
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);
    
    return () => clearTimeout(handler);
  }, [value, delay]);
  
  return debouncedValue;
};

// Use in search functionality
const PropertySearch = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const debouncedSearchTerm = useDebounce(searchTerm, 300);
  
  useEffect(() => {
    if (debouncedSearchTerm) {
      searchProperties(debouncedSearchTerm);
    }
  }, [debouncedSearchTerm]);
};
```

## 🔐 Security Guidelines

### Input Validation

**Backend Validation:**
```python
from utils.validators import validate_positive_number, ValidationError

@property_bp.route('/simulate', methods=['POST'])
def simulate_property():
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('property_type'):
            raise ValidationError('Property type is required')
        
        # Validate data types and ranges
        validate_positive_number(data.get('purchase_price', 0), 'Purchase price')
        validate_positive_number(data.get('monthly_rent', 0), 'Monthly rent')
        
        # Sanitize string inputs
        address = data.get('address', '').strip()[:200]  # Limit length
        
        # Use factory for validation and preparation
        prepared_data = PropertyTemplateFactory.prepare_property_data(
            data['property_type'], data
        )
        
        return jsonify({'success': True, 'data': results})
        
    except ValidationError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Simulation error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500
```

**Frontend Validation:**
```javascript
const validatePropertyForm = (data) => {
  const errors = {};
  
  // Required field validation
  if (!data.purchase_price) {
    errors.purchase_price = 'Purchase price is required';
  } else if (data.purchase_price <= 0) {
    errors.purchase_price = 'Purchase price must be positive';
  }
  
  if (!data.monthly_rent) {
    errors.monthly_rent = 'Monthly rent is required';
  } else if (data.monthly_rent <= 0) {
    errors.monthly_rent = 'Monthly rent must be positive';
  }
  
  // Range validation
  if (data.down_payment_percent && (data.down_payment_percent < 0 || data.down_payment_percent > 100)) {
    errors.down_payment_percent = 'Down payment must be between 0% and 100%';
  }
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};
```

### SQL Injection Prevention

```python
# Good: Using SQLAlchemy ORM (automatically parameterized)
properties = Property.query.filter(
    Property.user_id == user_id,
    Property.purchase_price >= min_price
).all()

# Good: Using parameterized raw SQL if needed
properties = db.session.execute(
    text("SELECT * FROM properties WHERE user_id = :user_id"),
    {'user_id': user_id}
).fetchall()

# Bad: String concatenation (vulnerable to SQL injection)
# properties = db.session.execute(
#     f"SELECT * FROM properties WHERE user_id = {user_id}"
# ).fetchall()
```

### Environment Variables

```python
# Good: Use environment variables for sensitive data
import os
from config import get_config

config = get_config()
secret_key = config.SECRET_KEY  # From environment variable

# Bad: Hardcoded secrets
# secret_key = "hardcoded-secret-key"  # Never do this!
```

## 📚 Documentation Standards

### Code Documentation

**Python Docstrings:**
```python
def calculate_mortgage_payment(principal: float, annual_rate: float, years: int) -> float:
    """Calculate monthly mortgage payment using standard amortization formula.
    
    Args:
        principal: Loan amount in dollars
        annual_rate: Annual interest rate as percentage (e.g., 4.0 for 4%)
        years: Loan term in years
        
    Returns:
        Monthly payment amount in dollars
        
    Raises:
        ValueError: If any parameter is negative or zero
        
    Example:
        >>> calculate_mortgage_payment(200000, 4.0, 30)
        954.83
    """
    if principal <= 0 or annual_rate < 0 or years <= 0:
        raise ValueError("All parameters must be positive")
    
    if annual_rate == 0:
        return principal / (years * 12)
    
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    
    payment = principal * (monthly_rate * (1 + monthly_rate) ** num_payments) / \
              ((1 + monthly_rate) ** num_payments - 1)
    
    return round(payment, 2)
```

**JavaScript Documentation:**
```javascript
/**
 * Calculate property ROI based on income, expenses, and investment
 * @param {number} annualIncome - Total annual rental income
 * @param {number} annualExpenses - Total annual expenses
 * @param {number} initialInvestment - Initial cash investment
 * @returns {number} ROI as percentage
 * @throws {Error} If initial investment is zero
 * 
 * @example
 * calculateROI(18000, 8000, 100000) // Returns 10.0
 */
const calculateROI = (annualIncome, annualExpenses, initialInvestment) => {
  if (initialInvestment === 0) {
    throw new Error('Initial investment cannot be zero');
  }
  
  const netIncome = annualIncome - annualExpenses;
  return (netIncome / initialInvestment) * 100;
};
```

### API Documentation

Always update API documentation when adding/modifying endpoints:

```python
@property_bp.route('/simulate', methods=['POST'])
def simulate_property():
    """
    Simulate property investment returns
    ---
    tags:
      - Properties
    parameters:
      - in: body
        name: property_data
        schema:
          type: object
          required:
            - property_type
            - purchase_price
            - monthly_rent
          properties:
            property_type:
              type: string
              enum: [single_family_rental, multifamily, commercial]
            purchase_price:
              type: number
              minimum: 1
            monthly_rent:
              type: number
              minimum: 1
    responses:
      200:
        description: Simulation results
        schema:
          type: object
          properties:
            success:
              type: boolean
            data:
              type: object
      400:
        description: Validation error
    """
    pass
```

## 🚀 Deployment

### Development Deployment

```bash
# Quick development setup
cd server && python app.py &
cd client && npm start &
```

### Production Deployment Checklist

**Pre-deployment:**
- [ ] All tests pass
- [ ] Security scan complete
- [ ] Performance testing done
- [ ] Database migrations ready
- [ ] Environment variables configured
- [ ] SSL certificates ready

**Deployment Steps:**
```bash
# 1. Backend deployment
cd server
pip install -r requirements.txt
python init_db.py production
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# 2. Frontend build
cd client
npm install
npm run build

# 3. Web server configuration (Nginx)
# Copy build files to web server
# Configure reverse proxy for API
```

### Environment Configuration

**Development (.env):**
```env
FLASK_ENV=development
DEBUG=True
SECRET_KEY=dev-secret-key
DATABASE_URL=sqlite:///cribb_dev.db
```

**Production (.env):**
```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=secure-production-key
DATABASE_URL=postgresql://user:pass@localhost/cribb
```

## 🔍 Debugging

### Backend Debugging

**Logging:**
```python
import logging

# Set up logger
logger = logging.getLogger(__name__)

def simulate_property(property_data):
    logger.info(f"Starting simulation for property type: {property_data.get('property_type')}")
    
    try:
        results = perform_simulation(property_data)
        logger.info(f"Simulation completed successfully, ROI: {results.get('roi')}")
        return results
    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}", exc_info=True)
        raise
```

**Flask Debug Mode:**
```python
# app.py
if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

### Frontend Debugging

**React Developer Tools:**
- Install React DevTools browser extension
- Use Component and Profiler tabs
- Monitor state changes and re-renders

**Console Debugging:**
```javascript
const PropertyForm = ({ onSubmit }) => {
  const [formData, setFormData] = useState({});
  
  // Debug state changes
  useEffect(() => {
    console.log('Form data updated:', formData);
  }, [formData]);
  
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Submitting form:', formData);
    onSubmit(formData);
  };
};
```

### Database Debugging

```python
# Enable SQL query logging
app.config['SQLALCHEMY_ECHO'] = True

# Debug specific queries
import sqlalchemy
sqlalchemy.event.listen(
    sqlalchemy.pool.Pool, "connect", 
    lambda dbapi_conn, connection_record: print("Database connected")
)
```

## 🤝 Contributing Guidelines

### Issue Reporting

**Bug Reports:**
- Use bug report template
- Include steps to reproduce
- Provide environment details
- Include error messages/logs

**Feature Requests:**
- Use feature request template
- Describe use case clearly
- Provide mockups if applicable
- Consider implementation complexity

### Code Contributions

**Before Starting:**
1. Check existing issues and PRs
2. Discuss large changes in issues first
3. Follow coding standards
4. Ensure adequate test coverage

**Development Process:**
1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Update documentation
5. Submit pull request

### Release Process

**Version Numbering:**
- Major: Breaking changes (1.0.0 → 2.0.0)
- Minor: New features (1.0.0 → 1.1.0)
- Patch: Bug fixes (1.0.0 → 1.0.1)

**Release Checklist:**
- [ ] Update version numbers
- [ ] Update CHANGELOG.md
- [ ] Create release notes
- [ ] Tag release in git
- [ ] Deploy to production
- [ ] Verify deployment

## 📊 Monitoring and Maintenance

### Application Monitoring

**Health Checks:**
```python
@app.route('/health')
def health_check():
    """Application health check endpoint."""
    try:
        # Check database connectivity
        db.session.execute('SELECT 1')
        
        # Check file system access
        os.path.exists(app.config['EXPORT_FOLDER'])
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': app.config.get('VERSION', 'unknown')
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

**Performance Monitoring:**
```python
from time import time

def log_performance(func):
    """Decorator to log function execution time."""
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        execution_time = time() - start_time
        
        logger.info(f"{func.__name__} executed in {execution_time:.3f} seconds")
        return result
    return wrapper

@log_performance
def simulate_property(property_data):
    # Simulation logic
    pass
```

### Database Maintenance

**Regular Tasks:**
```bash
# Backup database
python -c "from database import DatabaseManager; DatabaseManager.backup_database()"

# Analyze database performance
python -c "from database import DatabaseManager; print(DatabaseManager.get_table_info())"

# Update statistics (PostgreSQL)
# ANALYZE;
```

## 🎓 Learning Resources

### Design Patterns
- [Refactoring Guru - Design Patterns](https://refactoring.guru/design-patterns)
- [Python Design Patterns](https://python-patterns.guide/)

### Flask Development
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

### React Development
- [React Documentation](https://reactjs.org/docs)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro)

### Real Estate Finance
- [Real Estate Investment Analysis](https://www.investopedia.com/articles/mortgages-real-estate/10/real-estate-investment-analysis.asp)
- [Cap Rate and ROI Calculations](https://www.biggerpockets.com/renewsblog/cap-rate-calculation/)

---

Ready to start contributing? Check out our [open issues](https://github.com/yourusername/cribb/issues) and pick one that matches your skill level!