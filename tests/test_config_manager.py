"""
Unit tests untuk ProjectConfig / ConfigManager.
"""

import unittest
import sys
import os
import tempfile
import yaml
from pathlib import Path

sys.path.insert(0, os.getcwd())

from src.core.config_manager import ProjectConfig


class TestProjectConfig(unittest.TestCase):
    """Tests for ProjectConfig - test methods are ordered to avoid interference."""
    
    def setUp(self):
        # Create temporary directory for testing - unique per test
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.project_path = Path(self.temp_dir)
        self.config_dir = self.project_path / ".codearon"
        self.config_file = self.config_dir / "config.yaml"
    
    def tearDown(self):
        # Cleanup
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_01_default_config(self):
        """Test default configuration values."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        config = ProjectConfig(temp_dir)
        
        self.assertEqual(config.model_default, "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit")
        self.assertEqual(config.shell_cooldown, 2.0)
        self.assertEqual(config.max_consecutive_failures, 5)
        self.assertIn(".git", config.ignored_dirs)
        self.assertIn("ls", config.shell_auto_confirm)
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_02_get_nested_value(self):
        """Test getting nested config values with dot notation."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        config = ProjectConfig(temp_dir)
        
        value = config.get("model.default")
        self.assertEqual(value, "mlx-community/Qwen2.5-Coder-7B-Instruct-4bit")
        
        value = config.get("tools.shell.cooldown_seconds")
        self.assertEqual(value, 2.0)
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_03_get_nonexistent_value(self):
        """Test getting nonexistent config value."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        config = ProjectConfig(temp_dir)
        
        value = config.get("nonexistent.key", "default_value")
        self.assertEqual(value, "default_value")
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_04_create_default_config(self):
        """Test creating default config file."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        config = ProjectConfig(temp_dir)
        
        result = config.create_default_config()
        self.assertTrue(result)
        
        config_file = Path(temp_dir) / ".codearon" / "config.yaml"
        self.assertTrue(config_file.exists())
        
        # Verify content
        import yaml
        with open(config_file, 'r') as f:
            saved_config = yaml.safe_load(f)
        
        self.assertEqual(saved_config["version"], "1.0")
        self.assertIn("model", saved_config)
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_05_custom_config(self):
        """Test loading custom configuration."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        config_dir = Path(temp_dir) / ".codearon"
        config_file = config_dir / "config.yaml"
        
        # Create custom config
        config_dir.mkdir(parents=True, exist_ok=True)
        
        custom_config = {
            "model": {
                "default": "custom-model",
            },
            "tools": {
                "shell": {
                    "cooldown_seconds": 5.0,
                }
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(custom_config, f)
        
        config = ProjectConfig(temp_dir)
        
        self.assertEqual(config.model_default, "custom-model")
        self.assertEqual(config.shell_cooldown, 5.0)
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_06_ignored_dirs_property(self):
        """Test ignored_dirs property."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        config = ProjectConfig(temp_dir)
        
        dirs = config.ignored_dirs
        self.assertIsInstance(dirs, list)
        self.assertIn(".git", dirs)
        self.assertIn("node_modules", dirs)
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_07_shell_auto_confirm_property(self):
        """Test shell_auto_confirm property."""
        import tempfile
        temp_dir = tempfile.mkdtemp()
        config = ProjectConfig(temp_dir)
        
        commands = config.shell_auto_confirm
        self.assertIsInstance(commands, list)
        self.assertIn("ls", commands)
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main()
