#!/usr/bin/env python3
"""
Memory Profiling Script untuk CodeAron.

Script ini akan:
1. Monitor RAM usage selama sesi Aron
2. Detect potential memory leaks
3. Generate report setelah sesi

Usage:
    python scripts/profile_memory.py
"""

import os
import sys
import time
import tracemalloc
import psutil
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.orchestrator import Orchestrator
from unittest.mock import patch

# ANSI Colors
class Colors:
    RESET = '\033[0m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.RESET}")

def print_info(text):
    print(f"  {text}")

def get_memory_usage():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

def profile_memory_usage():
    """Profile memory usage during Aron session."""
    print_header("CodeAron Memory Profiling")
    
    # Start tracemalloc
    tracemalloc.start()
    
    # Initial memory
    initial_memory = get_memory_usage()
    print_info(f"Initial memory usage: {initial_memory:.2f} MB")
    
    # Track memory over time
    memory_samples = []
    commands = [
        "halo",
        "analisa project ini",
        "ls",
        "cat README.md",
    ]
    
    print_info(f"Running {len(commands)} test commands...\n")
    
    with patch('git.Repo'):
        with patch('questionary.confirm') as mock_confirm:
            mock_confirm.return_value.ask.return_value = True
            
            try:
                orc = Orchestrator()
                
                for i, cmd in enumerate(commands, 1):
                    print_info(f"[{i}/{len(commands)}] Running: {cmd}")
                    
                    # Sample before
                    before = get_memory_usage()
                    
                    try:
                        orc.run_cycle(cmd)
                    except Exception as e:
                        print_warning(f"Command failed (expected in test): {e}")
                    
                    # Sample after
                    after = get_memory_usage()
                    delta = after - before
                    
                    memory_samples.append({
                        'command': cmd,
                        'before': before,
                        'after': after,
                        'delta': delta
                    })
                    
                    status = "↑" if delta > 0 else "↓" if delta < 0 else "→"
                    color = Colors.RED if delta > 10 else Colors.GREEN if delta < 1 else Colors.YELLOW
                    print(f"  {color}Memory: {before:.2f} → {after:.2f} MB ({status} {delta:+.2f} MB){Colors.RESET}\n")
                    
                    # Small delay
                    time.sleep(0.5)
                
                # Final memory
                final_memory = get_memory_usage()
                
            except Exception as e:
                print_error(f"Error during profiling: {e}")
                final_memory = get_memory_usage()
    
    # Get tracemalloc stats
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    
    # Generate report
    print_header("Memory Profiling Report")
    
    total_delta = final_memory - initial_memory
    avg_delta = total_delta / len(commands) if commands else 0
    
    print_info(f"Initial Memory:     {initial_memory:.2f} MB")
    print_info(f"Final Memory:       {final_memory:.2f} MB")
    print_info(f"Total Change:       {Colors.RED if total_delta > 5 else Colors.GREEN}{total_delta:+.2f} MB{Colors.RESET}")
    print_info(f"Average per Command: {avg_delta:+.2f} MB")
    print_info(f"Peak Memory (tracemalloc): {peak / (1024 * 1024):.2f} MB")
    
    # Memory leak detection
    print(f"\n{Colors.BOLD}Memory Leak Analysis:{Colors.RESET}")
    
    if total_delta > 50:
        print_error(f"⚠ POTENTIAL MEMORY LEAK DETECTED!")
        print_info(f"  Memory increased by {total_delta:.2f} MB over {len(commands)} commands")
        print_info(f"  This could indicate:")
        print_info(f"    - Unclosed resources (file handles, DB connections)")
        print_info(f"    - Growing data structures without cleanup")
        print_info(f"    - Circular references preventing GC")
    elif total_delta > 20:
        print_warning(f"⚠ Moderate memory growth detected")
        print_info(f"  Memory increased by {total_delta:.2f} MB")
        print_info(f"  Monitor for extended sessions")
    else:
        print_success("✓ Memory usage stable - no leak detected")
        print_info(f"  Memory change within acceptable range ({total_delta:+.2f} MB)")
    
    # Per-command breakdown
    print(f"\n{Colors.BOLD}Per-Command Breakdown:{Colors.RESET}")
    for sample in memory_samples:
        color = Colors.RED if sample['delta'] > 10 else Colors.GREEN
        print(f"  {sample['command'][:20]:20s} {color}{sample['delta']:+.2f} MB{Colors.RESET}")
    
    # Recommendations
    print(f"\n{Colors.BOLD}Recommendations:{Colors.RESET}")
    if total_delta > 20:
        print_info("1. Check orchestrator._process_actions for resource cleanup")
        print_info("2. Verify vector_store.close() is called on shutdown")
        print_info("3. Check for growing chat_history without limits")
        print_info("4. Run with PYTHONTRACEMALLOC=1 for detailed traceback")
    else:
        print_info("1. Memory management looks good!")
        print_info("2. Continue monitoring for extended sessions")
        print_info("3. Consider adding periodic GC for long sessions")
    
    print(f"\n{Colors.GREEN}Profiling complete!{Colors.RESET}\n")
    
    return {
        'initial': initial_memory,
        'final': final_memory,
        'delta': total_delta,
        'peak': peak,
        'samples': memory_samples
    }

def main():
    print_header("CodeAron Memory Profiling Tool v0.3.0")
    
    # Run profiling
    results = profile_memory_usage()
    
    # Save report
    report_file = Path(__file__).parent.parent / "logs" / f"memory_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report_file, 'w') as f:
        f.write("CodeAron Memory Profiling Report\n")
        f.write("="*50 + "\n\n")
        f.write(f"Initial Memory: {results['initial']:.2f} MB\n")
        f.write(f"Final Memory: {results['final']:.2f} MB\n")
        f.write(f"Total Change: {results['delta']:+.2f} MB\n")
        f.write(f"Peak Memory: {results['peak'] / (1024 * 1024):.2f} MB\n\n")
        f.write("Per-Command Breakdown:\n")
        for sample in results['samples']:
            f.write(f"  {sample['command']}: {sample['delta']:+.2f} MB\n")
    
    print_info(f"Report saved to: {report_file}")
    
    return 0 if results['delta'] < 50 else 1

if __name__ == "__main__":
    sys.exit(main())
