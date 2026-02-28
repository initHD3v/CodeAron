"""
Smart Analysis System untuk CodeAron.
Memberikan analisis mendalam seperti Gemini CLI / Qwen CLI.
"""

import os
from pathlib import Path
from typing import Dict, List, Any


class SmartAnalyzer:
    """Smart analyzer untuk deep project analysis."""
    
    PROJECT_SIGNATURES = {
        "python": ["requirements.txt", "setup.py", "pyproject.toml", ".py"],
        "flutter": ["pubspec.yaml", "lib/main.dart"],
        "nodejs": ["package.json", "node_modules"],
        "react": ["package.json", "src/App.js", "src/App.tsx"],
        "vue": ["package.json", "vue.config.js", "src/App.vue"],
        "nextjs": ["package.json", "next.config.js", "pages/"],
        "rust": ["Cargo.toml", "src/main.rs"],
        "go": ["go.mod", "go.sum", "main.go"],
        "java": ["pom.xml", "build.gradle", "src/main/java"],
        "php": ["composer.json", "index.php", "wp-config.php"],
        "html_static": ["index.html", "*.html"],
    }
    
    COMMON_ISSUES = {
        "python": {
            "missing_requirements": "Tidak ada requirements.txt - sulit untuk reproduce environment",
            "missing_readme": "Tidak ada README.md - dokumentasi kurang",
            "missing_tests": "Tidak ada folder tests/ - tidak ada automated testing",
            "missing_gitignore": "Tidak ada .gitignore - risiko commit file sensitif",
        },
        "flutter": {
            "missing_pubspec": "Tidak ada pubspec.yaml - bukan project Flutter valid",
            "missing_analysis": "Tidak ada analysis_options.yaml - tidak ada linting config",
        },
        "nodejs": {
            "missing_package": "Tidak ada package.json - bukan project Node.js valid",
            "missing_gitignore": "Tidak ada .gitignore - node_modules bisa ter-commit",
        },
    }
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.project_type = None
        self.structure = {}
        self.issues = []
        self.recommendations = []
    
    def detect_project_type(self) -> str:
        """Detect project type dari file signatures."""
        for proj_type, signatures in self.PROJECT_SIGNATURES.items():
            matches = 0
            for sig in signatures:
                if sig.startswith("."):
                    if (self.project_path / sig[1:]).exists():
                        matches += 1
                elif sig.endswith("/"):
                    if (self.project_path / sig).is_dir():
                        matches += 1
                elif "*" in sig:
                    import glob
                    if glob.glob(str(self.project_path / sig)):
                        matches += 1
                else:
                    if (self.project_path / sig).exists():
                        matches += 1
            
            if matches >= 2 or (matches == 1 and proj_type in ["html_static"]):
                self.project_type = proj_type
                return proj_type
        
        return "unknown"
    
    def analyze_structure(self) -> Dict[str, Any]:
        """Analyze project structure secara mendalam."""
        structure = {
            "root_files": [],
            "directories": {},
            "total_files": 0,
            "total_dirs": 0,
            "code_files": 0,
            "config_files": 0,
        }
        
        for item in self.project_path.iterdir():
            if item.name.startswith(".") and item.name not in [".github", ".vscode"]:
                continue
            
            if item.is_file():
                structure["root_files"].append(item.name)
                structure["total_files"] += 1
                
                if item.suffix in [".py", ".js", ".ts", ".dart", ".rs", ".go", ".java"]:
                    structure["code_files"] += 1
                elif item.suffix in [".json", ".yaml", ".yml", ".toml", ".xml"]:
                    structure["config_files"] += 1
            
            elif item.is_dir():
                structure["total_dirs"] += 1
                dir_files = list(item.glob("*"))
                structure["directories"][item.name] = len(dir_files)
        
        self.structure = structure
        return structure
    
    def detect_issues(self) -> List[str]:
        """Detect potential issues dan best practice violations."""
        issues = []
        
        if not self.project_type:
            self.detect_project_type()
        
        # Common issues untuk semua project
        if not (self.project_path / "README.md").exists():
            issues.append("❌ Tidak ada README.md - dokumentasi kurang")
        
        if not (self.project_path / ".gitignore").exists():
            issues.append("⚠️ Tidak ada .gitignore - risiko commit file sensitif")
        
        if not (self.project_path / "tests").exists() and not (self.project_path / "test").exists():
            issues.append("⚠️ Tidak ada folder tests - tidak ada automated testing")
        
        # Project-specific issues
        if self.project_type in self.COMMON_ISSUES:
            for issue_key, issue_msg in self.COMMON_ISSUES[self.project_type].items():
                if issue_key == "missing_requirements" and not (self.project_path / "requirements.txt").exists():
                    issues.append(f"❌ {issue_msg}")
                elif issue_key == "missing_pubspec" and not (self.project_path / "pubspec.yaml").exists():
                    issues.append(f"❌ {issue_msg}")
                elif issue_key == "missing_package" and not (self.project_path / "package.json").exists():
                    issues.append(f"❌ {issue_msg}")
        
        self.issues = issues
        return issues
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        if not self.project_type:
            self.detect_project_type()
        
        # Base recommendations
        recommendations.append("📝 Buat README.md yang comprehensive dengan installation & usage guide")
        recommendations.append("🔧 Tambahkan .gitignore yang sesuai dengan tech stack")
        recommendations.append("🧪 Setup automated testing (unit test, integration test)")
        
        # Project-specific recommendations
        if self.project_type == "python":
            recommendations.append("📦 Gunakan virtual environment (venv, poetry, atau conda)")
            recommendations.append("📝 Tambahkan type hints untuk better code quality")
            recommendations.append("🔒 Pertimbangkan security scanning dengan safety atau bandit")
        
        elif self.project_type == "flutter":
            recommendations.append("📱 Setup Flutter flavor untuk different environments")
            recommendations.append("🎨 Gunakan consistent state management (Provider, Riverpod, Bloc)")
            recommendations.append("📊 Add integration tests dengan flutter_driver")
        
        elif self.project_type == "nodejs":
            recommendations.append("📦 Gunakan TypeScript untuk better type safety")
            recommendations.append("🔒 Run npm audit regularly untuk security vulnerabilities")
            recommendations.append("⚙️ Setup ESLint + Prettier untuk code consistency")
        
        elif self.project_type == "html_static":
            recommendations.append("🎨 Pertimbangkan menggunakan CSS framework (Tailwind, Bootstrap)")
            recommendations.append("⚡ Add build process dengan Vite atau Parcel untuk optimization")
            recommendations.append("📱 Pastikan responsive design untuk mobile devices")
        
        self.recommendations = recommendations
        return recommendations
    
    def generate_full_analysis(self) -> str:
        """Generate comprehensive analysis report."""
        if not self.project_type:
            self.detect_project_type()
        
        self.analyze_structure()
        self.detect_issues()
        self.generate_recommendations()
        
        # Build report
        report = []
        report.append("## 🔍 ANALISIS PROJECT LENGKAP\n")
        
        # Project Type
        type_emoji = {
            "python": "🐍",
            "flutter": "📱",
            "nodejs": "🟢",
            "react": "⚛️",
            "vue": "💚",
            "html_static": "🌐",
            "unknown": "❓",
        }
        report.append(f"**Type:** {type_emoji.get(self.project_type, '❓')} {self.project_type.upper() if self.project_type else 'UNKNOWN'}\n")
        
        # Structure Summary
        report.append("\n### 📊 STRUKTUR PROJECT")
        report.append(f"- **Total Files:** {self.structure.get('total_files', 0)}")
        report.append(f"- **Total Directories:** {self.structure.get('total_dirs', 0)}")
        report.append(f"- **Code Files:** {self.structure.get('code_files', 0)}")
        report.append(f"- **Config Files:** {self.structure.get('config_files', 0)}")
        
        if self.structure.get('root_files'):
            report.append(f"- **Root Files:** {', '.join(self.structure['root_files'][:5])}")
        
        if self.structure.get('directories'):
            dirs_str = ', '.join([f"{k} ({v} files)" for k, v in list(self.structure['directories'].items())[:5]])
            report.append(f"- **Directories:** {dirs_str}")
        
        # Issues
        report.append("\n### ⚠️ ISSUES TERDETEKSI")
        if self.issues:
            for issue in self.issues:
                report.append(f"- {issue}")
        else:
            report.append("- ✅ Tidak ada major issues terdeteksi!")
        
        # Recommendations
        report.append("\n### 💡 RECOMMENDATIONS")
        for i, rec in enumerate(self.recommendations[:7], 1):
            report.append(f"{i}. {rec}")
        
        # Summary
        report.append("\n### 📋 RESUME")
        if self.project_type == "unknown":
            report.append("Project ini terlihat seperti **static website** atau **project sederhana**.")
            report.append("Untuk analisis lebih mendalam, tambahkan dokumentasi atau configuration files.")
        else:
            report.append(f"Project **{self.project_type}** yang {'terstruktur dengan baik' if self.structure.get('code_files', 0) > 0 else 'sederhana'}.")
            report.append(f"{'✅ Ready untuk development' if len(self.issues) < 2 else '⚠️ Perlu improvement di beberapa area'}.")
        
        return "\n".join(report)


# Export untuk digunakan di orchestrator
def analyze_project(project_path: str) -> str:
    """Main function untuk analyze project."""
    analyzer = SmartAnalyzer(project_path)
    return analyzer.generate_full_analysis()
