from typing import Dict, List, Any

class ConfidenceEngine:
    """
    Responsibility: Calculate confidence score based on critic feedback, 
    tool success rate, and retry counts.
    """
    def __init__(self):
        pass

    def calculate_score(self, 
                        critic_severity: float, 
                        tool_success: bool, 
                        retry_count: int,
                        model_certainty: float = 1.0,
                        learning_mode: bool = False) -> float:
        """
        Calculates confidence score [0.0 - 1.0]
        - Critic severity penalty: 0.5 per point
        - Tool failure penalty: 0.3
        - Retry penalty: 0.1 per retry
        """
        score = model_certainty
        
        # Critic Penalty
        score -= (critic_severity * 0.5)
        
        # Tool Failure Penalty
        if not tool_success:
            score -= 0.3
            
        # Retry Penalty
        score -= (retry_count * 0.1)
        
        return max(0.0, min(1.0, score))

    def wrap_response(self, answer: str, metadata: Dict[str, Any]) -> str:
        # Returns a JSON-ready dict for UI/API
        learning_mode = metadata.get("learning_mode", False)
        reasoning = ""
        if learning_mode:
            reasoning = "\n\n[ARON REASONING]\n"
            reasoning += f"● Mode: {metadata.get('model', 'unknown')}\n"
            reasoning += f"● Steps: {metadata.get('iterations', 1)} cycles analyzed.\n"
            reasoning += "● Logic: Used weighted context retrieval to ensure project awareness.\n"
            reasoning += "---"

        result = {
            "answer": f"{answer}{reasoning}",
            "confidence": metadata.get("confidence", 0.0),
            "process": {
                "tools_used": metadata.get("tools_used", []),
                "iterations": metadata.get("iterations", 1),
                "model": metadata.get("model", "unknown")
            },
            "production_ready": metadata.get("confidence", 0.0) > 0.8
        }
        import json
        return json.dumps(result)
