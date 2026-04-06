"""
Benchmark Module untuk CodeAron.
Mengukur performa model AI secara komprehensif.
"""

import time
import re
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field

import psutil
import os

logger = logging.getLogger("Benchmark")


@dataclass
class BenchmarkResult:
    name: str
    status: str  # PASS, FAIL, WARN
    score: float  # 0-100
    metric: str
    value: str
    details: str = ""


@dataclass
class BenchmarkReport:
    results: List[BenchmarkResult] = field(default_factory=list)
    total_time: float = 0.0
    overall_score: float = 0.0

    def add(self, result: BenchmarkResult):
        self.results.append(result)

    def calculate_overall(self):
        if not self.results:
            self.overall_score = 0
            return
        self.overall_score = sum(r.score for r in self.results) / len(self.results)

    def render(self) -> str:
        self.calculate_overall()
        lines = []
        lines.append("")
        lines.append("  CodeAron Benchmark Report")
        lines.append("  " + "━" * 50)

        for r in self.results:
            status_icon = "✅" if r.status == "PASS" else ("⚠️" if r.status == "WARN" else "❌")
            padded_metric = f"{r.metric:<14}"
            lines.append(f"  {status_icon} {padded_metric} {r.value:<12} {r.score:.0f}%")
            if r.details:
                lines.append(f"     {r.details}")

        lines.append("  " + "━" * 50)

        grade = "S" if self.overall_score >= 95 else (
            "A" if self.overall_score >= 85 else (
            "B" if self.overall_score >= 70 else (
            "C" if self.overall_score >= 50 else "D")))

        lines.append(f"  Overall Score: {self.overall_score:.0f}/100  [Grade: {grade}]")
        lines.append(f"  Total Time:  {self.total_time:.1f}s")
        lines.append("  " + "━" * 50)
        return "\n".join(lines)


