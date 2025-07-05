# Database Migrations

This directory contains database migration files for the Cribb application.

## Using Flask-Migrate

### Initial Setup
```bash
# Initialize migrations (run once)
flask db init

# Create first migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade


# After modifying models, create a new migration
flask db migrate -m "Description of changes"

# Review the generated migration file in migrations/versions/

# Apply the migration
flask db upgrade


# Show current migration status
flask db current

# Show migration history
flask db history

# Downgrade to previous migration
flask db downgrade

# Upgrade to specific migration
flask db upgrade <revision>


# Initialize database tables
flask init-db

# Reset database (careful!)
flask reset-db

# Backup database
flask backup-db

# Show database info
flask db-info