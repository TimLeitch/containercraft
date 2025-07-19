"""Server instance model."""

from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from .base import Base


class ServerStatus(enum.Enum):
    """Server status enumeration."""
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    REMOVING = "removing"


class ServerInstance(Base):
    """Server instance model representing a deployed Minecraft server."""
    
    __tablename__ = "server_instances"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Basic server information
    name = Column(String(255), nullable=False, unique=True)
    modpack_id = Column(Integer, nullable=False)
    modpack_version = Column(String(50), nullable=False)
    
    # Docker container information
    container_id = Column(String(255), nullable=True)  # Nullable until container is created
    
    # Server status
    status = Column(Enum(ServerStatus), nullable=False, default=ServerStatus.CREATING)
    
    # Network configuration
    port = Column(Integer, nullable=False, unique=True)
    rcon_port = Column(Integer, nullable=False, unique=True)
    rcon_password = Column(String(255), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Foreign key to configuration template (optional)
    configuration_id = Column(UUID(as_uuid=True), ForeignKey("configuration_templates.id"), nullable=True)
    
    # Relationships
    configuration_template = relationship("ConfigurationTemplate", back_populates="servers")
    configuration_entries = relationship("ConfigurationEntry", back_populates="server", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ServerInstance(id={self.id}, name='{self.name}', status='{self.status.value}')>"
    
    @property
    def is_running(self):
        """Check if server is in running state."""
        return self.status == ServerStatus.RUNNING
    
    @property
    def is_stopped(self):
        """Check if server is stopped."""
        return self.status == ServerStatus.STOPPED
    
    def to_dict(self):
        """Convert server instance to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "modpack_id": self.modpack_id,
            "modpack_version": self.modpack_version,
            "container_id": self.container_id,
            "status": self.status.value if self.status else None,
            "port": self.port,
            "rcon_port": self.rcon_port,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "configuration_id": str(self.configuration_id) if self.configuration_id else None
        }
    
    def validate(self):
        """Validate server instance data."""
        errors = []
        
        # Validate name
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Server name cannot be empty")
        elif len(self.name) > 255:
            errors.append("Server name cannot exceed 255 characters")
        
        # Validate modpack_id
        if not isinstance(self.modpack_id, int) or self.modpack_id <= 0:
            errors.append("Modpack ID must be a positive integer")
        
        # Validate modpack_version
        if not self.modpack_version or len(self.modpack_version.strip()) == 0:
            errors.append("Modpack version cannot be empty")
        elif len(self.modpack_version) > 50:
            errors.append("Modpack version cannot exceed 50 characters")
        
        # Validate ports
        if not isinstance(self.port, int) or not (1024 <= self.port <= 65535):
            errors.append("Server port must be between 1024 and 65535")
        
        if not isinstance(self.rcon_port, int) or not (1024 <= self.rcon_port <= 65535):
            errors.append("RCON port must be between 1024 and 65535")
        
        if self.port == self.rcon_port:
            errors.append("Server port and RCON port cannot be the same")
        
        # Validate RCON password
        if not self.rcon_password or len(self.rcon_password) < 8:
            errors.append("RCON password must be at least 8 characters long")
        
        return errors