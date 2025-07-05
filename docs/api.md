# Cribb API Documentation

This document describes the REST API endpoints for the Cribb real estate investment platform.

## 🔗 Base URL

- **Development**: `http://localhost:5000/api/v1`
- **Production**: `https://yourdomain.com/api/v1`

## 📋 Response Format

All API responses follow this format:

```json
{
  "success": true,
  "data": { "..." },
  "message": "Optional message",
  "errors": []
}
```

## 🏠 Property Endpoints

### Get Property Types

Get available property types and their templates.

**Endpoint:** `GET /property-types`

**Response:**
```json
{
  "success": true,
  "data": {
    "property_types": ["single_family_rental", "multifamily", "commercial"],
    "template_info": {
      "single_family_rental": {
        "property_type": "single_family_rental",
        "required_fields": ["purchase_price", "monthly_rent", "address"],
        "default_values": {
          "down_payment_percent": 20.0,
          "interest_rate": 4.0,
          "loan_term": 30
        },
        "description": "Single-family rental property with standard residential investment assumptions"
      }
    }
  }
}
```

### Get Template Info

Get detailed information about a specific property template.

**Endpoint:** `GET /template-info/{property_type}`

**Parameters:**
- `property_type` (string): One of `single_family_rental`, `multifamily`, `commercial`

**Example:** `GET /template-info/multifamily`

**Response:**
```json
{
  "success": true,
  "data": {
    "template_info": {
      "property_type": "multifamily",
      "required_fields": ["purchase_price", "monthly_rent", "address", "num_units"],
      "default_values": {
        "down_payment_percent": 25.0,
        "interest_rate": 4.5,
        "loan_term": 30
      },
      "description": "Multifamily property (2-4 units) with higher down payment and management requirements"
    }
  }
}
```

### Simulate Property

Simulate ROI and cash flow for a property.

**Endpoint:** `POST /simulate`

**Request Body:**
```json
{
  "property_type": "single_family_rental",
  "purchase_price": 200000,
  "monthly_rent": 1500,
  "address": "123 Main St, City, State",
  "down_payment_percent": 20,
  "interest_rate": 4.0,
  "loan_term": 30
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "simulation_results": {
      "annual_roi": 12.5,
      "cap_rate": 8.2,
      "monthly_cash_flow": 150.00,
      "annual_cash_flow": 1800.00,
      "cash_on_cash_return": 4.5,
      "total_monthly_income": 1500.00,
      "total_monthly_expenses": 1350.00,
      "mortgage_payment": 954.83,
      "property_taxes": 200.00,
      "insurance": 100.00,
      "maintenance": 95.17
    },
    "property_data": {
      "property_type": "single_family_rental",
      "purchase_price": 200000,
      "monthly_rent": 1500,
      "address": "123 Main St, City, State",
      "down_payment_percent": 20,
      "interest_rate": 4.0,
      "loan_term": 30
    },
    "financial_breakdown": {
      "down_payment": 40000,
      "loan_amount": 160000,
      "closing_costs": 3000,
      "total_initial_investment": 43000
    }
  }
}
```

## 📊 Portfolio Endpoints

### Get Portfolio

Retrieve all properties in the user's portfolio.

**Endpoint:** `GET /portfolio`

**Response:**
```json
{
  "success": true,
  "data": {
    "properties": [
      {
        "id": "prop_1",
        "address": "123 Main St",
        "property_type": "single_family_rental",
        "purchase_price": 200000,
        "monthly_rent": 1500,
        "current_roi": 12.5,
        "monthly_cash_flow": 150.00
      }
    ],
    "portfolio_summary": {
      "total_properties": 1,
      "total_investment": 200000,
      "total_monthly_income": 1500,
      "average_roi": 12.5
    }
  }
}
```

### Add Property to Portfolio

Add a new property to the portfolio.

**Endpoint:** `POST /portfolio/properties`

**Request Body:**
```json
{
  "property_type": "single_family_rental",
  "purchase_price": 200000,
  "monthly_rent": 1500,
  "address": "123 Main St, City, State",
  "down_payment_percent": 20
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "property_id": "prop_123",
    "message": "Property added to portfolio successfully"
  }
}
```

### Update Property

Update an existing property in the portfolio.

**Endpoint:** `PUT /portfolio/properties/{property_id}`

