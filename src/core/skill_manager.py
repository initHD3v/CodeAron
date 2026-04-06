"""
Skill Manager untuk CodeAron
Mengelola load, parse, dan execute skill definitions
"""

import os
import re
import yaml
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger("SkillManager")


@dataclass
class SkillDefinition:
    """Representasi sebuah skill"""
    name: str
    description: str
    allowed_tools: List[str] = field(default_factory=list)
    instructions: str = ""
    steps: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    category: str = "general"
    auto_execute: bool = False  # Jika True, tidak perlu konfirmasi
    
    @classmethod
    def from_yaml(cls, yaml_content: str) -> "SkillDefinition":
        """Parse skill dari YAML format"""
        try:
            # Split frontmatter dan content
            if yaml_content.startswith("---"):
                parts = yaml_content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter = parts[1].strip()
                    content = parts[2].strip()
                else:
                    frontmatter = parts[1].strip() if len(parts) > 1 else ""
                    content = ""
            else:
                frontmatter = yaml_content
                content = ""
            
            # Parse YAML frontmatter
            data = {}
            if frontmatter:
                try:
                    data = yaml.safe_load(frontmatter)
                    if not isinstance(data, dict):
                        data = {}
                except yaml.YAMLError:
                    data = {}
            
            # Parse content untuk instructions dan steps
            instructions = content
            steps = []
            examples = []
            
            # Extract steps dari markdown
            step_pattern = r'###?\s*Step\s*\d*:?\s*(.+?)(?=###?\s*Step|\Z)'
            step_matches = re.findall(step_pattern, content, re.DOTALL | re.IGNORECASE)
            steps = [s.strip() for s in step_matches]
            
            # Extract examples
            example_pattern = r'(?:##?\s*Examples?|CONTOH)[:\s]*(.+?)(?=##|\Z)'
            example_matches = re.findall(example_pattern, content, re.DOTALL | re.IGNORECASE)
            examples = [e.strip() for e in example_matches]
            
            return cls(
                name=data.get("name", "unknown") if data else "unknown",
                description=data.get("description", "") if data else "",
                allowed_tools=data.get("allowedTools", []) if data else [],
                instructions=instructions,
                steps=steps,
                examples=examples,
                category=data.get("category", "general") if data else "general",
                auto_execute=data.get("auto_execute", False) if data else False
            )
        except Exception as e:
            logger.error(f"Error parsing skill YAML: {e}")
            # Return minimal skill on error
            return cls(
                name="unknown",
                description="",
                instructions=yaml_content
            )


class SkillManager:
    """
    Manager untuk load dan execute skills
    """
    
    DEFAULT_SKILLS_DIR = Path(__file__).parent.parent / "skills"
    
    def __init__(self, skills_dir: Optional[Path] = None):
        self.skills_dir = skills_dir or self.DEFAULT_SKILLS_DIR
        self.skills: Dict[str, SkillDefinition] = {}
        self.categories: Dict[str, List[str]] = {}
        
        # Auto-load skills dari directory
        self._load_all_skills()
    
    def _load_all_skills(self):
        """Load semua skill dari directory"""
        # Check jika skills_dir ada
        if not self.skills_dir.exists():
            # Coba fallback ke absolute path
            fallback_dir = Path("/Users/initialh/Projects/CodeAron/src/skills")
            if fallback_dir.exists():
                self.skills_dir = fallback_dir
            else:
                logger.warning(f"Skills directory not found: {self.skills_dir}")
                return
        
        # Load skills dari folder utama
        self._load_skills_from_folder(self.skills_dir)
        
        # Load skills dari subfolders (by category)
        for subdir in self.skills_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith("_"):
                self._load_skills_from_folder(subdir, category=subdir.name)
        
        logger.info(f"Loaded {len(self.skills)} skills")
    
    def _load_skills_from_folder(self, folder: Path, category: Optional[str] = None):
        """Load skills dari sebuah folder"""
        for file_path in folder.glob("*.md"):
            try:
                skill = self._load_skill_file(file_path)
                if category and not skill.category:
                    skill.category = category
                self.skills[skill.name] = skill
                
                # Add to category index
                if skill.category not in self.categories:
                    self.categories[skill.category] = []
                if skill.name not in self.categories[skill.category]:
                    self.categories[skill.category].append(skill.name)
                    
            except Exception as e:
                logger.error(f"Failed to load skill {file_path.name}: {e}")
    
    def _load_skill_file(self, file_path: Path) -> SkillDefinition:
        """Load single skill dari file"""
        content = file_path.read_text(encoding="utf-8")
        return SkillDefinition.from_yaml(content)
    
    def get_skill(self, name: str) -> Optional[SkillDefinition]:
        """Get skill by name"""
        return self.skills.get(name)
    
    def list_skills(self, category: Optional[str] = None) -> List[str]:
        """List semua skills, optionally filtered by category"""
        if category:
            return self.categories.get(category, [])
        return list(self.skills.keys())
    
    def list_categories(self) -> List[str]:
        """List semua categories"""
        return list(self.categories.keys())
    
    def get_skills_by_category(self) -> Dict[str, List[str]]:
        """Get semua skills grouped by category"""
        return self.categories.copy()
    
    def add_skill(self, skill: SkillDefinition):
        """Add skill secara dinamis"""
        self.skills[skill.name] = skill
        if skill.category not in self.categories:
            self.categories[skill.category] = []
        self.categories[skill.category].append(skill.name)
        logger.info(f"Added skill: {skill.name}")
    
    def remove_skill(self, name: str) -> bool:
        """Remove skill by name"""
        if name not in self.skills:
            return False
        
        skill = self.skills[name]
        del self.skills[name]
        
        if skill.category in self.categories:
            if name in self.categories[skill.category]:
                self.categories[skill.category].remove(name)
        
        logger.info(f"Removed skill: {name}")
        return True
    
    def get_skill_summary(self, name: str) -> str:
        """Get ringkasan skill untuk display"""
        skill = self.get_skill(name)
        if not skill:
            return f"Skill '{name}' not found"
        
        summary = f"**{skill.name}** - {skill.description}\n"
        summary += f"Category: `{skill.category}`\n"
        summary += f"Tools: {', '.join(skill.allowed_tools)}\n"
        
        if skill.steps:
            summary += f"\nSteps: {len(skill.steps)} langkah\n"
        
        return summary
    
    def register_skill(self, name: str, description: str, instructions: str, 
                       allowed_tools: List[str] = None, category: str = "custom"):
        """
        Register skill secara programmatic
        
        Example:
            skill_manager.register_skill(
                name="quick_fix",
                description="Fix common code errors",
                instructions="1. Analyze the code\n2. Find errors\n3. Fix them",
                allowed_tools=["file_read", "file_write", "shell"],
                category="coding"
            )
        """
        skill = SkillDefinition(
            name=name,
            description=description,
            instructions=instructions,
            allowed_tools=allowed_tools or [],
            category=category
        )
        self.add_skill(skill)
        return skill


# Singleton instance
_skill_manager: Optional[SkillManager] = None

def get_skill_manager() -> SkillManager:
    """Get singleton SkillManager instance"""
    global _skill_manager
    if _skill_manager is None:
        _skill_manager = SkillManager()
    return _skill_manager
