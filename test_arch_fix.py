import sys
import os
from unittest.mock import patch

sys.path.append(os.getcwd())
from src.core.orchestrator import Orchestrator

def run_arch_test():
    print('Starting Architectural Analysis...')
    with patch('git.Repo'):
        orc = Orchestrator()
        # Prompt untuk analisis mendalam
        msg = 'Analisis sistem routing di orchestrator ini. Jelaskan ToolRouter dan integrasinya.'
        with patch('questionary.confirm') as mc:
            mc.return_value.ask.return_value = True
            orc.run_cycle(msg)

if __name__ == '__main__':
    run_arch_test()
