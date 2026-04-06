"""
Prompt Template Manager untuk CodeAron.
"""

from typing import List, Dict, Any
from enum import Enum


class ModelFamily(Enum):
    QWEN = "qwen"
    LLAMA = "llama"
    CHATML = "chatml"
    UNKNOWN = "unknown"


# System prompt yang kuat untuk Aron - Senior Software Architect Persona
ARON_SYSTEM_PROMPT = """You are Aron, a Senior Software Architect AI.

RULES:
1. OBSERVE FIRST - Check project structure before answering
2. BE PRECISE - Technical accuracy > everything
3. NO HALLUCINATION - If unsure, say so. Never fabricate info
4. ACTION ORIENTED - Give executable solutions, not theory
5. CHECK BEFORE SPEAK - Validate empirically before opinions

RESPONSE FORMAT:
- Use markdown with syntax highlighting
- Shell commands in ```bash blocks
- Code in ```language blocks
- Brief explanation before/after action
- Actions > theory

CONSTRAINTS:
- Max 300 words explanation
- Stop after complete solution
- No repetition
- No fluff

LANGUAGE:
- Match the user's language (if user writes in Indonesian, respond in Indonesian)
- If mixed language, use the dominant language
- Technical terms and code stay in English

IDENTITY:
- You are Aron, created by **initHD3v** (also known as initialh)
- You are part of the **CodeAron** project — a 100% local AI coding assistant for Apple Silicon
- You run using **MLX framework** with **Qwen2.5/DeepSeek** models
- Your name comes from the **Karo tribe** tradition: "Aron" = collaborative work group
- You are a Senior Software Architect AI — professional, direct, solution-focused

PERSONA:
- Professional, direct
- Solution-focused
- No rambling

EXAMPLES:

User: "How do I list files in current directory?"
Aron: Use the `ls` command:

```bash
ls -la
```

This shows all files including hidden ones with details.

---

User: "Fix the syntax error in src/main.py"
Aron: Let me check the file first.

```bash
cat src/main.py
```

[After reading file] Found missing colon on line 5. Here's the fix:

```python
def greet(name):
    print(f"Hello, {name}!")
```

---

User: "What does this function do? def factorial(n): return 1 if n <= 1 else n * factorial(n-1)"
Aron: This is a **recursive factorial** function.

- **Base case**: returns 1 when n <= 1
- **Recursive case**: returns n * factorial(n-1)
- **Time complexity**: O(n)
- **Space complexity**: O(n) due to call stack

Warning: Will hit recursion limit for n > 1000 in Python.
"""


class PromptTemplateManager:
    @staticmethod
    def detect_model_family(model_path: str) -> ModelFamily:
        model_name = model_path.lower()
        if "qwen" in model_name:
            return ModelFamily.QWEN
        elif "llama" in model_name:
            return ModelFamily.LLAMA
        return ModelFamily.CHATML
    
    @staticmethod
    def build_prompt(messages: List[Dict[str, str]], model_family: ModelFamily, system_prompt: str = None) -> str:
        if model_family == ModelFamily.QWEN:
            return PromptTemplateManager._build_qwen(messages, system_prompt)
        elif model_family == ModelFamily.LLAMA:
            return PromptTemplateManager._build_llama(messages, system_prompt)
        return PromptTemplateManager._build_chatml(messages, system_prompt)
    
    @staticmethod
    def _build_qwen(messages: List[Dict[str, str]], system_prompt: str = None) -> str:
        """
        Build prompt menggunakan ChatML format (standar Qwen2.5).
        Format: <|im_start|>{role}\n{content}<|im_end|>\n
        """
        if system_prompt is None:
            system_prompt = ARON_SYSTEM_PROMPT

        prompt = ""
        has_system = any(m['role'] == 'system' for m in messages)

        # System message (pertama kali, sebelum messages lain)
        if system_prompt and not has_system:
            prompt += "<|im_start|>system\n" + system_prompt + "<|im_end|>\n"

        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                prompt += "<|im_start|>system\n" + content + "<|im_end|>\n"
            elif role == 'user':
                prompt += "<|im_start|>user\n" + content + "<|im_end|>\n"
            elif role == 'assistant':
                prompt += "<|im_start|>assistant\n" + content + "<|im_end|>\n"

        # Akhiri dengan assistant header (model akan lanjut dari sini)
        prompt += "<|im_start|>assistant\n"
        return prompt
    
    @staticmethod
    def _build_llama(messages: List[Dict[str, str]], system_prompt: str = None) -> str:
        prompt = "<|begin_of_text|>"
        has_system = any(m['role'] == 'system' for m in messages)
        if system_prompt and not has_system:
            prompt += "<|start_header_id|>system<|end_header_id|>\n\n"
            prompt += system_prompt + "<|eot_id|>"
        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                prompt += "<|start_header_id|>system<|end_header_id|>\n\n"
                prompt += content + "<|eot_id|>"
            elif role == 'user':
                prompt += "<|start_header_id|>user<|end_header_id|>\n\n"
                prompt += content + "<|eot_id|>"
            elif role == 'assistant':
                prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
                prompt += content + "<|eot_id|>"
        prompt += "<|start_header_id|>assistant<|end_header_id|>\n\n"
        return prompt
    
    @staticmethod
    def _build_chatml(messages: List[Dict[str, str]], system_prompt: str = None) -> str:
        prompt = ""
        for msg in messages:
            role = msg['role']
            content = msg['content']
            prompt += role + ": " + content + "\n"
        return prompt
    
    @staticmethod
    def sanitize_output(response: str) -> str:
        """Hapus token artifacts dari output model."""
        # ChatML special tokens
        chatml_tokens = [
            "<|im_end|>", "<|im_start|>",
            "<|User|>", "<|Assistant|>",
            "<｜User｜>", "<｜Assistant｜>",
            "<|end_of_sentence|>",
        ]
        for t in chatml_tokens:
            response = response.replace(t, "")

        # Hapus trailing special tokens di awal/akhir
        import re
        response = re.sub(r'^\s*<\|.*?\|>\s*', '', response)
        response = re.sub(r'\s*<\|.*?\|>\s*$', '', response)

        return response.strip()
