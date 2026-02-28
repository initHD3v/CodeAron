"""
Real AI-Powered Analysis untuk CodeAron.
Bukan template - benar-benar menggunakan LLM untuk reasoning.
"""

import os
from pathlib import Path
from typing import Dict, Any, List


def gather_project_data(cwd: str) -> Dict[str, Any]:
    """Gather comprehensive project data."""
    data = {
        "type": "unknown",
        "structure": [],
        "readme": None,
        "configs": {},
        "main_files": [],
        "issues": [],
    }
    
    project_path = Path(cwd)
    
    # Detect type
    if (project_path / "pubspec.yaml").exists():
        data["type"] = "Flutter/Dart"
    elif (project_path / "package.json").exists():
        data["type"] = "Node.js/JavaScript"
    elif (project_path / "requirements.txt").exists():
        data["type"] = "Python"
    elif (project_path / "Cargo.toml").exists():
        data["type"] = "Rust"
    elif (project_path / "go.mod").exists():
        data["type"] = "Go"
    else:
        data["type"] = "Other"
    
    # Scan structure
    for item in project_path.iterdir():
        if item.name.startswith(".") and item.name not in [".github"]:
            continue
        if item.name in ["node_modules", ".venv", "__pycache__", "build"]:
            continue
        
        if item.is_file():
            data["structure"].append(f"📄 {item.name}")
            
            # Read README
            if item.name.lower() == "readme.md":
                try:
                    data["readme"] = item.read_text()[:2000]
                except:
                    pass
            
            # Read configs
            if item.name in ["pubspec.yaml", "package.json", "requirements.txt"]:
                try:
                    data["configs"][item.name] = item.read_text()[:1000]
                except:
                    pass
            
            if item.suffix in [".py", ".js", ".ts", ".dart", ".rs", ".go"]:
                data["main_files"].append(item.name)
        
        elif item.is_dir():
            count = len(list(item.glob("*")))
            data["structure"].append(f"📁 {item.name}/ ({count} files)")
    
    # Check issues
    if not (project_path / "README.md").exists():
        data["issues"].append("No README.md")
    if not (project_path / ".gitignore").exists():
        data["issues"].append("No .gitignore")
    if not (project_path / "tests").exists() and not (project_path / "test").exists():
        data["issues"].append("No test folder")
    
    return data


def build_analysis_prompt(data: Dict[str, Any]) -> str:
    """Build prompt untuk deep AI analysis."""
    return f"""
You are a Senior Software Architect. Analyze this project DEEPLY in BAHASA INDONESIA.

PROJECT DATA:
- Type: {data['type']}
- Files: {', '.join(data['structure'][:12])}
- Main Code: {', '.join(data['main_files'][:8])}
- Issues: {', '.join(data['issues']) if data['issues'] else 'None obvious'}

README:
{data['readme'][:800] if data['readme'] else 'No README'}

Config:
{list(data['configs'].keys())}

---

Provide REAL INSIGHTS (not generic advice):

1. **APA INI?** - Project apa ini? Untuk apa?

2. **ANALISIS STRUKTUR** - Apakah terorganisir baik? Ada masalah?

3. **CODE QUALITY** - Dari file structure, apakah code berkualitas?

4. **ISSUES SPESIFIK** - Masalah apa yang kamu lihat di project INI?

5. **RECOMMENDATIONS** - 3-5 saran SPESIFIK untuk project ini (bukan generic!)

6. **KESIMPULAN** - Resume singkat

Be HONEST and CRITICAL. Don't sugarcoat issues!
"""
