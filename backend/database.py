"""Database initialization and management."""

import os
import logging
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models.base import Base, engine
from models import ServerInstance, ConfigurationTemplate, ConfigurationEntry

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize the database by creating all tables."""
    try:
        logger.info("Initializing database...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database initialized successfully")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False


def check_database_exists():
    """Check if database tables exist."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ["server_instances", "configuration_templates", "configuration_entries"]
        existing_tables = [table for table in expected_tables if table in tables]
        
        logger.info(f"Found {len(existing_tables)} of {len(expected_tables)} expected tables")
        return len(existing_tables) == len(expected_tables)
        
    except Exception as e:
        logger.error(f"Failed to check database: {e}")
        return False


def reset_database():
    """Reset the database by dropping and recreating all tables."""
    try:
        logger.warning("Resetting database - all data will be lost!")
        
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.info("Dropped all tables")
        
        # Recreate all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Recreated all tables")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        return False


def get_database_info():
    """Get information about the current database."""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        info = {
            "database_url": str(engine.url),
            "tables": []
        }
        
        for table_name in tables:
            columns = inspector.get_columns(table_name)
            info["tables"].append({
                "name": table_name,
                "columns": [{"name": col["name"], "type": str(col["type"])} for col in columns]
            })
        
        return info
        
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return None


if __name__ == "__main__":
    """Run database initialization when script is executed directly."""
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "init":
            success = init_database()
            sys.exit(0 if success else 1)
            
        elif command == "reset":
            success = reset_database()
            sys.exit(0 if success else 1)
            
        elif command == "check":
            exists = check_database_exists()
            print(f"Database properly initialized: {exists}")
            sys.exit(0 if exists else 1)
            
        elif command == "info":
            info = get_database_info()
            if info:
                print(f"Database URL: {info['database_url']}")
                print(f"Tables: {len(info['tables'])}")
                for table in info["tables"]:
                    print(f"  - {table['name']}: {len(table['columns'])} columns")
            sys.exit(0 if info else 1)
            
        else:
            print(f"Unknown command: {command}")
            print("Available commands: init, reset, check, info")
            sys.exit(1)
    else:
        # Default behavior: initialize if not exists
        if not check_database_exists():
            success = init_database()
            sys.exit(0 if success else 1)
        else:
            logger.info("Database already initialized")
            sys.exit(0)