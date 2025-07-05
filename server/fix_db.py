#!/usr/bin/env python3
"""
Quick database fix script
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from models import db, Property
from models.property import PropertyType
from decimal import Decimal


def fix_database():
    """Fix the property enum issue"""

    # Create Flask app
    app = Flask(__name__)
    instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
    app.config.update({
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{os.path.join(instance_dir, "cribb.db")}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })

    db.init_app(app)

    with app.app_context():
        try:
            # Get all properties
            properties = Property.query.all()
            print(f"Found {len(properties)} properties to fix...")

            for prop in properties:
                print(f"Fixing property: {prop.name}")
                # Delete the problematic property
                db.session.delete(prop)

            db.session.commit()
            print("✅ Deleted problematic properties")

            # Re-create with correct enum
            from models import User
            user = User.query.first()

            if user:
                property_obj = Property(
                    name='Sample Investment Property',
                    address='123 Investment Street',
                    city='Demo City',
                    state='CA',
                    zip_code='12345',
                    property_type=PropertyType.SINGLE_FAMILY,  # Correct enum
                    purchase_price=Decimal('400000'),
                    down_payment=Decimal('80000'),
                    loan_amount=Decimal('320000'),
                    interest_rate=Decimal('0.045'),
                    monthly_rent=Decimal('3200'),
                    property_taxes=Decimal('500'),
                    insurance=Decimal('150'),
                    hoa_fees=Decimal('0'),
                    property_management=Decimal('256'),
                    maintenance_reserve=Decimal('160'),
                    owner_id=user.id
                )
                db.session.add(property_obj)
                db.session.commit()
                print("✅ Created new property with correct enum")

        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()


if __name__ == '__main__':
    fix_database()
    print("🎉 Database fixed! Restart your server.")