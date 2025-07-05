#!/usr/bin/env python3
"""
Development server runner for Cribb backend
"""

import os
from dotenv import load_dotenv


def main():
    """Main function to run the development server"""

    # Load environment variables
    load_dotenv()

    # Import after loading env
    from app import create_app
    from services.database_service import (
        create_tables, seed_database,
        check_database_connection, get_database_info
    )

    # Create app
    app = create_app('development')

    with app.app_context():
        print("🚀 Starting Cribb Backend Development Server")
        print("=" * 50)

        # Check database connection
        print("📊 Checking database connection...")
        if check_database_connection():
            print("✅ Database connection successful!")

            # Get database info
            db_info = get_database_info()
            print(f"📋 Database Info:")
            print(f"   - Users: {db_info.get('users', 0)}")
            print(f"   - Properties: {db_info.get('properties', 0)}")
            print(f"   - Simulations: {db_info.get('simulations', 0)}")

        else:
            print("❌ Database connection failed!")
            print("🔧 Creating database tables...")
            create_tables()

            print("🌱 Seeding database with sample data...")
            seed_database()

    print("\n🌐 API Endpoints Available:")
    print("   - Health Check: http://localhost:5000/health")
    print("   - API Info: http://localhost:5000/api/info")
    print("   - Users: http://localhost:5000/api/v1/users")
    print("   - Properties: http://localhost:5000/api/v1/properties")
    print("   - Simulations: http://localhost:5000/api/v1/simulations")

    print("\n💡 Quick Test Commands:")
    print("   curl http://localhost:5000/health")
    print("   curl http://localhost:5000/api/info")
    print("   curl http://localhost:5000/api/v1/users")

    print("\n🔥 Starting Flask development server...")
    print("=" * 50)

    # Run the application
    app.run(
        debug=True,
        port=int(os.getenv('PORT', 5000)),
        host=os.getenv('HOST', '127.0.0.1')
    )


if __name__ == '__main__':
    main()