**Request Body:**
```json
{
  "monthly_rent": 1600,
  "maintenance_rate": 1.2
}
```

### Delete Property

Remove a property from the portfolio.

**Endpoint:** `DELETE /portfolio/properties/{property_id}`

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Property removed from portfolio"
  }
}
```

## 🔔 Alert Endpoints

### Get Alerts

Get active performance alerts.

**Endpoint:** `GET /alerts`

**Query Parameters:**
- `property_id` (optional): Filter alerts for specific property

**Response:**
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "property_id": "prop_1",
        "alert_type": "low_roi",
        "message": "Property ROI (6.50%) is below threshold (8.00%)",
        "threshold": 8.0,
        "actual_value": 6.5,
        "severity": "warning",
        "timestamp": "2025-01-15T10:30:00Z",
        "acknowledged": false
      }
    ]
  }
}
```

### Acknowledge Alert

Mark an alert as acknowledged.

**Endpoint:** `POST /alerts/{alert_id}/acknowledge`

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Alert acknowledged"
  }
}
```

## 📄 Export Endpoints

### Export Property Report

Export a property simulation report.

**Endpoint:** `POST /export/property`

**Request Body:**
```json
{
  "property_id": "prop_1",
  "format": "pdf",
  "include_charts": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "download_url": "/static/exports/property_report_20250115_103000.pdf",
    "filename": "property_report_20250115_103000.pdf",
    "format": "pdf"
  }
}
```

### Export Portfolio Report

Export a complete portfolio report.

**Endpoint:** `POST /export/portfolio`

**Request Body:**
```json
{
  "format": "csv",
  "include_summary": true
}
```

## 🔧 Utility Endpoints

### Health Check

Check API health and database connectivity.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "connected",
    "version": "1.0.0",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### Calculate Mortgage

Calculate mortgage payment for given parameters.

**Endpoint:** `POST /calculate/mortgage`

**Request Body:**
```json
{
  "principal": 160000,
  "annual_rate": 4.0,
  "years": 30
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "monthly_payment": 954.83,
    "total_interest": 183739.52,
    "total_paid": 343739.52
  }
}
```

## ❌ Error Responses

All error responses follow this format:

```json
{
  "success": false,
  "message": "Error description",
  "errors": ["Detailed error messages"],
  "error_code": "ERROR_CODE"
}
```

### Common Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| `VALIDATION_ERROR` | Invalid input data | 400 |
| `PROPERTY_NOT_FOUND` | Property doesn't exist | 404 |
| `UNKNOWN_PROPERTY_TYPE` | Invalid property type | 400 |
| `DATABASE_ERROR` | Database operation failed | 500 |
| `EXPORT_ERROR` | Report generation failed | 500 |

### Example Error Response

```json
{
  "success": false,
  "message": "Validation failed",
  "errors": [
    "Purchase price must be a positive number",
    "Monthly rent is required"
  ],
  "error_code": "VALIDATION_ERROR"
}
```

## 🔑 Authentication

*Note: Authentication endpoints will be added in future versions*

Current version operates without authentication for development purposes.

## 📈 Rate Limiting

- **Development**: No rate limiting
- **Production**: 100 requests per minute per IP

## 🔄 Pagination

For endpoints that return lists, use these query parameters:

- `page` (default: 1): Page number
- `limit` (default: 20): Items per page
- `sort` (default: created_at): Sort field
- `order` (default: desc): Sort order (asc/desc)

**Example:** `GET /portfolio?page=2&limit=10&sort=purchase_price&order=desc`

## 🧪 Testing the API

### Using cURL

```bash
# Get property types
curl -X GET http://localhost:5000/api/v1/property-types

# Simulate a property
curl -X POST http://localhost:5000/api/v1/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "property_type": "single_family_rental",
    "purchase_price": 200000,
    "monthly_rent": 1500,
    "address": "123 Test St"
  }'
```

### Using Python

```python
import requests

# Simulate property
response = requests.post('http://localhost:5000/api/v1/simulate', json={
    'property_type': 'single_family_rental',
    'purchase_price': 200000,
    'monthly_rent': 1500,
    'address': '123 Test St'
})

print(response.json())
```

## 📚 SDK and Integrations

*SDKs for popular languages will be available in future versions*

For now, you can use standard HTTP clients to integrate with the API.