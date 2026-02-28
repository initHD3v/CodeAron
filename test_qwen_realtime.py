import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.getcwd())
from src.core.orchestrator import Orchestrator

def test():
    print("START QWEN2.5 TEST")
    with patch('git.Repo'):
        orc = Orchestrator()
        
        print("\n[USER]: Analisis proyek ini mendalam.")
        with patch('questionary.confirm') as mc:
            mc.return_value.ask.return_value = True
            orc.run_cycle("Analisis proyek ini mendalam.")

if __name__ == "__main__":
    test()
