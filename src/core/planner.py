from typing import List, Dict, Any
from enum import Enum
import json

class TaskComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"

class TaskPlan:
    def __init__(self, steps: List[str], complexity: TaskComplexity):
        self.steps = steps
        self.complexity = complexity
        self.current_step_index = 0

    def to_json(self):
        return json.dumps({
            "complexity": self.complexity.value,
            "steps": self.steps
        })

class TaskPlanner:
    """
    Responsibility: Breaks down user requests into structured steps.
    Detects task complexity level.
    """
    def __init__(self):
        pass

    def _detect_complexity(self, intent: str) -> TaskComplexity:
        intent_lower = intent.lower()
        if any(word in intent_lower for word in ["refactor", "architect", "add feature", "design"]):
            return TaskComplexity.COMPLEX
        if any(word in intent_lower for word in ["fix", "change", "update", "implement"]):
            return TaskComplexity.MODERATE
        return TaskComplexity.SIMPLE

    def create_plan(self, user_intent: str, context: str) -> TaskPlan:
        complexity = self._detect_complexity(user_intent)
        
        # Base steps for any cognitive agent task
        steps = [
            "Intent Analysis: Understanding user requirements",
            "Project Alignment: Checking README and structural context"
        ]

        if complexity == TaskComplexity.SIMPLE:
            steps.extend([
                "Execution: Performing the direct action",
                "Verification: Confirming result"
            ])
        elif complexity == TaskComplexity.MODERATE:
            steps.extend([
                "Exploration: MUST run 'ls -R' or find to list relevant files",
                "Modification: Applying targeted changes",
                "Validation: Running local checks",
                "Self-Critique: Ensuring no regressions"
            ])
        else:
            steps.extend([
                "Discovery Phase: MUST run recursive directory listing to understand structure",
                "Deep Context Retrieval: MUST read core files (orchestrator.py, memory.py, etc.) via <shell> or <file>",
                "Architectural Audit: Verifying Section 1-12 integration logic",
                "Self-Critique: Checking for potential race conditions or resource leaks",
                "Final Polish: Optimizing and cleaning up"
            ])
        
        return TaskPlan(steps, complexity)
