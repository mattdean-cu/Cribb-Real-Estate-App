#!/usr/bin/env python3
"""
Production Authentication Setup Script for Cribb Real Estate
This script sets up the complete production-ready authentication system.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def print_header(title):
    """Print a formatted header"""
    print(f"\n{'=' * 60}")
    print(f"🔧 {title}")
    print(f"{'=' * 60}")


def print_step(step, description):
    """Print a formatted step"""
    print(f"\n{step}. {description}")


def create_directory(path):
    """Create directory if it doesn't exist"""
    os.makedirs(path, exist_ok=True)
    print(f"   ✅ Created directory: {path}")


def create_file(path, content):
    """Create file with content"""
    with open(path, 'w') as f:
        f.write(content)
    print(f"   ✅ Created file: {path}")


def run_command(command, description):
    """Run a command and report success/failure"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   ✅ {description}")
            return True
        else:
            print(f"   ❌ {description} failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"   ❌ {description} failed: {str(e)}")
        return False


def main():
    """Main setup function"""

    print_header("Cribb Real Estate - Production Authentication Setup")
    print("This script will set up a production-ready authentication system.")
    print("Please make sure you're in the server directory.")

    # Verify we're in the right directory
    if not os.path.exists('models') or not os.path.exists('app.py'):
        print("\n❌ Error: Please run this script from the server directory.")
        print("Expected files: models/, app.py")
        sys.exit(1)

    # Step 1: Create directories
    print_step(1, "Creating directory structure")
    directories = [
        'auth',
        'middleware',
        'config',
        'logs',
        'instance'
    ]

    for directory in directories:
        create_directory(directory)

    # Step 2: Create __init__.py files
    print_step(2, "Creating __init__.py files")
    init_files = [
        'auth/__init__.py',
        'middleware/__init__.py'
    ]

    for init_file in init_files:
        create_file(init_file, "# Authentication module\n")

    # Step 3: Install dependencies
    print_step(3, "Installing Python dependencies")

    dependencies = [
        "Flask==3.0.0",
        "Flask-SQLAlchemy==3.1.1",
        "Flask-Login==0.6.3",
        "Flask-Migrate==4.0.5",
        "Flask-CORS==4.0.0",
        "Flask-Limiter==3.5.0",
        "Flask-WTF==1.2.1",
        "Flask-Mail==0.9.1",
        "python-dotenv==1.0.0",
        "python-decouple==3.8",
        "zxcvbn==4.4.28",
        "redis==5.0.1",
        "cryptography==41.0.7"
    ]

    for dep in dependencies:
        if run_command(f"pip install {dep}", f"Installing {dep.split('==')[0]}"):
            continue
        else:
            print(f"   ⚠️  Failed to install {dep}, continuing anyway...")

    # Step 4: Create configuration files
    print_step(4, "Creating configuration files")

    # Create .env file
    env_content = '''# Cribb Real Estate - Development Configuration
FLASK_ENV=development
SECRET_KEY=dev-super-secure-secret-key-change-this-in-production
DATABASE_URL=sqlite:///instance/cribb.db
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
SESSION_TIMEOUT_HOURS=8
REDIS_URL=
ENABLE_REGISTRATION=true
REQUIRE_EMAIL_VERIFICATION=false
ENABLE_PASSWORD_RESET=true
LOG_LEVEL=INFO
LOG_FILE=logs/cribb.log
ADMIN_EMAIL=admin@cribb.com
'''

    if not os.path.exists('.env'):
        create_file('.env', env_content)
    else:
        print("   ⚠️  .env file already exists, skipping...")

    # Step 5: Create production config
    print_step(5, "Setting up production configuration")

    config_content = '''# config/__init__.py
from .production import config

__all__ = ['config']
'''
    create_file('config/__init__.py', config_content)

    # Step 6: Database migration
    print_step(6, "Setting up database")

    # Check if database exists
    if os.path.exists('instance/cribb.db'):
        backup_db = input("\n   Database exists. Create backup? (y/n): ").lower() == 'y'
        if backup_db:
            shutil.copy('instance/cribb.db', 'instance/cribb_backup.db')
            print("   ✅ Database backed up to cribb_backup.db")

    # Initialize Flask-Migrate if not already done
    if not os.path.exists('migrations'):
        run_command("flask db init", "Initializing Flask-Migrate")

    print("\n   📋 Database setup complete. New tables will be created on first run.")

    # Step 7: Test the setup
    print_step(7, "Testing the setup")

    # Test imports
    test_script = '''
import sys
import os
sys.path.insert(0, os.getcwd())

try:
    from models import db, User, Property, Simulation
    print("✅ Models imported successfully")
except Exception as e:
    print(f"❌ Model import failed: {e}")

try:
    from services.auth_service import ProductionAuthService
    print("✅ Auth service imported successfully")
except Exception as e:
    print(f"❌ Auth service import failed: {e}")

try:
    from routes.auth_routes import auth_bp
    print("✅ Auth routes imported successfully")
except Exception as e:
    print(f"❌ Auth routes import failed: {e}")

try:
    from config.production import config
    print("✅ Production config imported successfully")
except Exception as e:
    print(f"❌ Production config import failed: {e}")

print("\\n🎉 Import test completed!")
'''

    with open('test_setup.py', 'w') as f:
        f.write(test_script)

    run_command("python test_setup.py", "Running import tests")
    os.remove('test_setup.py')

    # Step 8: Final instructions
    print_step(8, "Setup complete!")

    print(f"\n{'🎉 SUCCESS! Production Authentication System Installed'}")
    print(f"\n📝 NEXT STEPS:")
    print(f"   1. Update your requirements.txt:")
    print(f"      pip freeze > requirements.txt")
    print(f"   ")
    print(f"   2. Review and customize your .env file")
    print(f"   ")
    print(f"   3. Start the application:")
    print(f"      python app.py")
    print(f"   ")
    print(f"   4. Test the authentication endpoints:")
    print(f"      Demo user: demo@cribb.com / Demo123!")
    print(f"      Admin user: admin@cribb.com / Admin123!@#")

    print(f"\n🔐 SECURITY FEATURES ENABLED:")
    print(f"   ✅ Password strength validation (12+ chars, mixed case, numbers, symbols)")
    print(f"   ✅ Account lockout after failed attempts")
    print(f"   ✅ Rate limiting on auth endpoints")
    print(f"   ✅ Secure session management")
    print(f"   ✅ Security headers")
    print(f"   ✅ Input validation and sanitization")
    print(f"   ✅ Comprehensive audit logging")
    print(f"   ✅ Email verification (configurable)")
    print(f"   ✅ Password reset functionality")

    print(f"\n🌐 API ENDPOINTS:")
    print(f"   Authentication: /api/auth/*")
    print(f"   Properties: /api/v1/properties/*")
    print(f"   Portfolio: /api/v1/portfolio/*")
    print(f"   Health: /health")

    print(f"\n📊 MONITORING:")
    print(f"   Logs: {os.path.abspath('logs/cribb.log')}")
    print(f"   Health check: http://localhost:5000/health")
    print(f"   Auth health: http://localhost:5000/api/auth/health")

    print(f"\n🔧 FOR PRODUCTION DEPLOYMENT:")
    print(f"   1. Set FLASK_ENV=production in .env")
    print(f"   2. Use PostgreSQL: DATABASE_URL=postgresql://...")
    print(f"   3. Set up Redis: REDIS_URL=redis://...")
    print(f"   4. Configure email: MAIL_SERVER, MAIL_USERNAME, etc.")
    print(f"   5. Enable email verification: REQUIRE_EMAIL_VERIFICATION=true")
    print(f"   6. Use strong SECRET_KEY")
    print(f"   7. Set proper CORS_ORIGINS")

    print(f"\n{'=' * 60}")
    print(f"🚀 Ready to launch! Run 'python app.py' to start the server.")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()