class BenchmarkSuite:
    """Suite benchmark untuk CodeAron."""

    def __init__(self, orchestrator):
        self.orch = orchestrator
        self.process = psutil.Process(os.getpid())
        self.report = BenchmarkReport()
        self._model_ram = 0.0

    def _get_ram_gb(self) -> float:
        return self.process.memory_info().rss / (1024 ** 3)

    def _measure_model_ram(self):
        """Ukur RAM yang dipakai model."""
        ram_before = self._get_ram_gb()
        # Trigger load model
        if not self.orch.inference.model:
            self.orch.inference.load_model()
        ram_after = self._get_ram_gb()
        self._model_ram = ram_after - ram_before
        return self._model_ram

    def _time_generate(self, prompt: str, task_type: str = "coding") -> Tuple[str, float]:
        """Generate dan ukur waktu."""
        if not self.orch.inference.model:
            self.orch.inference.load_model()

        # Build prompt via template manager
        from src.core.prompt_templates import PromptTemplateManager, ModelFamily
        model_family = PromptTemplateManager.detect_model_family(self.orch.inference.model_path)
        system_prompt = None
        messages = [{"role": "user", "content": prompt}]
        formatted = PromptTemplateManager.build_prompt(messages, model_family, system_prompt)

        start = time.time()
        full_response = ""
        for chunk in self.orch.inference.generate_stream(formatted, task_type=task_type):
            full_response += chunk
        elapsed = time.time() - start

        return full_response, elapsed

    def _count_tokens(self, text: str) -> int:
        """Estimasi token count (1 token ≈ 4 chars)."""
        return max(1, len(text) // 4)

    def run_all(self) -> BenchmarkReport:
        """Jalankan semua test."""
        total_start = time.time()

        self.test_speed_coding()
        self.test_speed_analysis()
        self.test_speed_chat()
        self.test_code_correctness()
        self.test_context_memory()
        self.test_ram_usage()
        self.test_multilingual()

        self.report.total_time = time.time() - total_start
        return self.report

    def test_speed_coding(self):
        """Test kecepatan generate code."""
        name = "Speed (Coding)"
        prompt = "Write a Python function to sort a list of dictionaries by a key."

        response, elapsed = self._time_generate(prompt, "coding")
        tokens_out = self._count_tokens(response)
        tokens_per_sec = tokens_out / elapsed if elapsed > 0 else 0

        # Target: >= 5 tok/s untuk M1 Pro
        if tokens_per_sec >= 15:
            status, score = "PASS", 100
        elif tokens_per_sec >= 10:
            status, score = "PASS", 85
        elif tokens_per_sec >= 5:
            status, score = "WARN", 65
        else:
            status, score = "FAIL", 30

        self.report.add(BenchmarkResult(
            name=name, status=status, score=score,
            metric="Speed (Code)",
            value=f"{tokens_per_sec:.1f} t/s",
            details=f"{tokens_out} tokens in {elapsed:.1f}s"
        ))

    def test_speed_analysis(self):
        """Test kecepatan analysis task."""
        name = "Speed (Analysis)"
        prompt = "Explain the difference between TCP and UDP."

        response, elapsed = self._time_generate(prompt, "analysis")
        tokens_out = self._count_tokens(response)
        tokens_per_sec = tokens_out / elapsed if elapsed > 0 else 0

        if tokens_per_sec >= 15:
            status, score = "PASS", 100
        elif tokens_per_sec >= 10:
            status, score = "PASS", 85
        elif tokens_per_sec >= 5:
            status, score = "WARN", 65
        else:
            status, score = "FAIL", 30

        self.report.add(BenchmarkResult(
            name=name, status=status, score=score,
            metric="Speed (Analysis)",
            value=f"{tokens_per_sec:.1f} t/s",
            details=f"{tokens_out} tokens in {elapsed:.1f}s"
        ))

    def test_speed_chat(self):
        """Test kecepatan casual chat."""
        name = "Speed (Chat)"
        prompt = "Tell me a short joke about programming."

        response, elapsed = self._time_generate(prompt, "chat")
        tokens_out = self._count_tokens(response)
        tokens_per_sec = tokens_out / elapsed if elapsed > 0 else 0

        if tokens_per_sec >= 15:
            status, score = "PASS", 100
        elif tokens_per_sec >= 10:
            status, score = "PASS", 85
        elif tokens_per_sec >= 5:
            status, score = "WARN", 65
        else:
            status, score = "FAIL", 30

        self.report.add(BenchmarkResult(
            name=name, status=status, score=score,
            metric="Speed (Chat)",
            value=f"{tokens_per_sec:.1f} t/s",
            details=f"{tokens_out} tokens in {elapsed:.1f}s"
        ))

    def test_code_correctness(self):
        """Test apakah code yang dihasilkan benar."""
        name = "Code Correctness"
        prompt = """Write a Python function called `fibonacci` that returns the nth Fibonacci number.
Only output the function, nothing else.
"""

        response, elapsed = self._time_generate(prompt, "coding")

        # Check: function definition ada?
        has_def = "def fibonacci" in response or "def fibonacci" in response
        # Check: base case ada?
        has_base = "0" in response or "1" in response
        # Check: recursive/iterative logic ada?
        has_logic = "+" in response or "range" in response or "for " in response or "while " in response

        checks = sum([has_def, has_base, has_logic])
        score = (checks / 3) * 100

        if checks == 3:
            status = "PASS"
        elif checks >= 2:
            status = "WARN"
        else:
            status = "FAIL"

        details_parts = []
        if has_def: details_parts.append("✓ def")
        if has_base: details_parts.append("✓ base case")
        if has_logic: details_parts.append("✓ logic")
        if not details_parts: details_parts.append("✗ nothing valid")

        self.report.add(BenchmarkResult(
            name=name, status=status, score=score,
            metric="Correctness",
            value=f"{checks}/3 checks",
            details=", ".join(details_parts)
        ))

    def test_context_memory(self):
        """Test kemampuan multi-turn context."""
        name = "Context Memory"

        if not self.orch.inference.model:
            self.orch.inference.load_model()

        from src.core.prompt_templates import PromptTemplateManager, ModelFamily
        model_family = PromptTemplateManager.detect_model_family(self.orch.inference.model_path)

        # Turn 1: kasih info
        messages = [{"role": "user", "content": "My favorite color is crimson. Remember this."}]
        formatted = PromptTemplateManager.build_prompt(messages, model_family)
        resp1 = ""
        for chunk in self.orch.inference.generate_stream(formatted, task_type="chat"):
            resp1 += chunk

        # Turn 2: tanya
        messages = [
            {"role": "user", "content": "My favorite color is crimson. Remember this."},
            {"role": "assistant", "content": resp1},
            {"role": "user", "content": "What is my favorite color? Just say the color name."}
        ]
        formatted = PromptTemplateManager.build_prompt(messages, model_family)
        resp2 = ""
        for chunk in self.orch.inference.generate_stream(formatted, task_type="chat"):
            resp2 += chunk

        # Check: apakah ingat "crimson"?
        resp2_lower = resp2.lower()
        remembers = "crimson" in resp2_lower or "red" in resp2_lower

        score = 90 if remembers else 30
        status = "PASS" if remembers else "FAIL"

        self.report.add(BenchmarkResult(
            name=name, status=status, score=score,
            metric="Context",
            value="Yes" if remembers else "No",
            details=f"Answer: {resp2.strip()[:80]}"
        ))

    def test_ram_usage(self):
        """Test pemakaian RAM."""
        name = "RAM Usage"

        model_ram = self._measure_model_ram()
        total_ram = self._get_ram_gb()

        # Threshold: < 4GB = excellent, < 6GB = good, < 8GB = warn, > 8GB = fail
        if model_ram <= 3.0:
            status, score = "PASS", 100
        elif model_ram <= 4.5:
            status, score = "PASS", 80
        elif model_ram <= 6.0:
            status, score = "WARN", 60
        else:
            status, score = "FAIL", 30

        self.report.add(BenchmarkResult(
            name=name, status=status, score=score,
            metric="RAM",
            value=f"{model_ram:.1f}GB",
            details=f"Total process: {total_ram:.1f}GB"
        ))

    def test_multilingual(self):
        """Test kemampuan multilingual (Indonesia)."""
        name = "Multilingual (ID)"
        prompt = "Jelaskan apa itu Python dalam 2 kalimat."

        response, elapsed = self._time_generate(prompt, "analysis")
        tokens_out = self._count_tokens(response)
        tokens_per_sec = tokens_out / elapsed if elapsed > 0 else 0

        # Check: apakah jawab dalam Bahasa Indonesia?
        id_words = sum(1 for w in ["adalah", "dengan", "yang", "untuk", "ini", "dari"] if w in response.lower())

        if id_words >= 3 and tokens_per_sec >= 3:
            status, score = "PASS", 80
        elif id_words >= 2:
            status, score = "WARN", 60
        elif id_words >= 1:
            status, score = "WARN", 40
        else:
            status, score = "FAIL", 20

        self.report.add(BenchmarkResult(
            name=name, status=status, score=score,
            metric="Multilingual",
            value=f"{tokens_per_sec:.1f} t/s",
            details=f"ID words: {id_words}, {tokens_out} tokens in {elapsed:.1f}s"
        ))
