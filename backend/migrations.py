"""Database migration system for ContainerCraft."""

import os
import logging
from datetime import datetime
from sqlalchemy import text, inspect
from models.base import engine

logger = logging.getLogger(__name__)


class Migration:
    """Base migration class."""
    
    def __init__(self, version: str, description: str):
        self.version = version
        self.description = description
        self.timestamp = datetime.now()
    
    def up(self):
        """Apply the migration."""
        raise NotImplementedError("Migration must implement up() method")
    
    def down(self):
        """Rollback the migration."""
        raise NotImplementedError("Migration must implement down() method")


class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self):
        self.migrations = []
        self._ensure_migration_table()
    
    def _ensure_migration_table(self):
        """Create migration tracking table if it doesn't exist."""
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version VARCHAR(50) PRIMARY KEY,
                    description TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
    
    def register_migration(self, migration: Migration):
        """Register a migration."""
        self.migrations.append(migration)
        # Sort by version to ensure proper order
        self.migrations.sort(key=lambda m: m.version)
    
    def get_applied_migrations(self):
        """Get list of applied migrations."""
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version FROM schema_migrations ORDER BY version"))
            return [row[0] for row in result]
    
    def get_pending_migrations(self):
        """Get list of pending migrations."""
        applied = set(self.get_applied_migrations())
        return [m for m in self.migrations if m.version not in applied]
    
    def apply_migration(self, migration: Migration):
        """Apply a single migration."""
        try:
            logger.info(f"Applying migration {migration.version}: {migration.description}")
            
            with engine.begin() as conn:
                # Apply the migration
                migration.up()
                
                # Record the migration
                conn.execute(text("""
                    INSERT INTO schema_migrations (version, description) 
                    VALUES (:version, :description)
                """), {
                    "version": migration.version,
                    "description": migration.description
                })
            
            logger.info(f"Successfully applied migration {migration.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply migration {migration.version}: {e}")
            return False
    
    def rollback_migration(self, migration: Migration):
        """Rollback a single migration."""
        try:
            logger.info(f"Rolling back migration {migration.version}: {migration.description}")
            
            with engine.begin() as conn:
                # Rollback the migration
                migration.down()
                
                # Remove the migration record
                conn.execute(text("""
                    DELETE FROM schema_migrations WHERE version = :version
                """), {"version": migration.version})
            
            logger.info(f"Successfully rolled back migration {migration.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rollback migration {migration.version}: {e}")
            return False
    
    def migrate_up(self):
        """Apply all pending migrations."""
        pending = self.get_pending_migrations()
        
        if not pending:
            logger.info("No pending migrations")
            return True
        
        logger.info(f"Applying {len(pending)} pending migrations")
        
        for migration in pending:
            if not self.apply_migration(migration):
                return False
        
        logger.info("All migrations applied successfully")
        return True
    
    def migrate_down(self, target_version: str = None):
        """Rollback migrations to target version."""
        applied = self.get_applied_migrations()
        
        if not applied:
            logger.info("No migrations to rollback")
            return True
        
        # Find migrations to rollback
        to_rollback = []
        for version in reversed(applied):
            if target_version and version == target_version:
                break
            
            # Find the migration object
            migration = next((m for m in self.migrations if m.version == version), None)
            if migration:
                to_rollback.append(migration)
        
        if not to_rollback:
            logger.info("No migrations to rollback")
            return True
        
        logger.info(f"Rolling back {len(to_rollback)} migrations")
        
        for migration in to_rollback:
            if not self.rollback_migration(migration):
                return False
        
        logger.info("Migrations rolled back successfully")
        return True
    
    def status(self):
        """Show migration status."""
        applied = set(self.get_applied_migrations())
        
        print("Migration Status:")
        print("================")
        
        for migration in self.migrations:
            status = "APPLIED" if migration.version in applied else "PENDING"
            print(f"{migration.version}: {migration.description} [{status}]")
        
        if not self.migrations:
            print("No migrations registered")


# Example migration for future use
class InitialMigration(Migration):
    """Initial database schema migration."""
    
    def __init__(self):
        super().__init__("001", "Initial database schema")
    
    def up(self):
        """Create initial tables."""
        # This would be handled by SQLAlchemy create_all in our case
        pass
    
    def down(self):
        """Drop all tables."""
        # This would be handled by SQLAlchemy drop_all
        pass


# Global migration manager instance
migration_manager = MigrationManager()

# Register initial migration
migration_manager.register_migration(InitialMigration())


if __name__ == "__main__":
    """Run migration commands."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "up":
            success = migration_manager.migrate_up()
            sys.exit(0 if success else 1)
            
        elif command == "down":
            target = sys.argv[2] if len(sys.argv) > 2 else None
            success = migration_manager.migrate_down(target)
            sys.exit(0 if success else 1)
            
        elif command == "status":
            migration_manager.status()
            sys.exit(0)
            
        else:
            print(f"Unknown command: {command}")
            print("Available commands: up, down [target_version], status")
            sys.exit(1)
    else:
        print("Usage: python migrations.py <command>")
        print("Commands:")
        print("  up                    - Apply all pending migrations")
        print("  down [target_version] - Rollback migrations")
        print("  status                - Show migration status")
        sys.exit(1)