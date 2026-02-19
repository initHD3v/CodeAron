from typing import List, Dict, Any, Optional
import os
import json
from src.core.config import settings

class MemoryLayer:
    def __init__(self):
        self.data = []

class MemoryManager:
    """
    1. ShortTermMemory (session-based)
    2. ProjectMemory (repository-based)
    3. LongTermMemory (vector DB)
    """
    def __init__(self, vector_store=None):
        self.short_term = [] # List of past messages in session
        self.project_context = {} 
        self.vector_store = vector_store
        self.max_short_term = 10

    def add_short_term(self, role: str, content: str):
        self.short_term.append({"role": role, "content": content})
        if len(self.short_term) > self.max_short_term:
            self.short_term.pop(0)

    def load_project_memory(self):
        # Load README, .codearon configs, etc.
        readme_path = os.path.join(settings.CURRENT_PROJECT_DIR, "README.md")
        if os.path.exists(readme_path):
            with open(readme_path, 'r') as f:
                self.project_context['readme'] = f.read()[:2000]

    def get_combined_context(self, query: str) -> str:
        # Short Term
        st_text = "\n[SHORT-TERM SESSION]\n" + "\n".join([f"{m['role']}: {m['content']}" for m in self.short_term[-5:]])
        
        # Project Memory
        pm_text = "\n[PROJECT CONTEXT]\n" + (self.project_context.get('readme', 'No README found'))
        
        # Long Term (Vector)
        lt_text = "\n[LONG-TERM MEMORY]\n"
        if self.vector_store:
            results = self.vector_store.search(query, limit=3)
            lt_text += "\n".join([f"File: {r['file_path']}\n{r['content'][:500]}" for r in results])
        
        return f"{pm_text}\n{lt_text}\n{st_text}"

class ContextCompressor:
    """
    Responsibility: Reduce token size of context before sending to LLM.
    Uses summarization or simple pruning.
    """
    def compress(self, context: str, max_tokens: int = 4000) -> str:
        # Heuristic: If context is too long, prune from middle or summarize
        if len(context) < max_tokens * 4: # Roughly 1 token = 4 chars
            return context
        
        lines = context.split("\n")
        # Placeholder for more complex summarization logic
        return "\n".join(lines[:50] + ["... [truncated for token efficiency] ..."] + lines[-50:])
