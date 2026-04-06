"""
Chain-of-Thought (CoT) Reasoning Module untuk CodeAron.
Membantu Qwen 7B melakukan reasoning yang lebih terstruktur untuk task kompleks.
"""

from typing import Dict, Any


# Chain-of-Thought template untuk berbagai jenis task kompleks
COT_TEMPLATES = {
    # Template untuk problem solving umum
    "general": """Let's think step by step:

1. UNDERSTAND THE PROBLEM:
   - What is being asked?
   - What are the key requirements?
   - What constraints exist?

2. GATHER INFORMATION:
   - What do I need to observe first?
   - What files/directories should I check?
   - What context is relevant?

3. ANALYZE THE SITUATION:
   - What patterns do I recognize?
   - What are the potential approaches?
   - What are the trade-offs?

4. PLAN THE SOLUTION:
   - What steps should I take?
   - In what order?
   - What could go wrong?

5. EXECUTE THE PLAN:
   - Take action step by step
   - Verify each step
   - Adjust if needed

6. VERIFY THE RESULT:
   - Does this solve the problem?
   - Are there any issues?
   - What about edge cases?

Now, let's solve this problem:
{user_input}
""",

    # Template untuk code analysis/refactoring
    "code_analysis": """Let's analyze this code systematically:

1. CODE UNDERSTANDING:
   - What does this code do?
   - What is the main purpose?
   - What are the key components?

2. STRUCTURE ANALYSIS:
   - How is the code organized?
   - Are there clear separations of concern?
   - What is the dependency structure?

3. QUALITY ASSESSMENT:
   - Code readability (naming, formatting, comments)
   - Code complexity (nested loops, long functions)
   - Potential bugs or issues
   - Performance concerns

4. BEST PRACTICES CHECK:
   - Does it follow language conventions?
   - Are there design pattern opportunities?
   - Error handling adequacy
   - Test coverage

5. REFACTORING OPPORTUNITIES:
   - What can be improved?
   - Priority: High/Medium/Low
   - Effort vs Impact analysis

6. RECOMMENDATIONS:
   - Specific actionable items
   - Code examples where helpful
   - Migration path if needed

Let's analyze:
{user_input}
""",

    # Template untuk architecture design
    "architecture": """Let's design this architecture systematically:

1. REQUIREMENTS ANALYSIS:
   - Functional requirements
   - Non-functional requirements (performance, scalability, security)
   - Constraints (time, resources, technology)

2. SYSTEM BOUNDARIES:
   - What's inside the system?
   - What's external?
   - Interfaces and APIs

3. COMPONENT DESIGN:
   - Major components/modules
   - Responsibilities of each
   - Interactions between components

4. DATA FLOW:
   - How data moves through the system
   - Data storage strategy
   - Data transformation points

5. TECHNOLOGY SELECTION:
   - Programming languages
   - Frameworks and libraries
   - Infrastructure choices
   - Justification for each choice

6. SCALABILITY & MAINTAINABILITY:
   - How to scale horizontally/vertically
   - Monitoring and logging
   - Deployment strategy
   - Maintenance considerations

7. RISK ASSESSMENT:
   - Technical risks
   - Mitigation strategies
   - Fallback plans

Design challenge:
{user_input}
""",

    # Template untuk debugging
    "debugging": """Let's debug this systematically:

1. PROBLEM DEFINITION:
   - What is the expected behavior?
   - What is the actual behavior?
   - When does it occur? (frequency, conditions)

2. INFORMATION GATHERING:
   - Error messages
   - Stack traces
   - Logs
   - Recent changes

3. HYPOTHESIS GENERATION:
   - What could cause this?
   - List all possible causes
   - Rank by likelihood

4. HYPOTHESIS TESTING:
   - Test each hypothesis
   - Add logging/debug statements
   - Isolate the issue

5. ROOT CAUSE IDENTIFICATION:
   - What is the fundamental cause?
   - Why did this happen?
   - Contributing factors

6. SOLUTION DESIGN:
   - Fix the immediate issue
   - Address root cause
   - Prevent recurrence

7. VERIFICATION:
   - Test the fix
   - Check for regressions
   - Update tests if needed

Debug this issue:
{user_input}
""",

    # Template untuk feature implementation
    "feature": """Let's implement this feature systematically:

1. FEATURE UNDERSTANDING:
   - What problem does this solve?
   - Who are the users?
   - What are the success criteria?

2. REQUIREMENTS BREAKDOWN:
   - Must-have features
   - Nice-to-have features
   - Future enhancements

3. TECHNICAL APPROACH:
   - Where does this fit in the existing codebase?
   - What existing code can be reused?
   - What new code is needed?

4. IMPLEMENTATION PLAN:
   - Step 1: ...
   - Step 2: ...
   - Step 3: ...
   - Dependencies between steps

5. CODE STRUCTURE:
   - New files/modules needed
   - Changes to existing files
   - API changes

6. TESTING STRATEGY:
   - Unit tests
   - Integration tests
   - Manual testing scenarios

7. EDGE CASES:
   - Error conditions
   - Boundary conditions
   - Performance considerations

8. DOCUMENTATION:
   - Code comments
   - API documentation
   - User documentation

Implement this feature:
{user_input}
"""
}


