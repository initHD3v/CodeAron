"""
Configuration Manager untuk CodeAron.
Mengelola konfigurasi project-specific melalui .codearon/config.yaml
"""

import os
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.core.exceptions import ConfigurationError
import logging

logger = logging.getLogger("ConfigManager")


class ProjectConfig:
    """Manages project-specific configuration for CodeAron."""
    
    DEFAULT_CONFIG = {
        "version": "1.0",
        "model": {
            "default": "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit",
            "fallback": "mlx-community/DeepSeek-Coder-V2-Lite-Instruct-4bit",
        },
        "memory": {
            "max_short_term": 10,
            "vector_search_limit": 5,
        },
        "tools": {
            "shell": {
                "auto_confirm": ["ls", "pwd", "head", "tail", "echo"],
                "blocked": ["rm -rf /", "sudo", "mkfs", "dd"],
                "cooldown_seconds": 2.0,
                "max_consecutive_failures": 5,
            },
            "file": {
                "max_file_size": 1048576,  # 1MB
                "auto_backup": True,
            },
        },
        "ignored_dirs": [
            ".git",
            "node_modules",
            ".venv",
            "venv",
            "__pycache__",
            "build",
            "dist",
            ".idea",
            ".vscode",
        ],
        "analysis": {
            "max_context_tokens": 24000,
            "temperature": 0.2,
            "max_iterations": 5,
        },
    }
    
    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.config_dir = self.project_path / ".codearon"
        self.config_file = self.config_dir / "config.yaml"
        self.config = self.DEFAULT_CONFIG.copy()
        
        if self.config_file.exists():
            self._load_config()
    
    def _load_config(self):
        """Load configuration from .codearon/config.yaml"""
        try:
            with open(self.config_file, 'r') as f:
                user_config = yaml.safe_load(f)
            
            if user_config:
                # Merge with default config (user config takes precedence)
                self._merge_config(user_config)
                logger.info(f"Loaded project config from {self.config_file}")
        except Exception as e:
            logger.warning(f"Failed to load config: {e}. Using defaults.")
            raise ConfigurationError(f"Config load error: {e}", config_key="config_file")
    
    def _merge_config(self, user_config: Dict[str, Any]):
        """Deep merge user config with defaults."""
        def deep_merge(base: dict, override: dict) -> dict:
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        self.config = deep_merge(self.config, user_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        Example: config.get('tools.shell.cooldown_seconds')
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def save(self):
        """Save current configuration to file."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Saved config to {self.config_file}")
    
    def create_default_config(self):
        """Create default config file if it doesn't exist."""
        if not self.config_file.exists():
            self.save()
            logger.info(f"Created default config at {self.config_file}")
            return True
        return False
    
    @property
    def ignored_dirs(self) -> List[str]:
        """Get list of ignored directories."""
        return self.config.get("ignored_dirs", self.DEFAULT_CONFIG["ignored_dirs"])
    
    @property
    def model_default(self) -> str:
        """Get default model ID."""
        return self.config.get("model", {}).get("default", self.DEFAULT_CONFIG["model"]["default"])
    
    @property
    def shell_auto_confirm(self) -> List[str]:
        """Get list of auto-confirm shell commands."""
        return self.config.get("tools", {}).get("shell", {}).get("auto_confirm", [])
    
    @property
    def shell_blocked(self) -> List[str]:
        """Get list of blocked shell commands."""
        return self.config.get("tools", {}).get("shell", {}).get("blocked", [])
    
    @property
    def shell_cooldown(self) -> float:
        """Get shell command cooldown in seconds."""
        return self.config.get("tools", {}).get("shell", {}).get("cooldown_seconds", 2.0)
    
    @property
    def max_consecutive_failures(self) -> int:
        """Get max consecutive failures before circuit breaker."""
        return self.config.get("tools", {}).get("shell", {}).get("max_consecutive_failures", 5)
