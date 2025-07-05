# Cribb Architecture Guide

This document explains the architecture, design patterns, and code organization of the Cribb real estate investment platform.

## 🏗️ Overall Architecture

Cribb follows a **clean architecture** approach with clear separation between layers:

```
┌─────────────────┐    ┌─────────────────┐
│   React Client  │◄──►│  Flask Server   │
│   (Frontend)    │    │   (Backend)     │
└─────────────────┘    └─────────────────┘
                              │
                       ┌─────────────────┐
                       │    Database     │
                       │  (SQLite/Pg)    │
                       └─────────────────┘
```

### Technology Stack

**Frontend (Client):**
- **React** - Component-based UI framework
- **Plotly.js** - Interactive charts and graphs
- **Axios** - HTTP client for API calls

**Backend (Server):**
- **Flask** - Lightweight Python web framework
- **SQLAlchemy** - ORM for database operations
- **ReportLab** - PDF generation library

**Database:**
- **SQLite** - Development database
- **PostgreSQL** - Production database

## 🎨 Design Patterns

Cribb implements several classic design patterns to maintain clean, extensible code:

### 1. Factory Pattern

**Location:** `server/factories/`

**Purpose:** Creates different property simulation templates with type-specific defaults and validation rules.

```python
# Usage
factory = PropertyTemplateFactory()
template = factory.create_template('single_family_rental')
prepared_data = template.prepare_simulation_data(raw_input)
```

**Benefits:**
- Easy to add new property types
- Consistent validation across property types
- Encapsulates property-specific business rules

**Templates:**
- `RentalPropertyTemplate` - Single-family rentals
- `MultifamilyPropertyTemplate` - 2-4 unit properties  
- `CommercialPropertyTemplate` - Commercial properties

### 2. Decorator Pattern

**Location:** `server/decorators/`

**Purpose:** Applies optional costs and features to property simulations dynamically.

```python
# Usage
base_simulation = BasePropertySimulation(property_data)
with_insurance = InsuranceDecorator(base_simulation)
with_management = PropertyManagementDecorator(with_insurance)
final_simulation = with_management.calculate()
```

**Benefits:**
- Add/remove features without changing core simulation
- Mix and match different cost factors
- Runtime configuration of simulation parameters

**Decorators:**
- `InsuranceDecorator` - Property insurance costs
- `PropertyManagementDecorator` - Management fees
- `MaintenanceDecorator` - Maintenance reserves
- `VacancyDecorator` - Vacancy allowances

### 3. Observer Pattern

**Location:** `server/notifications/`

**Purpose:** Sends alerts when properties underperform defined thresholds.

```python
# Usage
watcher = PerformanceWatcher()
watcher.add_observer(EmailNotifier())
watcher.add_observer(DatabaseNotifier())
watcher.check_property_performance(property_data, results)
```

**Benefits:**
- Loosely coupled notification system
- Easy to add new notification channels
- Configurable alert thresholds

**Observers:**
- `EmailNotifier` - Send email alerts
- `DatabaseNotifier` - Store alerts in database
- `WebhookNotifier` - Send to external webhooks

### 4. Strategy Pattern

**Location:** `server/exporters/`

**Purpose:** Handles different export formats (PDF, CSV) using interchangeable strategies.

```python
# Usage
exporter = PDFExporter()
file_path = exporter.export(simulation_data, 'report.pdf')

# Or switch strategies
exporter = CSVExporter() 
file_path = exporter.export(simulation_data, 'data.csv')
```

**Benefits:**
- Easy to add new export formats
- Consistent export interface
- Runtime format selection

**Strategies:**
- `PDFExporter` - Professional PDF reports with charts
- `CSVExporter` - Data exports for analysis

### 5. DAO Pattern

**Location:** `server/dao/`

**Purpose:** Abstracts database operations into maintainable, reusable classes.

```python
# Usage
property_dao = PropertyDAO()
property = property_dao.create(property_data)
portfolio = property_dao.get_by_user(user_id)
property_dao.update(property_id, updates)
```

**Benefits:**
- Database logic separated from business logic
- Easy to test and mock
- Consistent data access patterns

### 6. MVC Pattern

**Purpose:** Separates data, logic, and presentation between Flask and React.

