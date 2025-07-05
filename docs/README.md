# Cribb - Real Estate ROI Simulator & Portfolio Manager

## 📋 Documentation Index

Welcome to the Cribb documentation! This real estate investment platform helps you analyze properties, simulate ROI, and manage your investment portfolio.

### Quick Links

- **[Setup Guide](setup.md)** - Get Cribb running on your system
- **[User Guide](user-guide.md)** - How to use the application
- **[API Documentation](api.md)** - REST API endpoints and usage
- **[Architecture Guide](architecture.md)** - Design patterns and code structure
- **[Development Guide](development.md)** - Contributing and development workflow

## 🏠 What is Cribb?

Cribb is a full-stack web application that helps real estate investors:

- **Simulate ROI** for different property types (single-family, multifamily, commercial)
- **Analyze cash flow** with customizable financial parameters
- **Manage portfolios** with multiple properties
- **Get alerts** when properties underperform
- **Export reports** in PDF and CSV formats

## 🎯 Key Features

### Property Simulation
- Multiple property templates (rental, multifamily, commercial)
- Automatic validation and default value application
- Real-time ROI, cap rate, and cash flow calculations
- Customizable financial add-ons (insurance, maintenance, etc.)

### Portfolio Management
- Track multiple properties in one dashboard
- Performance comparison across properties
- Portfolio-level analytics and reporting

### Smart Alerts
- Automatic notifications for underperforming properties
- Configurable thresholds for ROI and cap rate
- Multiple notification channels (email, database, webhooks)

### Export & Reporting
- Professional PDF reports with charts and tables
- CSV exports for data analysis
- Portfolio-level and property-level reports

## 🏗️ Architecture Overview

Cribb is built with modern design patterns and clean architecture:

- **Factory Pattern** - Creates property templates with type-specific defaults
- **Decorator Pattern** - Applies optional costs and features to properties
- **Observer Pattern** - Sends alerts when properties underperform
- **Strategy Pattern** - Handles different export formats (PDF, CSV)
- **DAO Pattern** - Abstracts database operations
- **MVC Pattern** - Separates concerns between Flask backend and React frontend

## 🔧 Technology Stack

**Frontend:**
- React (JavaScript)
- Plotly.js for interactive charts

**Backend:**
- Python Flask (REST API)
- SQLAlchemy ORM
- ReportLab for PDF generation

**Database:**
- SQLite (development)
- PostgreSQL (production ready)

## 📊 Quick Start

1. **Installation**: Follow the [Setup Guide](setup.md)
2. **First Property**: Use the [User Guide](user-guide.md) to add your first property
3. **API Integration**: Check the [API Documentation](api.md) for programmatic access
4. **Development**: See [Development Guide](development.md) to contribute

## 🤝 Contributing

We welcome contributions! Please see our [Development Guide](development.md) for:
- Code style guidelines
- Testing requirements
- Pull request process
- Development environment setup

## 📝 License

[Add your license information here]

## 🆘 Support

- **Issues**: Report bugs and feature requests on GitHub
- **Documentation**: Check this docs folder for detailed guides
- **API Questions**: See the [API Documentation](api.md)

---

*Built with ❤️ for real estate investors*