class ChainOfThought:
    """
    Chain-of-Thought reasoning engine untuk task kompleks.
    """
    
    @staticmethod
    def get_template(template_type: str) -> str:
        """
        Get CoT template by type.
        
        Args:
            template_type: Type of template (general, code_analysis, architecture, debugging, feature)
        
        Returns:
            CoT template string
        """
        return COT_TEMPLATES.get(template_type, COT_TEMPLATES["general"])
    
    @staticmethod
    def build_cot_prompt(user_input: str, template_type: str = "general", context: str = "") -> str:
        """
        Build complete CoT prompt with context.
        
        Args:
            user_input: User's request/problem
            template_type: Type of CoT template to use
            context: Additional context (project info, previous conversation, etc.)
        
        Returns:
            Complete prompt with CoT reasoning
        """
        template = ChainOfThought.get_template(template_type)
        
        # Add context if provided
        if context:
            full_prompt = f"""CONTEXT:
{context}

---

{template.format(user_input=user_input)}
"""
        else:
            full_prompt = template.format(user_input=user_input)
        
        return full_prompt
    
    @staticmethod
    def detect_complexity(user_input: str, context_length: int = 0) -> tuple[bool, str]:
        """
        Detect if a task requires Chain-of-Thought reasoning.
        
        Args:
            user_input: User's request
            context_length: Length of context (code, files, etc.)
        
        Returns:
            Tuple of (needs_cot: bool, template_type: str)
        """
        input_lower = user_input.lower()
        
        # Keywords untuk complex tasks
        complex_keywords = {
            "architecture": ["architect", "design system", "scalability", "microservice", "distributed"],
            "code_analysis": ["refactor", "code review", "analyze this code", "improve structure"],
            "debugging": ["debug", "fix bug", "error", "not working", "why fails"],
            "feature": ["implement feature", "add functionality", "new feature", "build"],
        }
        
        # Check for complex keywords
        for template_type, keywords in complex_keywords.items():
            if any(keyword in input_lower for keyword in keywords):
                return True, template_type
        
        # Check context length (large context = complex task)
        if context_length > 5000:
            return True, "general"
        
        # Check for multi-step tasks
        multi_step_indicators = ["first", "then", "after that", "finally", "step"]
        if any(indicator in input_lower for indicator in multi_step_indicators):
            return True, "general"
        
        # Default: no CoT needed for simple tasks
        return False, "general"
    
    @staticmethod
    def get_reasoning_steps(template_type: str) -> list[str]:
        """
        Get numbered reasoning steps for a template type.
        
        Args:
            template_type: Type of template
        
        Returns:
            List of step descriptions
        """
        template = ChainOfThought.get_template(template_type)
        
        # Extract step headers
        steps = []
        for line in template.split('\n'):
            if line.strip() and any(line.strip().startswith(num) for num in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.']):
                # Extract the step title
                parts = line.split(':', 1)
                if len(parts) > 1:
                    steps.append(parts[0].strip())
        
        return steps


# Convenience functions
def cot_reasoning(user_input: str, template_type: str = "general", context: str = "") -> str:
    """
    Quick function to build CoT prompt.
    
    Args:
        user_input: User's request
        template_type: Type of CoT template
        context: Additional context
    
    Returns:
        Complete CoT prompt
    """
    return ChainOfThought.build_cot_prompt(user_input, template_type, context)


def needs_cot(user_input: str, context_length: int = 0) -> bool:
    """
    Quick check if task needs CoT.
    
    Args:
        user_input: User's request
        context_length: Length of context
    
    Returns:
        True if CoT is recommended
    """
    needs, _ = ChainOfThought.detect_complexity(user_input, context_length)
    return needs
