"""
Error codes and exception classes for the sidecar.

All errors follow a consistent structure with:
- code: Stable symbolic error code (e.g., E_SCENE_NOT_FOUND)
- message: Human-readable error message
- details: Additional context (optional)
- retryable: Whether the operation can be safely retried
"""

from typing import Dict, Any, Optional


class SidecarError(Exception):
    """Base exception for all sidecar errors."""
    
    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        retryable: bool = False,
    ):
        self.code = code
        self.message = message
        self.details = details or {}
        self.retryable = retryable
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format for responses."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "retryable": self.retryable,
        }


class CommandError(SidecarError):
    """Error related to command execution."""
    pass


class ValidationError(SidecarError):
    """Error related to parameter validation."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="E_INVALID_PARAMS",
            message=message,
            details=details,
            retryable=False,
        )


class TimeoutError(SidecarError):
    """Command execution timeout."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="E_TIMEOUT",
            message=message,
            details=details,
            retryable=True,
        )


class SceneNotFoundError(SidecarError):
    """Scene does not exist."""
    
    def __init__(self, scene_name: str):
        super().__init__(
            code="E_SCENE_NOT_FOUND",
            message=f"Scene '{scene_name}' not found",
            details={"scene_name": scene_name},
            retryable=False,
        )


class CollectionNotFoundError(SidecarError):
    """Collection does not exist."""
    
    def __init__(self, collection_name: str):
        super().__init__(
            code="E_COLLECTION_MISSING",
            message=f"Collection '{collection_name}' not found",
            details={"collection_name": collection_name},
            retryable=False,
        )


class ExportError(SidecarError):
    """Export operation failed."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="E_EXPORT_FAIL",
            message=message,
            details=details,
            retryable=True,
        )


class UnsupportedVersionError(SidecarError):
    """Unsupported protocol version."""
    
    def __init__(self, version: str):
        super().__init__(
            code="E_UNSUPPORTED_VERSION",
            message=f"Unsupported protocol version: {version}",
            details={"version": version},
            retryable=False,
        )


# Error code constants
ERROR_CODES = {
    "E_INVALID_PARAMS": "Invalid command parameters",
    "E_TIMEOUT": "Command execution timeout",
    "E_SCENE_NOT_FOUND": "Scene not found",
    "E_COLLECTION_MISSING": "Collection not found",
    "E_EXPORT_FAIL": "Export operation failed",
    "E_UNSUPPORTED_VERSION": "Unsupported protocol version",
    "E_UNKNOWN_COMMAND": "Unknown command",
    "E_REDIS_ERROR": "Redis connection error",
    "E_INTERNAL": "Internal sidecar error",
}

