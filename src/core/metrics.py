import json
import time
from typing import List, Dict, Any

class MetricsTracker:
    """
    Responsibility: Log structured JSON for each request.
    Track token usage, duration, and state transitions.
    """
    def __init__(self):
        self.start_time: float = 0.0
        self.state_transitions: List[Dict[str, Any]] = []

    def log_transition(self, from_state: str, to_state: str):
        self.state_transitions.append({
            "timestamp": time.time(),
            "from": from_state,
            "to": to_state
        })

    def start_request(self):
        self.start_time = time.time()

    def end_request(self, metadata: Dict[str, Any]) -> str:
        duration = (time.time() - self.start_time) * 1000 if self.start_time > 0 else 0
        log_entry = {
            "intent": metadata.get("intent"),
            "duration_ms": duration,
            "tools_selected": metadata.get("tools_selected", []),
            "model_used": metadata.get("model_used"),
            "confidence": metadata.get("confidence"),
            "retry_count": metadata.get("retry_count", 0),
            "state_transitions": self.state_transitions
        }
        return json.dumps(log_entry, indent=2)
