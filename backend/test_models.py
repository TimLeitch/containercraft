"""Test script for database models."""

import sys
import os
from sqlalchemy.orm import sessionmaker
from models.base import engine
from models.server import ServerInstance, ServerStatus
from models.configuration import ConfigurationTemplate, ConfigurationEntry, ConfigType, UIControlType

# Create session
Session = sessionmaker(bind=engine)


def test_server_instance():
    """Test ServerInstance model."""
    print("Testing ServerInstance model...")
    
    # Test validation
    server = ServerInstance(
        name="Test Server",
        modpack_id=12345,
        modpack_version="1.0.0",
        port=25565,
        rcon_port=25575,
        rcon_password="testpassword123"
    )
    
    errors = server.validate()
    if errors:
        print(f"Validation errors: {errors}")
        return False
    
    print("✓ ServerInstance validation passed")
    
    # Test invalid data
    invalid_server = ServerInstance(
        name="",  # Empty name
        modpack_id=-1,  # Invalid ID
        modpack_version="",  # Empty version
        port=80,  # Invalid port
        rcon_port=80,  # Same as server port
        rcon_password="short"  # Too short
    )
    
    errors = invalid_server.validate()
    if len(errors) != 7:  # Should have 7 validation errors
        print(f"Expected 7 validation errors, got {len(errors)}: {errors}")
        return False
    
    print("✓ ServerInstance validation correctly catches errors")
    
    # Test to_dict
    server_dict = server.to_dict()
    expected_keys = ["id", "name", "modpack_id", "modpack_version", "container_id", 
                     "status", "port", "rcon_port", "created_at", "updated_at", "configuration_id"]
    
    if not all(key in server_dict for key in expected_keys):
        print(f"Missing keys in to_dict output: {set(expected_keys) - set(server_dict.keys())}")
        return False
    
    print("✓ ServerInstance to_dict works correctly")
    return True


def test_configuration_template():
    """Test ConfigurationTemplate model."""
    print("Testing ConfigurationTemplate model...")
    
    # Test validation
    template = ConfigurationTemplate(
        name="Test Template",
        description="A test configuration template",
        modpack_id=12345,
        config_data={"server.properties": {"max-players": 20, "difficulty": "normal"}}
    )
    
    errors = template.validate()
    if errors:
        print(f"Validation errors: {errors}")
        return False
    
    print("✓ ConfigurationTemplate validation passed")
    
    # Test invalid data
    invalid_template = ConfigurationTemplate(
        name="",  # Empty name
        modpack_id=-1,  # Invalid ID
        config_data="not a dict"  # Invalid config data
    )
    
    errors = invalid_template.validate()
    if len(errors) != 3:  # Should have 3 validation errors
        print(f"Expected 3 validation errors, got {len(errors)}: {errors}")
        return False
    
    print("✓ ConfigurationTemplate validation correctly catches errors")
    return True


def test_configuration_entry():
    """Test ConfigurationEntry model."""
    print("Testing ConfigurationEntry model...")
    
    # Test validation
    entry = ConfigurationEntry(
        file_path="server.properties",
        key="max-players",
        value="20",
        value_type=ConfigType.INTEGER,
        ui_control=UIControlType.SLIDER,
        min_value=1,
        max_value=100
    )
    
    errors = entry.validate()
    if errors:
        print(f"Validation errors: {errors}")
        return False
    
    print("✓ ConfigurationEntry validation passed")
    
    # Test typed value conversion
    if entry.typed_value != 20:
        print(f"Expected typed_value to be 20, got {entry.typed_value}")
        return False
    
    print("✓ ConfigurationEntry typed_value conversion works")
    
    # Test boolean conversion
    bool_entry = ConfigurationEntry(
        file_path="server.properties",
        key="pvp",
        value="true",
        value_type=ConfigType.BOOLEAN,
        ui_control=UIControlType.TOGGLE
    )
    
    if bool_entry.typed_value != True:
        print(f"Expected boolean typed_value to be True, got {bool_entry.typed_value}")
        return False
    
    print("✓ ConfigurationEntry boolean conversion works")
    
    # Test dropdown validation
    dropdown_entry = ConfigurationEntry(
        file_path="server.properties",
        key="difficulty",
        value="normal",
        value_type=ConfigType.ENUM,
        ui_control=UIControlType.DROPDOWN,
        options=["peaceful", "easy", "normal", "hard"]
    )
    
    errors = dropdown_entry.validate()
    if errors:
        print(f"Dropdown validation errors: {errors}")
        return False
    
    print("✓ ConfigurationEntry dropdown validation works")
    return True


def test_database_operations():
    """Test basic database operations."""
    print("Testing database operations...")
    
    session = Session()
    
    try:
        # Create a configuration template
        template = ConfigurationTemplate(
            name="Test Template",
            description="Test configuration",
            modpack_id=12345,
            config_data={"test": "data"}
        )
        session.add(template)
        session.commit()
        
        # Create a server instance
        server = ServerInstance(
            name="Test Server",
            modpack_id=12345,
            modpack_version="1.0.0",
            port=25565,
            rcon_port=25575,
            rcon_password="testpassword123",
            configuration_id=template.id
        )
        session.add(server)
        session.commit()
        
        # Create a configuration entry
        entry = ConfigurationEntry(
            server_id=server.id,
            file_path="server.properties",
            key="max-players",
            value="20",
            value_type=ConfigType.INTEGER,
            ui_control=UIControlType.SLIDER,
            min_value=1,
            max_value=100
        )
        session.add(entry)
        session.commit()
        
        # Test relationships
        loaded_server = session.query(ServerInstance).filter_by(name="Test Server").first()
        if not loaded_server:
            print("Failed to load server from database")
            return False
        
        if loaded_server.configuration_template.name != "Test Template":
            print("Server-template relationship not working")
            return False
        
        if len(loaded_server.configuration_entries) != 1:
            print("Server-entries relationship not working")
            return False
        
        print("✓ Database operations and relationships work correctly")
        
        # Cleanup
        session.delete(entry)
        session.delete(server)
        session.delete(template)
        session.commit()
        
        return True
        
    except Exception as e:
        print(f"Database operation failed: {e}")
        session.rollback()
        return False
    finally:
        session.close()


def main():
    """Run all tests."""
    print("Running model tests...\n")
    
    tests = [
        test_server_instance,
        test_configuration_template,
        test_configuration_entry,
        test_database_operations
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
                print("✓ PASSED\n")
            else:
                print("✗ FAILED\n")
        except Exception as e:
            print(f"✗ FAILED with exception: {e}\n")
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    return passed == len(tests)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)