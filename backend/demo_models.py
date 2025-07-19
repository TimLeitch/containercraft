"""Demonstration script showing model usage."""

from sqlalchemy.orm import sessionmaker
from models.base import engine
from models.server import ServerInstance, ServerStatus
from models.configuration import ConfigurationTemplate, ConfigurationEntry, ConfigType, UIControlType
import uuid

# Create session
Session = sessionmaker(bind=engine)


def demo_model_usage():
    """Demonstrate typical model usage patterns."""
    session = Session()

    try:
        print("ContainerCraft Model Demonstration")
        print("=" * 40)

        # 1. Create a configuration template
        print("\n1. Creating configuration template...")
        template = ConfigurationTemplate(
            name="Minecraft Survival Server",
            description="Standard survival server configuration",
            modpack_id=12345,
            config_data={
                "server.properties": {
                    "max-players": 20,
                    "difficulty": "normal",
                    "pvp": True,
                    "spawn-protection": 16
                },
                "bukkit.yml": {
                    "spawn-radius": 16,
                    "view-distance": 10
                }
            }
        )

        # Validate template
        errors = template.validate()
        if errors:
            print(f"Template validation errors: {errors}")
            return

        session.add(template)
        session.commit()
        print(f"✓ Created template: {template.name} (ID: {template.id})")

        # 2. Create a server instance
        print("\n2. Creating server instance...")
        server = ServerInstance(
            name="My Survival Server",
            modpack_id=12345,
            modpack_version="1.19.2",
            port=25565,
            rcon_port=25575,
            rcon_password="secure_password_123",
            configuration_id=template.id
        )

        # Validate server
        errors = server.validate()
        if errors:
            print(f"Server validation errors: {errors}")
            return

        session.add(server)
        session.commit()
        print(f"✓ Created server: {server.name} (ID: {server.id})")

        # 3. Create configuration entries
        print("\n3. Creating configuration entries...")

        config_entries = [
            ConfigurationEntry(
                server_id=server.id,
                file_path="server.properties",
                key="max-players",
                value="20",
                value_type=ConfigType.INTEGER,
                ui_control=UIControlType.SLIDER,
                min_value=1,
                max_value=100,
                description="Maximum number of players allowed on the server"
            ),
            ConfigurationEntry(
                server_id=server.id,
                file_path="server.properties",
                key="difficulty",
                value="normal",
                value_type=ConfigType.ENUM,
                ui_control=UIControlType.DROPDOWN,
                options=["peaceful", "easy", "normal", "hard"],
                description="Server difficulty level"
            ),
            ConfigurationEntry(
                server_id=server.id,
                file_path="server.properties",
                key="pvp",
                value="true",
                value_type=ConfigType.BOOLEAN,
                ui_control=UIControlType.TOGGLE,
                description="Enable player vs player combat"
            )
        ]

        for entry in config_entries:
            errors = entry.validate()
            if errors:
                print(f"Entry validation errors for {entry.key}: {errors}")
                continue

            session.add(entry)
            print(
                f"✓ Added config entry: {entry.key} = {entry.value} ({entry.ui_control.value})")

        session.commit()

        # 4. Demonstrate relationships and queries
        print("\n4. Testing relationships and queries...")

        # Load server with relationships
        loaded_server = session.query(ServerInstance).filter_by(
            name="My Survival Server").first()
        print(f"✓ Loaded server: {loaded_server.name}")
        print(f"  - Template: {loaded_server.configuration_template.name}")
        print(
            f"  - Config entries: {len(loaded_server.configuration_entries)}")

        # Show configuration entries
        for entry in loaded_server.configuration_entries:
            typed_val = entry.typed_value
            print(
                f"  - {entry.key}: {entry.value} (type: {type(typed_val).__name__}, control: {entry.ui_control.value})")

        # 5. Demonstrate model serialization
        print("\n5. Testing model serialization...")

        server_dict = loaded_server.to_dict()
        template_dict = loaded_server.configuration_template.to_dict()

        print(f"✓ Server serialized with {len(server_dict)} fields")
        print(f"✓ Template serialized with {len(template_dict)} fields")

        # 6. Update server status
        print("\n6. Testing server status updates...")

        loaded_server.status = ServerStatus.RUNNING
        session.commit()
        print(f"✓ Updated server status to: {loaded_server.status.value}")
        print(f"  - Is running: {loaded_server.is_running}")
        print(f"  - Is stopped: {loaded_server.is_stopped}")

        print("\n✅ All model operations completed successfully!")

        # Cleanup
        print("\n7. Cleaning up demo data...")
        for entry in config_entries:
            session.delete(entry)
        session.delete(server)
        session.delete(template)
        session.commit()
        print("✓ Demo data cleaned up")

    except Exception as e:
        print(f"❌ Error during demo: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    demo_model_usage()
