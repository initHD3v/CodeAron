import sys
import os
from unittest.mock import patch

sys.path.append(os.getcwd())
from src.core.orchestrator import Orchestrator

def run_test():
    print("STARTING REAL-TIME TEST: SIMPLETASK")
    with patch('git.Repo'):
        orc = Orchestrator()
        instruction = "Selesaikan proyek di direktori simpletask/. Analisis dan beri peningkatan signifikan agar profesional."
        with patch('questionary.confirm') as mc:
            mc.return_value.ask.return_value = True
            orc.run_cycle(instruction)

if __name__ == '__main__':
    run_test()
