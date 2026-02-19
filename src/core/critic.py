from typing import Dict, Any, List
import json

class CriticFeedback:
    def __init__(self, is_valid: bool, flaws: List[str], severity_score: float, confidence_score: float):
        self.is_valid = is_valid
        self.flaws = flaws
        self.severity_score = severity_score
        self.confidence_score = confidence_score

class SelfCritic:
    """
    Responsibility: Evaluates output for flaws, inefficiencies, or incorrect logic.
    Returns structured feedback.
    """
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def evaluate(self, user_input: str, response: str) -> CriticFeedback:
        flaws: List[str] = []
        severity: float = 0.0
        
        # 1. Structural Tags check
        if "<shell>" in response and "</shell>" not in response:
            flaws.append("Missing closing </shell> tag.")
            severity += 0.8
            
        if "<file" in response and "</file>" not in response:
            flaws.append("Missing closing </file> tag.")
            severity += 0.8

        # 2. Hallucination Detection
        internal_tokens = ["<｜User｜>", "<｜Assistant｜>", "Assistant:"]
        for token in internal_tokens:
            if token in response:
                flaws.append(f"Hallucination: Internal token '{token}' leaked into response.")
                severity += 0.5

        # 3. Conciseness check
        if len(response) < 10 and "<shell>" not in response:
            flaws.append("Response is too brief/empty.")
            severity += 0.3

        # 4. Logical check placeholder
        if "I don't have access" in response and "file" in response.lower():
            flaws.append("False refusal: Agent claims no access despite local execution environment.")
            severity += 0.6

        return CriticFeedback(
            is_valid=(severity < 0.5),
            flaws=flaws,
            severity_score=severity,
            confidence_score=0.9 - (len(flaws) * 0.1)
        )

    def needs_refinement(self, feedback: CriticFeedback) -> bool:
        return feedback.severity_score > self.threshold