**Model (M):** SQLAlchemy models in `server/models/`
**View (V):** React components in `client/src/components/`
**Controller (C):** Flask routes in `server/routes/`

## 📁 Directory Structure

```
Cribb/
├── client/                    # React frontend
│   ├── src/
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/            # Page-level components
│   │   ├── services/         # API service layer
│   │   └── utils/            # Frontend utilities
│   └── public/               # Static assets
│
└── server/                   # Flask backend
    ├── models/               # SQLAlchemy data models
    ├── routes/               # Flask route handlers
    ├── services/             # Business logic layer
    ├── dao/                  # Data access objects
    ├── factories/            # Factory pattern implementation
    ├── decorators/           # Decorator pattern implementation
    ├── notifications/        # Observer pattern implementation
    ├── exporters/           # Strategy pattern implementation
    ├── utils/               # Utility functions and helpers
    ├── config/              # Configuration management
    ├── tests/               # Test suites
    └── static/              # Generated files (PDFs, etc.)
```

## 🔄 Data Flow

### 1. Property Simulation Flow

```
User Input → Factory Pattern → Decorator Pattern → Simulation Engine → Results
     ↓              ↓               ↓                 ↓              ↓
Frontend      Template       Add Features      Calculate ROI    Display Results
Request       Validation     (Insurance,etc)    Cash Flow       Charts/Tables
              Defaults                          Cap Rate
```

### 2. Alert Flow

```
Simulation Results → Observer Pattern → Notification Strategies → User Alerts
        ↓                  ↓                    ↓                    ↓
    Check Thresholds   Performance         Email/Database/       Email/UI/
    (ROI, Cap Rate)     Watcher            Webhook               Dashboard
```

### 3. Export Flow

```
Portfolio Data → Strategy Pattern → Export Generators → File Output
      ↓               ↓                    ↓              ↓
   Multiple         PDF/CSV            ReportLab/       Download
   Properties       Exporter           CSV Writer       Links
```

## 🧩 Component Interaction

### Backend Components

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Routes    │◄──►│  Services   │◄──►│    DAO      │
│ (Controllers)│    │ (Business   │    │  (Data      │
│             │    │   Logic)    │    │  Access)    │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Factories  │    │ Decorators  │    │   Models    │
│             │    │             │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│Notifications│    │  Exporters  │    │  Database   │
│ (Observers) │    │ (Strategy)  │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Frontend Components

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Pages    │◄──►│ Components  │◄──►│  Services   │
│  (Views)    │    │  (UI Parts) │    │ (API Calls) │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Utils     │    │    State    │    │   Charts    │
│             │    │ Management  │    │ (Plotly.js) │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 🔧 Configuration Management

### Environment-Based Configuration

```
config/
├── base.py          # Common settings
├── development.py   # Development overrides
├── production.py    # Production overrides
└── testing.py       # Test environment settings
```

**Benefits:**
- Environment-specific settings
- Secure secret management
- Easy deployment configuration

### Configuration Hierarchy

1. **Base Config** - Common settings for all environments
2. **Environment Config** - Environment-specific overrides
3. **Environment Variables** - Runtime configuration
4. **Command Line Arguments** - Override any setting

## 🔐 Security Architecture

### Input Validation

```python
# Multi-layer validation
User Input → Frontend Validation → Backend Validation → Database Constraints
     ↓              ↓                    ↓                     ↓
  JavaScript     React Forms        Factory Pattern       SQLAlchemy
  Validation     prop-types         Validators            Field Types
```

### Data Protection

- **Environment Variables** for sensitive configuration
- **SQL Injection Protection** via SQLAlchemy ORM
- **CORS Configuration** for API access control
- **Input Sanitization** at multiple layers

## 📊 Performance Considerations

### Database Optimization

- **Connection Pooling** via SQLAlchemy
- **Query Optimization** with proper indexing
- **Lazy Loading** for related data
- **Caching Strategy** for frequently accessed data

### Frontend Performance

- **Component Memoization** for expensive calculations
- **Code Splitting** for faster initial load
- **API Response Caching** for static data
- **Optimized Chart Rendering** with Plotly.js

### Backend Performance

- **Async Operations** for I/O bound tasks
- **Background Jobs** for report generation
- **Response Compression** for large datasets
- **Database Query Optimization**

## 🧪 Testing Strategy

