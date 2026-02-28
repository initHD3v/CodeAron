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
        prompt = "[INST]"
        has_system = any(m['role'] == 'system' for m in messages)
        if system_prompt and not has_system:
            prompt += " <<SYS>>" + system_prompt + "<</SYS>>\n\n"
        for msg in messages:
            role = msg['role']
            content = msg['content']
            if role == 'system':
                prompt += "<<SYS>>" + content + "<</SYS>>\n\n"
            elif role in ('user', 'assistant'):
                prompt += content + "\n"
        prompt += "[/INST]"
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
        tokens = ["<|User|>", "<|Assistant|>", "<｜User｜>", "<｜Assistant｜>"]
        for t in tokens:
            response = response.replace(t, "")
        return response.strip()
