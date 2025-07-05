# Cribb - Real Estate ROI Simulator & Portfolio Manager

A full-stack web application for simulating real estate investments and managing portfolios with advanced design patterns and professional reporting.

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/cribb.git
cd cribb

# Backend setup
cd server
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python init_db.py development

# Frontend setup (new terminal)
cd client
npm install

# Run the application
# Terminal 1 (Backend):
cd server && python app.py

# Terminal 2 (Frontend):
cd client && npm start
```

Visit http://localhost:3000 to start analyzing properties!

## 📚 Documentation

- **[📖 User Guide](docs/user-guide.md)** - Learn how to use Cribb
- **[⚙️ Setup Guide](docs/setup.md)** - Installation and configuration
- **[🔌 API Documentation](docs/api.md)** - REST API reference
- **[🏗️ Architecture Guide](docs/architecture.md)** - Design patterns and code structure
- **[👨‍💻 Development Guide](docs/development.md)** - Contributing and development workflow

## ✨ Features

### 🏠 Property Analysis
- **Multiple Property Types** - Single-family, multifamily, and commercial properties
- **Smart Templates** - Pre-configured assumptions for each property type
- **Real-time Calculations** - ROI, cap rate, cash flow, and cash-on-cash return
- **Customizable Parameters** - Adjust financing, expenses, and growth assumptions

### 📊 Portfolio Management
- **Property Dashboard** - Track multiple properties in one view
- **Performance Comparison** - Side-by-side analysis of investments
- **Portfolio Analytics** - Aggregate metrics and performance trends

### 🔔 Smart Alerts
- **Performance Monitoring** - Automatic alerts for underperforming properties
- **Configurable Thresholds** - Set custom ROI and cap rate minimums
- **Multiple Channels** - Email, database, and webhook notifications

### 📄 Professional Reporting
- **PDF Reports** - Beautiful, professional property analysis reports
- **CSV Exports** - Data exports for further analysis
- **Portfolio Reports** - Comprehensive portfolio summaries

## 🏗️ Architecture

Built with clean architecture and proven design patterns:

- **🏭 Factory Pattern** - Creates property templates with type-specific defaults
- **🎨 Decorator Pattern** - Applies optional costs and features dynamically
- **👀 Observer Pattern** - Sends alerts when properties underperform
- **📋 Strategy Pattern** - Handles different export formats (PDF, CSV)
- **💾 DAO Pattern** - Abstracts database operations
- **🎯 MVC Pattern** - Separates concerns between Flask and React

## 🛠️ Technology Stack

**Frontend:**
- React with modern hooks
- Plotly.js for interactive charts
- Responsive design

**Backend:**
- Python Flask (REST API)
- SQLAlchemy ORM
- ReportLab for PDF generation

**Database:**
- SQLite (development)
- PostgreSQL (production ready)

## 📁 Project Structure

```
Cribb/
├── client/                    # React frontend application
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/            # Page-level components
│   │   └── services/         # API service layer
│   └── public/               # Static assets
│
├── server/                   # Flask backend application
│   ├── models/               # SQLAlchemy data models
│   ├── routes/               # Flask route handlers (Controllers)
│   ├── services/             # Business logic layer
│   ├── dao/                  # Data access objects
│   ├── factories/            # Factory pattern - Property templates
│   ├── decorators/           # Decorator pattern - Optional features
│   ├── notifications/        # Observer pattern - Performance alerts
│   ├── exporters/           # Strategy pattern - Report generation
│   ├── utils/               # Utility functions and helpers
│   ├── config/              # Environment-based configuration
│   └── tests/               # Comprehensive test suites
│
└── docs/                    # Comprehensive documentation
    ├── setup.md             # Installation guide
    ├── user-guide.md        # How to use Cribb
    ├── api.md              # REST API documentation
    ├── architecture.md      # Design patterns and structure
    └── development.md       # Contributing guidelines
```

## 🔧 Configuration

Cribb uses environment-based configuration:

```env
# Development
FLASK_ENV=development
SECRET_KEY=your-secret-key
DEV_DATABASE_URL=sqlite:///cribb_dev.db
CORS_ORIGINS=http://localhost:3000

# Production
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@localhost/cribb_prod
```

## 🧪 Testing

```bash
# Backend tests
cd server
python -m pytest tests/ -v --cov=.

# Frontend tests
cd client
npm test
```

## 📈 Example Usage

### Analyze a Rental Property

```python
from factories import PropertyTemplateFactory

# Create property data
property_data = {
    'property_type': 'single_family_rental',
    'purchase_price': 200000,
    'monthly_rent': 1500,
    'address': '123 Main St'
}

# Prepare data with factory (applies defaults and validation)
prepared_data = PropertyTemplateFactory.prepare_property_data(
    property_data['property_type'], 
    property_data
)

# Results include ROI, cash flow, cap rate, etc.
```

### Set Up Performance Monitoring

```python
from notifications import PerformanceWatcher, EmailNotifier

# Create watcher with email notifications
watcher = PerformanceWatcher()
watcher.add_observer(EmailNotifier())

# Monitor property performance
watcher.check_property_performance(property_data, simulation_results)
# Automatic alerts if ROI < 8% or cap rate < 6%
```

### Generate Professional Reports

```python
from exporters import PDFExporter

# Export property analysis to PDF
exporter = PDFExporter()
report_path = exporter.export({
    'property_data': property_data,
    'simulation_results': results,
    'financial_breakdown': breakdown
}, 'property_analysis.pdf')
```

## 🤝 Contributing

We welcome contributions! Please see our [Development Guide](docs/development.md) for:

- Code style guidelines
- Testing requirements
- Pull request process
- Architecture patterns

## 📄 License

[Add your license here]

## 🆘 Support

- **📖 Documentation**: Check the [docs](docs/) folder
- **🐛 Bug Reports**: [Create an issue](https://github.com/yourusername/cribb/issues)
- **💡 Feature Requests**: [Start a discussion](https://github.com/yourusername/cribb/discussions)
- **❓ Questions**: See our [User Guide](docs/user-guide.md)

## 🎯 Roadmap

- [ ] Market data integration
- [ ] Automated rent estimates
- [ ] Tax calculation integration
- [ ] Multi-user collaboration
- [ ] Mobile application
- [ ] Advanced portfolio analytics

---

**Built with ❤️ for real estate investors**

*Cribb helps you make data-driven investment decisions with professional-grade analysis tools.*