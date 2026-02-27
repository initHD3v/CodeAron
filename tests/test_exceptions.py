"""
Unit tests untuk CodeAron exceptions dan error handling.
"""

import unittest
import sys
import os

sys.path.insert(0, os.getcwd())

from src.core.exceptions import (
    AronError,
    ModelLoadError,
    VectorStoreError,
    MemoryError,
    ToolError,
    FileOperationError,
    ConfigurationError,
    ValidationError,
    CircuitBreakerError,
    RecoveryError
)


class TestExceptions(unittest.TestCase):
    
    def test_aron_error_base(self):
        """Test base AronError exception."""
        error = AronError("Test error", "TEST_CODE")
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.code, "TEST_CODE")
        self.assertIn("Test error", str(error))
    
    def test_model_load_error(self):
        """Test ModelLoadError exception."""
        error = ModelLoadError("Model failed to load", "/path/to/model")
        self.assertEqual(error.model_path, "/path/to/model")
        self.assertEqual(error.code, "MODEL_LOAD_ERROR")
    
    def test_vector_store_error(self):
        """Test VectorStoreError exception."""
        error = VectorStoreError("Qdrant connection failed", "connect")
        self.assertEqual(error.operation, "connect")
        self.assertEqual(error.code, "VECTOR_STORE_ERROR")
    
    def test_memory_error(self):
        """Test MemoryError exception."""
        error = MemoryError("Context too large", "short_term")
        self.assertEqual(error.memory_type, "short_term")
        self.assertEqual(error.code, "MEMORY_ERROR")
    
    def test_tool_error(self):
        """Test ToolError exception."""
        error = ToolError("Shell command failed", "shell")
        self.assertEqual(error.tool_name, "shell")
        self.assertEqual(error.code, "TOOL_ERROR")
    
    def test_file_operation_error(self):
        """Test FileOperationError exception."""
        error = FileOperationError("Permission denied", "/path/to/file", "write")
        self.assertEqual(error.file_path, "/path/to/file")
        self.assertEqual(error.operation, "write")
        self.assertEqual(error.code, "FILE_OPERATION_ERROR")
    
    def test_configuration_error(self):
        """Test ConfigurationError exception."""
        error = ConfigurationError("Invalid config key", "model.default")
        self.assertEqual(error.config_key, "model.default")
        self.assertEqual(error.code, "CONFIGURATION_ERROR")
    
    def test_validation_error(self):
        """Test ValidationError exception."""
        error = ValidationError("Syntax error detected", "python")
        self.assertEqual(error.validation_type, "python")
        self.assertEqual(error.code, "VALIDATION_ERROR")
    
    def test_circuit_breaker_error(self):
        """Test CircuitBreakerError exception."""
        error = CircuitBreakerError("Service unavailable", "shell_executor")
        self.assertEqual(error.service, "shell_executor")
        self.assertEqual(error.code, "CIRCUIT_BREAKER_OPEN")
    
    def test_recovery_error(self):
        """Test RecoveryError exception."""
        original = ValueError("Original error")
        error = RecoveryError("Recovery failed", original)
        self.assertEqual(error.original_error, original)
        self.assertEqual(error.code, "RECOVERY_ERROR")
    
    def test_exception_inheritance(self):
        """Test that all custom exceptions inherit from AronError."""
        exceptions = [
            ModelLoadError("test"),
            VectorStoreError("test"),
            MemoryError("test"),
            ToolError("test"),
            FileOperationError("test"),
            ConfigurationError("test"),
            ValidationError("test"),
            CircuitBreakerError("test"),
            RecoveryError("test")
        ]
        
        for exc in exceptions:
            self.assertIsInstance(exc, AronError)


if __name__ == '__main__':
    unittest.main()
