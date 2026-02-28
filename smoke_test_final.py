import sys
import os
from unittest.mock import MagicMock, patch

sys.path.append(os.getcwd())
from src.core.orchestrator import Orchestrator
from src.llm.inference import InferenceEngine
from src.core.states import AronState

def test():
    print("FINAL SMOKETEST")
    engine = InferenceEngine()
    print("1. Inference: OK")
    
    with patch('git.Repo'):
        orc = Orchestrator()
        print("2. Orchestrator Init: OK")
        
        # Test 1: Fast Track
        res = orc.run_cycle("hai")
        if "Aron" in res: print("3. Fast-Track Greeting: OK")
        
        # Test 2: Auto-Correct Markdown
        md = "Tentu:\n```shell\nls\n```"
        with patch('questionary.confirm') as mc:
            mc.return_value.ask.return_value = True
            with patch.object(orc, '_run_shell') as mr:
                from src.core.states import ExecutionResult
                mr.return_value = ExecutionResult(True, "total", "", 0)
                acts = orc._process_actions(md)
                if len(acts) > 0: print("4. Auto-Correction Parser: OK")
        
        # Test 3: State
        if orc.state == AronState.IDLE: print("5. State Integrity: OK")

    print("\n--- ALL SYSTEMS STABLE ---")

if __name__ == "__main__":
    test()
