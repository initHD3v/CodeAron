#!/usr/bin/env python3
"""
Manual test untuk observasi response Aron.
Jalankan dan perhatikan output untuk deteksi:
1. Halusinasi
2. Loop tidak penting  
3. Execution failure
"""

import sys
import os

# Add src path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.orchestrator import Orchestrator
from unittest.mock import patch

def test_aron_responses():
    print("="*70)
    print(" CODEARON MANUAL TESTING - OBSERVATION MODE")
    print("="*70)
    print()
    
    test_cases = [
        ("Greeting", "halo"),
        ("Simple LS", "ls"),
        ("Analysis", "analisa projek ini"),
        ("File Read", "cat README.md"),
    ]
    
    with patch('git.Repo'):
        with patch('questionary.confirm', return_value=type('obj', (object,), {'ask': lambda: True})()):
            orc = Orchestrator()
            
            for name, command in test_cases:
                print(f"\n{'='*70}")
                print(f" TEST: {name}")
                print(f" INPUT: {command}")
                print(f"{'='*70}")
                
                try:
                    result = orc.run_cycle(command)
                    
                    print(f"\n✅ EXECUTION SUCCESS")
                    print(f"Response type: {type(result)}")
                    
                    # Check for hallucination indicators
                    if result:
                        result_str = str(result).lower()
                        
                        hallucination_signs = [
                            "i can't", "i cannot", "unable to", "don't have access",
                            "tidak bisa", "tidak dapat"
                        ]
                        
                        loop_signs = [
                            "putaran 1", "putaran 2", "putaran 3", "putaran 4", "putaran 5"
                        ]
                        
                        failure_signs = [
                            "gagal", "error", "failed", "exception"
                        ]
                        
                        has_hallucination = any(sign in result_str for sign in hallucination_signs)
                        has_loop = any(sign in result_str for sign in loop_signs)
                        has_failure = any(sign in result_str for sign in failure_signs)
                        
                        if has_hallucination:
                            print("⚠️  WARNING: Potential hallucination detected!")
                        if has_loop:
                            print("⚠️  WARNING: Potential loop detected!")
                        if has_failure:
                            print("⚠️  WARNING: Execution failure detected!")
                        
                        if not (has_hallucination or has_loop or has_failure):
                            print("✅ No issues detected in response")
                    
                except Exception as e:
                    print(f"\n❌ EXECUTION FAILED")
                    print(f"Error: {e}")
                    import traceback
                    traceback.print_exc()
                
                print()
            
            # Final test - quit
            print(f"\n{'='*70}")
            print(" TEST: Exit")
            print(f" INPUT: /quit")
            print(f"{'='*70}")
            orc._shutdown()

if __name__ == "__main__":
    test_aron_responses()
