from typing import List, Dict, Any, Optional

class ToolRouter:
    """
    Responsibility: Scores and ranks tools dynamically.
    Selects primary + fallback tools.
    """
    def __init__(self):
        self.tools = {
            "shell": {"score": 0.8, "desc": "Execute system commands"},
            "file_patcher": {"score": 0.9, "desc": "Modify or create files"},
            "qdrant": {"score": 0.7, "desc": "Search semantic memory"}
        }
        self.models = {
            "fast": "deepseek-coder-v2-lite-instruct",
            "heavy": "deepseek-v3", # Placeholder for larger model
            "summarizer": "gemma-2b"
        }

    def route(self, intent: str, context: str) -> Dict[str, Any]:
        intent_lower = intent.lower()
        
        # 1. Tool Selection Logic
        if any(word in intent_lower for word in ["run", "list", "show", "search"]):
            primary_tool = "shell"
        elif any(word in intent_lower for word in ["write", "create", "modify", "fix"]):
            primary_tool = "file_patcher"
        else:
            primary_tool = "shell" if "file" not in intent_lower else "file_patcher"

        # 2. Model Routing Logic
        # Direct complexity-based routing
        if any(word in intent_lower for word in ["architect", "redesign", "complex", "review"]):
            selected_model = self.models["heavy"]
            reasoning_depth = "deep"
        elif len(context) > 10000: # Context is heavy
            selected_model = self.models["heavy"]
            reasoning_depth = "moderate"
        else:
            selected_model = self.models["fast"]
            reasoning_depth = "standard"

        return {
            "primary_tool": primary_tool,
            "fallback_tool": "shell" if primary_tool != "shell" else None,
            "selected_model": selected_model,
            "reasoning_depth": reasoning_depth,
            "confidence": 0.92
        }

    def get_retry_strategy(self, tool_name: str) -> Dict[str, Any]:
        return {
            "max_retries": 3,
            "backoff": "exponential"
        }
