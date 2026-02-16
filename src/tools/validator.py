import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger("ValidationEngine")

class ValidationEngine:
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)

    def detect_project_type(self) -> str:
        """Mendeteksi tipe proyek berdasarkan file manifes."""
        if (self.project_path / "pubspec.yaml").exists():
            return "flutter"
        if (self.project_path / "requirements.txt").exists() or (self.project_path / "pyproject.toml").exists():
            return "python"
        if (self.project_path / "package.json").exists():
            return "nodejs"
        return "generic"

    def validate_code(self) -> Dict[str, Any]:
        """Menjalankan validasi sesuai tipe proyek."""
        project_type = self.detect_project_type()
        logger.info(f"Menjalankan validasi untuk proyek tipe: {project_type}")
        
        if project_type == "flutter":
            return self._run_command("flutter analyze")
        elif project_type == "python":
            # Cek syntax secara cepat untuk semua file python yang baru diubah
            return self._run_command("python -m compileall -q .")
        
        return {"success": True, "message": "Tidak ada alat validasi spesifik untuk tipe proyek ini."}

    def _run_command(self, command: str) -> Dict[str, Any]:
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return {"success": True, "message": result.stdout}
            else:
                return {"success": False, "message": result.stdout or result.stderr}
        except Exception as e:
            return {"success": False, "message": str(e)}
