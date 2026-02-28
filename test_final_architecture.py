import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.getcwd())
from src.core.orchestrator import Orchestrator

def test():
    print("FINAL TEST: Deep Architecture")
    with patch('git.Repo'):
        orc = Orchestrator()
        instruction = "Analisis sistem routing di orchestrator ini. Jelaskan ToolRouter dan integrasinya di orchestrator.py."
        with patch('questionary.confirm') as mc:
            mc.return_value.ask.return_value = True
            orc.run_cycle(instruction)

if __name__ == "__main__":
    test()
