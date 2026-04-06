"""
CodeAron Skills Package

Skills adalah specialized agents untuk task tertentu.
Setiap skill didefinisikan dalam file Markdown dengan YAML frontmatter.
"""

from pathlib import Path

# Default skills directory
SKILLS_DIR = Path(__file__).parent

__all__ = ["SKILLS_DIR"]
