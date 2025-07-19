"""Configuration models for templates and entries."""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON, ForeignKey, Float, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from .base import Base


class ConfigType(enum.Enum):
    """Configuration value type enumeration."""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ENUM = "enum"


class UIControlType(enum.Enum):
    """UI control type enumeration."""
    INPUT = "input"
    SLIDER = "slider"
    TOGGLE = "toggle"
    DROPDOWN = "dropdown"
    TEXTAREA = "textarea"


class ConfigurationTemplate(Base):
    """Configuration template model for saving and reusing server configurations."""
    
    __tablename__ = "configuration_templates"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    modpack_id = Column(Integer, nullable=False)
    
    # Configuration data stored as JSON
    config_data = Column(JSON, nullable=False)
    
    # Template metadata
    is_default = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    servers = relationship("ServerInstance", back_populates="configuration_template")
    
    def __repr__(self):
        return f"<ConfigurationTemplate(id={self.id}, name='{self.name}', modpack_id={self.modpack_id})>"
    
    def to_dict(self):
        """Convert configuration template to dictionary."""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "modpack_id": self.modpack_id,
            "config_data": self.config_data,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    def validate(self):
        """Validate configuration template data."""
        errors = []
        
        # Validate name
        if not self.name or len(self.name.strip()) == 0:
            errors.append("Template name cannot be empty")
        elif len(self.name) > 255:
            errors.append("Template name cannot exceed 255 characters")
        
        # Validate modpack_id
        if not isinstance(self.modpack_id, int) or self.modpack_id <= 0:
            errors.append("Modpack ID must be a positive integer")
        
        # Validate config_data
        if not isinstance(self.config_data, dict):
            errors.append("Configuration data must be a valid JSON object")
        
        # Validate description length if provided
        if self.description and len(self.description) > 1000:
            errors.append("Description cannot exceed 1000 characters")
        
        return errors


class ConfigurationEntry(Base):
    """Individual configuration entry for a server."""
    
    __tablename__ = "configuration_entries"
    
    # Primary key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign key to server
    server_id = Column(UUID(as_uuid=True), ForeignKey("server_instances.id"), nullable=False)
    
    # Configuration file information
    file_path = Column(String(500), nullable=False)
    key = Column(String(255), nullable=False)
    
    # Configuration value and metadata
    value = Column(String(1000), nullable=False)
    value_type = Column(Enum(ConfigType), nullable=False)
    
    # UI control information
    ui_control = Column(Enum(UIControlType), nullable=False)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    options = Column(JSON, nullable=True)  # For dropdown options
    
    # Metadata
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    
    # Relationships
    server = relationship("ServerInstance", back_populates="configuration_entries")
    
    # Composite unique constraint on server_id, file_path, and key
    __table_args__ = (
        {"sqlite_autoincrement": True}
    )
    
    def __repr__(self):
        return f"<ConfigurationEntry(id={self.id}, key='{self.key}', value='{self.value}')>"
    
    def to_dict(self):
        """Convert configuration entry to dictionary."""
        return {
            "id": str(self.id),
            "server_id": str(self.server_id),
            "file_path": self.file_path,
            "key": self.key,
            "value": self.value,
            "value_type": self.value_type.value,
            "ui_control": self.ui_control.value,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "options": self.options,
            "description": self.description,
            "category": self.category
        }
    
    @property
    def typed_value(self):
        """Get the value converted to its proper type."""
        if self.value_type == ConfigType.BOOLEAN:
            return self.value.lower() in ('true', '1', 'yes', 'on')
        elif self.value_type == ConfigType.INTEGER:
            return int(self.value)
        elif self.value_type == ConfigType.FLOAT:
            return float(self.value)
        else:
            return self.value
    
    def set_typed_value(self, value):
        """Set the value from a typed value."""
        if self.value_type == ConfigType.BOOLEAN:
            self.value = str(bool(value)).lower()
        else:
            self.value = str(value)
    
    def validate(self):
        """Validate configuration entry data."""
        errors = []
        
        # Validate file_path
        if not self.file_path or len(self.file_path.strip()) == 0:
            errors.append("File path cannot be empty")
        elif len(self.file_path) > 500:
            errors.append("File path cannot exceed 500 characters")
        
        # Validate key
        if not self.key or len(self.key.strip()) == 0:
            errors.append("Configuration key cannot be empty")
        elif len(self.key) > 255:
            errors.append("Configuration key cannot exceed 255 characters")
        
        # Validate value
        if not self.value:
            errors.append("Configuration value cannot be empty")
        elif len(self.value) > 1000:
            errors.append("Configuration value cannot exceed 1000 characters")
        
        # Validate value type consistency
        try:
            typed_value = self.typed_value
        except (ValueError, TypeError) as e:
            errors.append(f"Value '{self.value}' is not valid for type {self.value_type.value}: {e}")
        
        # Validate numeric ranges
        if self.value_type in [ConfigType.INTEGER, ConfigType.FLOAT]:
            if self.min_value is not None and self.max_value is not None:
                if self.min_value >= self.max_value:
                    errors.append("Minimum value must be less than maximum value")
        
        # Validate dropdown options
        if self.ui_control == UIControlType.DROPDOWN:
            if not self.options or not isinstance(self.options, list) or len(self.options) == 0:
                errors.append("Dropdown control must have at least one option")
            elif self.value not in self.options:
                errors.append(f"Value '{self.value}' is not in the list of valid options")
        
        return errors