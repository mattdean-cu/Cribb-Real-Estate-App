# Cribb Setup Guide

This guide will help you get Cribb running on your local machine or deploy it to production.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** (3.9+ recommended)
- **Node.js 16+** and npm
- **Git** for version control
- **PostgreSQL** (for production deployment)

## 🚀 Quick Start (Development)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/cribb.git
cd cribb
```

### 2. Backend Setup

```bash
# Navigate to server directory
cd server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env

# Edit .env file with your settings
nano .env
```

**Configure your `.env` file:**
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DEV_DATABASE_URL=sqlite:///cribb_dev.db
CORS_ORIGINS=http://localhost:3000
```

### 3. Initialize Database

```bash
# Still in server directory
python init_db.py development
```

### 4. Frontend Setup

```bash
# Navigate to client directory (from project root)
cd client

# Install Node.js dependencies
npm install

# Create environment file
cp .env.example .env

# Edit client .env file
nano .env
```

**Configure your client `.env` file:**
```env
REACT_APP_API_URL=http://localhost:5000/api/v1
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd server
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd client
npm start
```

The application will be available at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## 🏗️ Production Deployment

### 1. Environment Setup

Create a production environment file:

```bash
# In server directory
cp .env.example .env.production
```

**Configure production settings:**
```env
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key
DATABASE_URL=postgresql://username:password@localhost/cribb_prod
CORS_ORIGINS=https://yourdomain.com
```

### 2. Database Setup

```bash
# Install PostgreSQL and create database
createdb cribb_prod

# Run migrations
python init_db.py production
```

### 3. Frontend Build

```bash
cd client
npm run build
```

### 4. Server Configuration

**Option A: Using Gunicorn**
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Option B: Using Docker**
```dockerfile
# Create Dockerfile in server directory
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### 5. Web Server (Nginx)

**Sample Nginx configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Serve React app
    location / {
        root /path/to/client/build;
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Environment mode | `development` | No |
| `SECRET_KEY` | Flask secret key | - | Yes (production) |
| `DATABASE_URL` | Database connection string | SQLite file | No |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` | No |
| `MIN_ROI_THRESHOLD` | Alert threshold for ROI | `8.0` | No |
| `MIN_CAP_RATE_THRESHOLD` | Alert threshold for cap rate | `6.0` | No |

### Database Configuration

**SQLite (Development):**
```env
DEV_DATABASE_URL=sqlite:///cribb_dev.db
```

**PostgreSQL (Production):**
```env
DATABASE_URL=postgresql://user:password@localhost/cribb_prod
```

## 🧪 Testing Setup

### Run Backend Tests

```bash
cd server
python -m pytest tests/ -v
```

### Run Frontend Tests

```bash
cd client
npm test
```

### Run All Tests

```bash
# From project root
./run_tests.sh
```

## 🔍 Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check database status
python db_health.py

# Reset database if needed
python init_db.py development
```

**2. Import Errors**
```bash
# Ensure you're in the right directory and venv is activated
cd server
source venv/bin/activate
python -c "from utils import calculate_annual_roi; print('OK')"
```

**3. Port Conflicts**
```bash
# Check what's running on port 5000
lsof -i :5000

# Or change the port in app.py
app.run(port=5001)
```

**4. CORS Issues**
- Ensure `CORS_ORIGINS` in server `.env` matches your frontend URL
- Check that both frontend and backend are running on expected ports

### Database Issues

**Reset Database:**
```bash
cd server
python -c "from database import reset_database; reset_database()"
```

**Backup Database:**
```bash
python -c "from database import DatabaseManager; DatabaseManager.backup_database()"
```

## 📚 Next Steps

After setup, check out:
- [User Guide](user-guide.md) - Learn how to use Cribb
- [API Documentation](api.md) - Integrate with the REST API
- [Architecture Guide](architecture.md) - Understand the codebase
- [Development Guide](development.md) - Start contributing

## 🆘 Getting Help

If you encounter issues:
1. Check this troubleshooting section
2. Search existing GitHub issues
3. Create a new issue with details about your environment and error messages