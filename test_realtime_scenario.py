import sys
import os
from unittest.mock import patch, MagicMock

sys.path.append(os.getcwd())
from src.core.orchestrator import Orchestrator

def test():
    print("START MULTI-TURN TEST")
    with patch('git.Repo'):
        orc = Orchestrator()
        
        # Turn 1
        print("\n--- TURN 1: GREETING ---")
        orc.run_cycle("hai aron")
        
        # Turn 2
        print("\n--- TURN 2: PWD ---")
        with patch('questionary.confirm') as mc:
            mc.return_value.ask.return_value = True
            orc.run_cycle("di directory mana kamu berjalan?")
            
        # Turn 3
        print("\n--- TURN 3: ANALYSIS ---")
        with patch('questionary.confirm') as mc:
            mc.return_value.ask.return_value = True
            orc.run_cycle("analisis folder ini. jika ini project code, jelaskan detail isinya.")

if __name__ == "__main__":
    test()
