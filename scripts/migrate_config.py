#!/usr/bin/env python3
"""
Migration Script untuk CodeAron v0.2.x ke v0.3.0

Script ini akan:
1. Backup config lama (jika ada)
2. Generate config baru dengan format v0.3.0
3. Migrate settings lama ke format baru

Usage:
    python scripts/migrate_config.py
"""

import os
import sys
import shutil
import yaml
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.config import settings

# ANSI Color Codes
class Colors:
    RESET = '\033[0m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    print(f"  {text}")

def backup_old_config(config_file):
    """Backup config lama jika ada."""
    if not config_file.exists():
        return None
    
    backup_path = config_file.parent / f"config.yaml.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    try:
        shutil.copy2(config_file, backup_path)
        print_success(f"Backup config lama ke: {backup_path}")
        return backup_path
    except Exception as e:
        print_error(f"Gagal backup config: {e}")
        return None

def migrate_old_config(old_config):
    """Migrate settings dari config lama ke format baru."""
    new_config = {
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
                "max_file_size": 1048576,
                "auto_backup": True,
            },
        },
        "ignored_dirs": [
            ".git", "node_modules", ".venv", "venv", "__pycache__",
            "build", "dist", ".idea", ".vscode",
        ],
        "analysis": {
            "max_context_tokens": 24000,
            "temperature": 0.2,
            "max_iterations": 5,
        },
    }
    
    # Migrate settings lama jika ada
    migrated_count = 0
    
    # Migrate model settings
    if "model" in old_config:
        if "default" in old_config["model"]:
            new_config["model"]["default"] = old_config["model"]["default"]
            migrated_count += 1
    
    # Migrate ignored dirs
    if "ignored_dirs" in old_config:
        new_config["ignored_dirs"] = old_config["ignored_dirs"]
        migrated_count += 1
    
    # Migrate shell settings
    if "tools" in old_config and "shell" in old_config["tools"]:
        old_shell = old_config["tools"]["shell"]
        if "auto_confirm" in old_shell:
            new_config["tools"]["shell"]["auto_confirm"] = old_shell["auto_confirm"]
            migrated_count += 1
        if "cooldown" in old_shell:
            new_config["tools"]["shell"]["cooldown_seconds"] = old_shell["cooldown"]
            migrated_count += 1
    
    return new_config, migrated_count

def generate_new_config(config_file, old_config=None):
    """Generate config baru."""
    config_dir = config_file.parent
    config_dir.mkdir(parents=True, exist_ok=True)
    
    if old_config:
        new_config, migrated_count = migrate_old_config(old_config)
        if migrated_count > 0:
            print_success(f"Migrate {migrated_count} settings dari config lama")
    else:
        # Gunakan default
        new_config = {
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
                    "max_file_size": 1048576,
                    "auto_backup": True,
                },
            },
            "ignored_dirs": [
                ".git", "node_modules", ".venv", "venv", "__pycache__",
                "build", "dist", ".idea", ".vscode",
            ],
            "analysis": {
                "max_context_tokens": 24000,
                "temperature": 0.2,
                "max_iterations": 5,
            },
        }
    
    # Write config baru
    with open(config_file, 'w') as f:
        yaml.dump(new_config, f, default_flow_style=False, sort_keys=False)
    
    print_success(f"Config baru dibuat: {config_file}")
    return new_config

def load_old_config(config_file):
    """Load config lama jika ada."""
    if not config_file.exists():
        return None
    
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print_warning(f"Gagal load config lama: {e}")
        return None

def validate_new_config(config):
    """Validate config baru."""
    required_keys = ["version", "model", "tools", "ignored_dirs"]
    
    for key in required_keys:
        if key not in config:
            print_error(f"Missing required key: {key}")
            return False
    
    if "default" not in config.get("model", {}):
        print_error("Missing model.default")
        return False
    
    print_success("Config valid!")
    return True

def main():
    print_header("CodeAron Config Migration Tool v0.3.0")
    
    # Determine config path
    project_dir = Path.cwd()
    config_dir = project_dir / ".codearon"
    config_file = config_dir / "config.yaml"
    
    print_info(f"Project directory: {project_dir}")
    print_info(f"Config file: {config_file}")
    
    # Check if config already exists
    if config_file.exists():
        print_warning("Config file sudah ada!")
        response = input(f"  Lanjutkan dan backup config lama? (y/N): ")
        if response.lower() != 'y':
            print_info("Migration dibatalkan.")
            return
    
    # Load old config if exists
    old_config = load_old_config(config_file)
    if old_config:
        print_info("Config lama ditemukan, akan dimigrate...")
        backup_old_config(config_file)
    
    # Generate new config
    new_config = generate_new_config(config_file, old_config)
    
    # Validate
    if not validate_new_config(new_config):
        print_error("Config validation failed!")
        return 1
    
    # Summary
    print_header("Migration Summary")
    print_success("Migration berhasil!")
    print_info(f"Config location: {config_file}")
    print_info("\nNext steps:")
    print_info("  1. Review config di .codearon/config.yaml")
    print_info("  2. Edit sesuai kebutuhan")
    print_info("  3. Jalankan 'aron' untuk memulai")
    
    print(f"\n{Colors.GREEN}Done!{Colors.RESET}\n")
    return 0

if __name__ == "__main__":
    sys.exit(main())
