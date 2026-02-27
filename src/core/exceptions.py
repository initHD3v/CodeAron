"""
Custom exceptions untuk CodeAron.
Menggunakan centralized error handling untuk konsistensi.
"""


class AronError(Exception):
    """Base exception untuk semua error di CodeAron."""
    
    def __init__(self, message: str, code: str = "UNKNOWN_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class ModelLoadError(AronError):
    """Error saat loading AI model."""
    
    def __init__(self, message: str, model_path: str = None):
        self.model_path = model_path
        super().__init__(message, code="MODEL_LOAD_ERROR")


class VectorStoreError(AronError):
    """Error saat operasi Vector Store (Qdrant)."""
    
    def __init__(self, message: str, operation: str = None):
        self.operation = operation
        super().__init__(message, code="VECTOR_STORE_ERROR")


class MemoryError(AronError):
    """Error saat operasi Memory (RAG, context)."""
    
    def __init__(self, message: str, memory_type: str = None):
        self.memory_type = memory_type
        super().__init__(message, code="MEMORY_ERROR")


class ToolError(AronError):
    """Error saat eksekusi tool (shell, file, dll)."""
    
    def __init__(self, message: str, tool_name: str = None):
        self.tool_name = tool_name
        super().__init__(message, code="TOOL_ERROR")


class FileOperationError(AronError):
    """Error saat operasi file (read, write, patch)."""
    
    def __init__(self, message: str, file_path: str = None, operation: str = None):
        self.file_path = file_path
        self.operation = operation
        super().__init__(message, code="FILE_OPERATION_ERROR")


class ConfigurationError(AronError):
    """Error saat loading atau validasi konfigurasi."""
    
    def __init__(self, message: str, config_key: str = None):
        self.config_key = config_key
        super().__init__(message, code="CONFIGURATION_ERROR")


class ValidationError(AronError):
    """Error saat validasi code atau project."""
    
    def __init__(self, message: str, validation_type: str = None):
        self.validation_type = validation_type
        super().__init__(message, code="VALIDATION_ERROR")


class CircuitBreakerError(AronError):
    """Error saat circuit breaker dalam keadaan OPEN."""
    
    def __init__(self, message: str, service: str = None):
        self.service = service
        super().__init__(message, code="CIRCUIT_BREAKER_OPEN")


class RecoveryError(AronError):
    """Error saat recovery dari failure."""
    
    def __init__(self, message: str, original_error: Exception = None):
        self.original_error = original_error
        super().__init__(message, code="RECOVERY_ERROR")