### Unit Tests

```
tests/
├── test_utils.py        # Utility function tests
├── test_models.py       # Database model tests
├── test_services.py     # Business logic tests
├── test_routes.py       # API endpoint tests
└── test_patterns.py     # Design pattern tests
```

### Integration Tests

- **API Integration** - Full request/response cycles
- **Database Integration** - Multi-table operations
- **Pattern Integration** - Cross-pattern interactions

### Frontend Tests

- **Component Tests** - React component rendering
- **Service Tests** - API service layer
- **E2E Tests** - Full user workflows

## 🚀 Deployment Architecture

### Development

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ React Dev   │    │ Flask Dev   │    │   SQLite    │
│ Server      │◄──►│ Server      │◄──►│  Database   │
│ :3000       │    │ :5000       │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Production

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│    Nginx    │    │  Gunicorn   │    │ PostgreSQL  │
│ (Static +   │◄──►│  (Flask     │◄──►│  Database   │
│  Proxy)     │    │   App)      │    │             │
└─────────────┘    └─────────────┘    └─────────────┘
```

## 🔄 Extension Points

### Adding New Property Types

1. Create new template in `factories/templates/`
2. Register in `PropertyTemplateFactory`
3. Add frontend form handling
4. Update API documentation

### Adding New Export Formats

1. Create new exporter in `exporters/`
2. Implement `ExportStrategy` interface
3. Register in export routing
4. Update frontend download options

### Adding New Notification Channels

1. Create new observer in `notifications/`
2. Implement `AlertObserver` interface
3. Register in performance watcher
4. Configure in application settings

### Adding New Decorators

1. Create new decorator in `decorators/`
2. Implement decorator interface
3. Register in simulation pipeline
4. Add frontend configuration options

## 📈 Monitoring and Observability

### Logging Strategy

```python
# Structured logging with different levels
import logging

logger = logging.getLogger(__name__)

# Application events
logger.info("Property simulation started", extra={
    "property_type": "rental",
    "user_id": user_id
})

# Performance metrics
logger.debug("Simulation completed", extra={
    "execution_time": elapsed_time,
    "property_count": count
})

# Error tracking
logger.error("Simulation failed", extra={
    "error": str(exception),
    "property_data": sanitized_data
})
```

### Health Checks

- **Database Connectivity** - Verify database connection
- **External Services** - Check third-party integrations
- **File System** - Verify export directory access
- **Memory Usage** - Monitor application memory

### Performance Metrics

- **API Response Times** - Track endpoint performance
- **Database Query Times** - Monitor slow queries
- **Export Generation Times** - Track report generation
- **User Activity** - Monitor application usage

## 🎯 Design Principles

### SOLID Principles

- **Single Responsibility** - Each class has one reason to change
- **Open/Closed** - Open for extension, closed for modification
- **Liskov Substitution** - Derived classes must be substitutable
- **Interface Segregation** - Many specific interfaces vs one general
- **Dependency Inversion** - Depend on abstractions, not concretions

### Clean Code Practices

- **Descriptive Naming** - Clear, intention-revealing names
- **Small Functions** - Functions do one thing well
- **No Magic Numbers** - Use named constants
- **Consistent Formatting** - Follow Python PEP 8 style guide
- **Comprehensive Tests** - High test coverage with meaningful tests

## 🚧 Future Architecture Considerations

### Microservices Migration

When scaling beyond current needs:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Property    │    │ Portfolio   │    │ Notification│
│ Service     │◄──►│ Service     │◄──►│ Service     │
└─────────────┘    └─────────────┘    └─────────────┘
       │                  │                  │
       ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Property  │    │  Portfolio  │    │    Alert    │
│  Database   │    │  Database   │    │  Database   │
└─────────────┘    └─────────────┘    └─────────────┘
```

### Event-Driven Architecture

For real-time features:

```
Property Update → Event Bus → Notification Service → Real-time Alerts
      ↓              ↓            ↓                     ↓
  Database       Message       Alert                WebSocket
  Change         Queue         Generation           Connection
```

### Caching Layer

For improved performance:

```
Frontend ↔ CDN ↔ Load Balancer ↔ App Server ↔ Redis ↔ Database
```

This architecture provides a solid foundation for growth while maintaining clean, maintainable code through proven design patterns.