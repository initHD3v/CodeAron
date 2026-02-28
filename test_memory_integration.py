import sys
import os

sys.path.append(os.getcwd())

from src.core.memory import MemoryManager
from src.memory.vector_store import VectorStore

def test_memory():
    print("MEMORI INTEGRASI TEST")
    vs = VectorStore()
    mm = MemoryManager(vector_store=vs)
    mm.add_short_term("User", "Halo Aron")
    mm.add_short_term("Aron", "Halo!")
    mm.load_project_memory()
    context = mm.get_combined_context("Orchestrator")
    
    print("Checking sections...")
    has_pm = "[PROJECT CONTEXT]" in context
    has_lt = "[LONG-TERM MEMORY]" in context
    has_st = "[SHORT-TERM SESSION]" in context
    
    if has_pm and has_lt and has_st:
        print("✅ INTEGRASI MEMORI: STABIL")
        # Print a small snippet
        print("\nSnippet:\n", context[:200], "...")
    else:
        print("❌ INTEGRASI MEMORI: GAGAL")
        print(f"PM: {has_pm}, LT: {has_lt}, ST: {has_st}")

if __name__ == "__main__":
    test_memory()
