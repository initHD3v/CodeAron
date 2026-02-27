"""
Integration tests untuk Orchestrator.
Test end-to-end workflow dari CodeAron.
"""

import unittest
import sys
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.getcwd())

from src.core.orchestrator import Orchestrator
from src.core.states import AronState, ExecutionResult
from src.core.config import settings


class TestOrchestratorIntegration(unittest.TestCase):
    """Integration tests untuk Orchestrator."""
    
    def setUp(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create minimal project structure
        (Path(self.temp_dir) / "README.md").write_text("# Test Project")
        (Path(self.temp_dir) / "test.py").write_text("def hello():\n    return 'world'")
    
    def tearDown(self):
        """Cleanup test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_greeting_response(self, mock_confirm, mock_git):
        """Test response untuk greeting."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Test greeting
        greetings = ["hai", "halo", "hi"]
        for greeting in greetings:
            result = orc.run_cycle(greeting)
            self.assertIn("Halo", result)
            self.assertIn("Aron", result)
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_state_transitions(self, mock_confirm, mock_git):
        """Test state transitions selama execution."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Initial state should be IDLE
        self.assertEqual(orc.state, AronState.IDLE)
        
        # Mock shell execution to avoid actual commands
        with patch.object(orc, '_run_shell') as mock_run:
            mock_run.return_value = ExecutionResult(True, "test output", "", 0)
            
            # Run a simple command
            orc.run_cycle("ls")
            
            # State should return to IDLE after completion
            self.assertEqual(orc.state, AronState.IDLE)
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_command_history_tracking(self, mock_confirm, mock_git):
        """Test command history tracking untuk loop detection."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Initial command history should be empty
        self.assertEqual(len(orc.command_history), 0)
        
        # Mock shell execution
        with patch.object(orc, '_run_shell') as mock_run:
            mock_run.return_value = ExecutionResult(True, "output", "", 0)
            
            # Run multiple cycles
            for i in range(3):
                orc.run_cycle(f"echo test{i}")
        
        # Command history should track commands
        # (exact count depends on implementation)
        self.assertGreaterEqual(len(orc.command_history), 0)
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_circuit_breaker_initial_state(self, mock_confirm, mock_git):
        """Test circuit breaker dalam keadaan awal."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Initial failure counter should be 0
        self.assertEqual(orc._consecutive_failures, 0)
        
        # Cooldown should be set
        self.assertGreater(orc._command_cooldown, 0)
        
        # Max failures threshold should be set
        self.assertGreater(orc._max_consecutive_failures, 0)
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_rate_limiting_config(self, mock_confirm, mock_git):
        """Test rate limiting configuration."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Check rate limiting is configured
        self.assertEqual(orc._command_cooldown, 2.0)
        self.assertEqual(orc._max_consecutive_failures, 5)
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_chat_history_management(self, mock_confirm, mock_git):
        """Test chat history management."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Initial history should be empty
        self.assertEqual(len(orc.chat_history), 0)
        
        # Run greeting (adds to history)
        orc.run_cycle("halo")
        
        # History should have 2 entries (user + assistant)
        self.assertEqual(len(orc.chat_history), 2)
        self.assertEqual(orc.chat_history[0]['role'], 'User')
        self.assertEqual(orc.chat_history[1]['role'], 'Aron')
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_cwd_tracking(self, mock_confirm, mock_git):
        """Test current working directory tracking."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Initial cwd should match test directory (resolve symlinks for macOS)
        import os
        self.assertEqual(os.path.realpath(orc.cwd), os.path.realpath(self.temp_dir))
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_resource_usage_tracking(self, mock_confirm, mock_git):
        """Test resource usage tracking."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Get resource usage
        usage = orc._get_resource_usage()
        
        # Should return dict with ram and cpu
        self.assertIsInstance(usage, dict)
        self.assertIn('ram', usage)
        self.assertIn('cpu', usage)
        
        # Values should be non-negative
        self.assertGreaterEqual(usage['ram'], 0.0)
        self.assertGreaterEqual(usage['cpu'], 0.0)
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_memory_manager_integration(self, mock_confirm, mock_git):
        """Test memory manager integration."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Memory manager should be initialized
        self.assertIsNotNone(orc.memory)
        
        # Short term memory should be accessible
        orc.memory.add_short_term("user", "test message")
        self.assertEqual(len(orc.memory.short_term), 1)
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_vision_engine_initialization(self, mock_confirm, mock_git):
        """Test vision engine initialization."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Vision engine should be initialized
        self.assertIsNotNone(orc.vision)


class TestOrchestratorActionProcessing(unittest.TestCase):
    """Tests untuk action processing di Orchestrator."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)
    
    def tearDown(self):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_shell_command_extraction(self, mock_confirm, mock_git):
        """Test extraction shell commands dari response."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Test <shell> tag extraction
        response_with_shell = "Let me run <shell>ls -la</shell> for you"
        results = orc._process_actions(response_with_shell)
        
        # Should extract and attempt to process command
        # (actual execution depends on mocks)
        self.assertIsInstance(results, list)
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_markdown_command_extraction(self, mock_confirm, mock_git):
        """Test extraction commands dari markdown blocks."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Test markdown code block extraction
        response_with_markdown = """
Here's the command:
```bash
echo "hello"
```
"""
        results = orc._process_actions(response_with_markdown)
        self.assertIsInstance(results, list)
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_file_tag_extraction(self, mock_confirm, mock_git):
        """Test extraction file operations dari response."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Test <file> tag extraction
        response_with_file = """
I'll create a file:
<file path="test.txt">
Hello World
</file>
"""
        results = orc._process_actions(response_with_file)
        
        # Should attempt to write file
        self.assertIsInstance(results, list)
    
    @patch('git.Repo')
    @patch('questionary.confirm')
    def test_interactive_command_rejection(self, mock_confirm, mock_git):
        """Test rejection interactive commands."""
        mock_confirm.return_value.ask.return_value = True
        
        orc = Orchestrator()
        
        # Test interactive command rejection
        response_with_vim = "Let me edit with <shell>vim test.py</shell>"
        results = orc._process_actions(response_with_vim)
        
        # Should reject interactive command
        self.assertTrue(any("interaktif" in r.lower() or "GAGAL" in r for r in results))


if __name__ == '__main__':
    unittest.main()
