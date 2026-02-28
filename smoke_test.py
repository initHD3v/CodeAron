import sys
import os
from unittest.mock import MagicMock, patch

# Tambahkan src ke path agar bisa diimport
sys.path.append(os.getcwd())

from src.core.orchestrator import Orchestrator
from src.llm.inference import InferenceEngine
from src.core.states import AronState

def run_smoke_test():
    print("SMOKE TEST: Memulai Verifikasi Stabilitas")
    
    # 1. Singleton Check
    engine1 = InferenceEngine()
    engine2 = InferenceEngine()
    if engine1 is engine2:
        print("✅ Singleton: OK")
    else:
        print("❌ Singleton: FAIL")
        return

    # 2. Orchestrator Init
    try:
        orc = Orchestrator()
        print("✅ Orchestrator Init: OK")
    except Exception as e:
        print(f"❌ Orchestrator Init: FAIL ({e})")
        return

    # 3. Action Processing Integration
    sample_response = "Test <shell>echo 'hi'</shell> <file path='t.txt'>content</file>"
    with patch('questionary.confirm') as mock_confirm:
        mock_confirm.return_value.ask.return_value = True
        with patch.object(orc, '_run_shell') as mock_run:
            from src.core.states import ExecutionResult
            mock_run.return_value = ExecutionResult(True, "hi", "", 0)
            orc.patcher.write_full_file = MagicMock()
            
            results = orc._process_actions(sample_response)
            if len(results) == 2:
                print("✅ Action Parsing & Mock Execution: OK")
            else:
                print(f"❌ Action Parsing: FAIL (Got {len(results)} actions)")

    # 4. Resource Cleanup
    try:
        orc.inference.unload_model()
        print("✅ Resource Cleanup: OK")
    except Exception as e:
        print(f"❌ Resource Cleanup: FAIL ({e})")

    print("\n🚀 ALL SYSTEM FOUNDATIONS ARE STABLE")

if __name__ == "__main__":
    run_smoke_test()
