"""
Skill Executor untuk CodeAron
Menjalankan skills dengan multi-agent pattern
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from .skill_manager import SkillDefinition, get_skill_manager

logger = logging.getLogger("SkillExecutor")


class SkillStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SkillResult:
    """Hasil execution skill"""
    skill_name: str
    status: SkillStatus
    output: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0
    steps_completed: int = 0
    findings: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.findings is None:
            self.findings = []


class SkillExecutor:
    """
    Executor untuk menjalankan skills
    
    Mendukung:
    - Single agent execution
    - Multi-agent parallel execution (untuk review, dll)
    - Progress tracking
    - Cancellation
    """
    
    def __init__(self, orchestrator=None):
        self.orchestrator = orchestrator
        self.skill_manager = get_skill_manager()
        self._current_execution: Optional[SkillResult] = None
        self._cancelled = False
    
    async def execute_skill(
        self,
        skill_name: str,
        target: Optional[str] = None,
        context: Optional[str] = None,
        auto_confirm: bool = False
    ) -> SkillResult:
        """
        Execute skill
        
        Args:
            skill_name: Nama skill untuk dijalankan
            target: Target skill (file path, function name, dll)
            context: Additional context dari user
            auto_confirm: Skip confirmation untuk destructive operations
        
        Returns:
            SkillResult dengan output execution
        """
        import time
        start_time = time.time()
        
        skill = self.skill_manager.get_skill(skill_name)
        if not skill:
            return SkillResult(
                skill_name=skill_name,
                status=SkillStatus.FAILED,
                error=f"Skill '{skill_name}' not found"
            )
        
        self._cancelled = False
        self._current_execution = SkillResult(
            skill_name=skill_name,
            status=SkillStatus.RUNNING
        )
        
        logger.info(f"Executing skill: {skill_name} on {target or 'general'}")
        
        try:
            # Check if confirmation needed
            if not auto_confirm and not skill.auto_execute:
                if not await self._request_confirmation(skill, target):
                    self._current_execution.status = SkillStatus.CANCELLED
                    return self._current_execution
            
            # Execute based on skill type
            if skill_name == "review":
                result = await self._execute_review(skill, target, context)
            elif skill_name == "explain":
                result = await self._execute_explain(skill, target, context)
            elif skill_name == "test":
                result = await self._execute_test(skill, target, context)
            elif skill_name == "refactor":
                result = await self._execute_refactor(skill, target, context)
            else:
                result = await self._execute_generic(skill, target, context)
            
            result.execution_time = time.time() - start_time
            result.status = SkillStatus.COMPLETED
            self._current_execution = result
            return result
            
        except asyncio.CancelledError:
            self._current_execution.status = SkillStatus.CANCELLED
            self._current_execution.error = "Execution cancelled by user"
            return self._current_execution
            
        except Exception as e:
            logger.error(f"Skill execution failed: {e}")
            self._current_execution.status = SkillStatus.FAILED
            self._current_execution.error = str(e)
            self._current_execution.execution_time = time.time() - start_time
            return self._current_execution
    
    async def _request_confirmation(self, skill: SkillDefinition, target: Optional[str]) -> bool:
        """Request user confirmation sebelum execute"""
        if not self.orchestrator:
            return True  # Auto-confirm jika tidak ada orchestrator
        
        # Tampilkan preview apa yang akan dilakukan
        preview = f"**Skill**: {skill.name}\n"
        preview += f"**Description**: {skill.description}\n"
        if target:
            preview += f"**Target**: {target}\n"
        preview += f"**Tools yang akan digunakan**: {', '.join(skill.allowed_tools)}\n"
        
        # Gunakan orchestrator untuk prompt
        # Note: Ini akan diimplementasi di orchestrator integration
        return True  # Default auto-confirm untuk sekarang
    
    async def _execute_review(
        self,
        skill: SkillDefinition,
        target: Optional[str],
        context: Optional[str]
    ) -> SkillResult:
        """Execute review skill dengan multi-agent pattern"""
        from src.tools.validator import ValidationEngine
        
        result = SkillResult(skill_name=skill.name, status=SkillStatus.RUNNING)
        
        # Step 1: Gather code to review
        code_content = await self._gather_code_content(target)
        if not code_content:
            result.error = "No code found to review"
            result.status = SkillStatus.FAILED
            return result
        
        # Step 2: Launch parallel review agents
        agents = [
            ("Correctness & Security", self._review_correctness),
            ("Code Quality", self._review_quality),
            ("Performance", self._review_performance),
            ("Design & Architecture", self._review_design),
        ]
        
        findings = []
        for agent_name, agent_func in agents:
            agent_result = await agent_func(code_content, target)
            if agent_result:
                findings.extend(agent_result)
                result.steps_completed += 1
        
        # Step 3: Compile findings
        output = self._compile_review_findings(findings, target, code_content)
        result.output = output
        result.findings = findings
        
        return result
    
    async def _review_correctness(self, code: str, target: Optional[str]) -> List[Dict]:
        """Review untuk correctness dan security"""
        findings = []
        
        # Check untuk common security issues
        security_patterns = [
            (r'eval\s*\(', 'Use of eval() is dangerous'),
            (r'exec\s*\(', 'Use of exec() is dangerous'),
            (r'__import__\s*\(', 'Dynamic import detected'),
            (r'os\.system\s*\(', 'OS command injection risk'),
            (r'subprocess\..*shell\s*=\s*True', 'Shell injection risk'),
        ]
        
        import re
        for pattern, issue in security_patterns:
            if re.search(pattern, code):
                findings.append({
                    "severity": "critical",
                    "category": "security",
                    "issue": issue,
                    "suggestion": "Avoid dynamic code execution"
                })
        
        # Check untuk error handling
        if 'try' not in code and len(code) > 100:
            findings.append({
                "severity": "suggestion",
                "category": "error_handling",
                "issue": "No error handling detected",
                "suggestion": "Add try-except blocks for robustness"
            })
        
        return findings
    
    async def _review_quality(self, code: str, target: Optional[str]) -> List[Dict]:
        """Review untuk code quality"""
        findings = []
        
        lines = code.split('\n')
        
        # Check line length
        long_lines = [i for i, line in enumerate(lines) if len(line) > 120]
        if long_lines:
            findings.append({
                "severity": "nice_to_have",
                "category": "style",
                "issue": f"{len(long_lines)} lines exceed 120 characters",
                "suggestion": "Break long lines for readability"
            })
        
        # Check function length
        if len(lines) > 100:
            findings.append({
                "severity": "suggestion",
                "category": "maintainability",
                "issue": "File is large (>100 lines)",
                "suggestion": "Consider splitting into smaller modules"
            })
        
        # Check for docstrings
        if '"""' not in code and "'''" not in code:
            findings.append({
                "severity": "suggestion",
                "category": "documentation",
                "issue": "No docstrings found",
                "suggestion": "Add docstrings to document code"
            })
        
        return findings
    
    async def _review_performance(self, code: str, target: Optional[str]) -> List[Dict]:
        """Review untuk performance"""
        findings = []
        
        # Check untuk inefficient patterns
        if '.append(' in code and 'for' in code:
            findings.append({
                "severity": "nice_to_have",
                "category": "performance",
                "issue": "List comprehension might be faster than append in loop",
                "suggestion": "Consider using list comprehension"
            })
        
        if 'time.sleep' in code:
            findings.append({
                "severity": "suggestion",
                "category": "performance",
                "issue": "Blocking sleep detected",
                "suggestion": "Consider async sleep for non-blocking wait"
            })
        
        return findings
    
    async def _review_design(self, code: str, target: Optional[str]) -> List[Dict]:
        """Review untuk design dan architecture"""
        findings = []
        
        # Check untuk tight coupling
        import_count = code.count('import ')
        if import_count > 10:
            findings.append({
                "severity": "suggestion",
                "category": "design",
                "issue": f"Many imports ({import_count})",
                "suggestion": "Consider if all dependencies are necessary"
            })
        
        # Check untuk god classes
        class_count = code.count('class ')
        if class_count == 1 and len(code.split('\n')) > 500:
            findings.append({
                "severity": "suggestion",
                "category": "design",
                "issue": "Large class detected",
                "suggestion": "Consider splitting into smaller classes"
            })
        
        return findings
    
    def _compile_review_findings(
        self,
        findings: List[Dict],
        target: Optional[str],
        code: str
    ) -> str:
        """Compile findings menjadi formatted review"""
        output = "## 🔍 Code Review Results\n\n"
        
        # Summary
        critical = len([f for f in findings if f.get('severity') == 'critical'])
        suggestions = len([f for f in findings if f.get('severity') == 'suggestion'])
        nice_to_have = len([f for f in findings if f.get('severity') == 'nice_to_have'])
        
        output += f"**Target**: {target or 'Uncommitted changes'}\n"
        lines_of_code = len(code.split('\n'))
        output += f"**Lines of code**: {lines_of_code}\n\n"
        
        output += "### Summary\n"
        output += f"- 🔴 Critical: {critical}\n"
        output += f"- 🟡 Suggestions: {suggestions}\n"
        output += f"- 🔵 Nice to have: {nice_to_have}\n\n"
        
        if not findings:
            output += "✅ No issues found! Code looks good.\n"
            return output
        
        # Group by severity
        output += "### Findings\n\n"
        
        for severity in ['critical', 'suggestion', 'nice_to_have']:
            severity_findings = [f for f in findings if f.get('severity') == severity]
            if not severity_findings:
                continue
            
            emoji = {'critical': '🔴', 'suggestion': '🟡', 'nice_to_have': '🔵'}[severity]
            output += f"#### {emoji} {severity.replace('_', ' ').title()}\n\n"
            
            for finding in severity_findings:
                output += f"- **{finding.get('category', 'general').title()}**: {finding.get('issue')}\n"
                output += f"  - 💡 {finding.get('suggestion', 'No suggestion')}\n\n"
        
        # Verdict
        output += "### Verdict\n\n"
        if critical > 0:
            output += "❌ **Request changes** - Critical issues must be fixed before merging."
        elif suggestions > 2:
            output += "💬 **Comment** - Several suggestions for improvement."
        else:
            output += "✅ **Approve** - No critical issues, good to merge."
        
        return output
    
    async def _execute_explain(
        self,
        skill: SkillDefinition,
        target: Optional[str],
        context: Optional[str]
    ) -> SkillResult:
        """Execute explain skill"""
        result = SkillResult(skill_name=skill.name, status=SkillStatus.RUNNING)
        
        # Gather content
        content = await self._gather_content(target)
        if not content:
            result.error = "No content found to explain"
            result.status = SkillStatus.FAILED
            return result
        
        # Generate explanation
        explanation = await self._generate_explanation(content, target, context)
        result.output = explanation
        result.steps_completed = 1
        
        return result
    
    async def _execute_test(
        self,
        skill: SkillDefinition,
        target: Optional[str],
        context: Optional[str]
    ) -> SkillResult:
        """Execute test generation skill"""
        result = SkillResult(skill_name=skill.name, status=SkillStatus.RUNNING)
        
        # Gather code to test
        code = await self._gather_code_content(target)
        if not code:
            result.error = "No code found to generate tests for"
            result.status = SkillStatus.FAILED
            return result
        
        # Generate tests
        tests = await self._generate_tests(code, target)
        result.output = tests
        result.steps_completed = 1
        
        return result
    
    async def _execute_refactor(
        self,
        skill: SkillDefinition,
        target: Optional[str],
        context: Optional[str]
    ) -> SkillResult:
        """Execute refactor skill"""
        result = SkillResult(skill_name=skill.name, status=SkillStatus.RUNNING)
        
        # Gather code to refactor
        code = await self._gather_code_content(target)
        if not code:
            result.error = "No code found to refactor"
            result.status = SkillStatus.FAILED
            return result
        
        # Analyze and suggest refactorings
        refactor_plan = await self._analyze_refactoring(code, target, context)
        result.output = refactor_plan
        result.steps_completed = 1
        
        return result
    
    async def _execute_generic(
        self,
        skill: SkillDefinition,
        target: Optional[str],
        context: Optional[str]
    ) -> SkillResult:
        """Execute generic skill menggunakan LLM"""
        result = SkillResult(skill_name=skill.name, status=SkillStatus.RUNNING)
        
        # Fallback ke LLM untuk custom skills
        if self.orchestrator and hasattr(self.orchestrator, 'inference'):
            prompt = self._build_skill_prompt(skill, target, context)
            response = await self._call_llm(prompt)
            result.output = response
            result.steps_completed = 1
        else:
            result.error = "No LLM available for generic skill execution"
            result.status = SkillStatus.FAILED
        
        return result
    
    # Helper methods
    
    async def _gather_code_content(self, target: Optional[str]) -> Optional[str]:
        """Gather code content dari target"""
        if not target:
            # Get from git diff
            return await self._get_git_diff()
        
        if self.orchestrator and hasattr(self.orchestrator, 'cwd'):
            target_path = target if target.startswith('/') else f"{self.orchestrator.cwd}/{target}"
            if os.path.exists(target_path):
                with open(target_path, 'r') as f:
                    return f.read()
        
        return None
    
    async def _gather_content(self, target: Optional[str]) -> Optional[str]:
        """Gather content (alias untuk backward compatibility)"""
        return await self._gather_code_content(target)
    
    async def _get_git_diff(self) -> Optional[str]:
        """Get git diff dari uncommitted changes"""
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'diff', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout if result.stdout else None
        except Exception:
            return None
    
    def _build_skill_prompt(
        self,
        skill: SkillDefinition,
        target: Optional[str],
        context: Optional[str]
    ) -> str:
        """Build prompt untuk LLM"""
        prompt = f"Execute the following skill:\n\n"
        prompt += f"**Skill**: {skill.name}\n"
        prompt += f"**Description**: {skill.description}\n"
        if target:
            prompt += f"**Target**: {target}\n"
        if context:
            prompt += f"**Context**: {context}\n"
        prompt += f"\n**Instructions**:\n{skill.instructions}\n"
        return prompt
    
    async def _call_llm(self, prompt: str) -> str:
        """Call LLM untuk execute skill"""
        if not self.orchestrator:
            return "LLM not available"
        
        # Use orchestrator's inference engine
        # This will be implemented in orchestrator integration
        return "LLM execution placeholder"
    
    async def _generate_explanation(self, content: str, target: Optional[str], context: Optional[str]) -> str:
        """Generate explanation untuk code"""
        # Placeholder - akan diimplementasi dengan LLM
        return f"## Explanation for {target or 'code'}\n\n[Explanation would be generated here using LLM]"
    
    async def _generate_tests(self, code: str, target: Optional[str]) -> str:
        """Generate tests untuk code"""
        # Placeholder - akan diimplementasi dengan LLM
        return f"# Tests for {target or 'code'}\n\n[Tests would be generated here using LLM]"
    
    async def _analyze_refactoring(self, code: str, target: Optional[str], context: Optional[str]) -> str:
        """Analyze dan suggest refactorings"""
        # Placeholder - akan diimplementasi dengan LLM
        return f"# Refactoring Plan for {target or 'code'}\n\n[Refactoring suggestions would be generated here using LLM]"
    
    def cancel(self):
        """Cancel current execution"""
        self._cancelled = True
        logger.info("Skill execution cancelled")


# Singleton instance
_executor: Optional[SkillExecutor] = None

def get_skill_executor(orchestrator=None) -> SkillExecutor:
    """Get singleton SkillExecutor instance"""
    global _executor
    if _executor is None:
        _executor = SkillExecutor(orchestrator)
    return _executor
