# server/test_imports.py
print("Testing imports...")

try:
    from models import db, User, Property, Simulation
    print("✅ Successfully imported from models package")
    print(f"   db: {db}")
    print(f"   User: {User}")
    print(f"   Property: {Property}")
    print(f"   Simulation: {Simulation}")
except Exception as e:
    print(f"❌ Error importing from models package: {e}")

try:
    from models.user import User
    print("✅ Successfully imported User directly")
except Exception as e:
    print(f"❌ Error importing User directly: {e}")

try:
    from services.auth_service import AuthService
    print("✅ Successfully imported AuthService")
except Exception as e:
    print(f"❌ Error importing AuthService: {e}")

print("Import test complete!")