# 🎯 Skill System Auto-Trigger

**Date**: 2026-03-29  
**Feature**: Auto-Detect & Auto-Run Skill System

---

## 📋 Overview

Skill System sekarang dilengkapi dengan **Auto-Trigger** yang secara otomatis mendeteksi intent user dan menjalankan skill yang sesuai, **tanpa perlu command `/skill`**.

---

## 🆕 vs 🔴 Old

### 🔴 Before (Manual)
```bash
User: "Review file orchestrator.py"
Aron: "Baik, saya akan analisis..."  # Tidak pakai skill

User: "/skill review orchestrator.py"  # <- Harus manual call
Aron: "🚀 Executing skill: review..."
```

### 🆕 After (Auto-Trigger)
```bash
User: "Review file orchestrator.py"
Aron: "🎯 Auto-detected skill: review"
Aron: "🚀 Executing skill: review..."  # <- Otomatis!
```

---

## 🎯 Trigger Keywords

### Review Skill
- `review`, `check`, `audit`, `inspect`, `evaluate`
- `code review`, `periksa`, `tinjau`, `analisis kode`
- `cek error`, `cek bug`, `cari bug`, `temukan masalah`

**Examples:**
```
"Review file ini"
"Check for bugs in main.py"
"Cek error di utils.py"
"Analisis kode orchestrator.py"
```

### Explain Skill
- `explain`, `describe`, `how does`, `what is`
- `jelaskan`, `apa itu`, `bagaimana cara`, `cara kerja`
- `fungsi`, `purpose`, `meaning`, `understand`, `pahami`

**Examples:**
```
"Jelaskan cara kerja function ini"
"Apa itu dependency injection?"
"Bagaimana cara kerja orchestrator?"
"Pahami kode di src/core"
```

### Test Skill
- `test`, `generate tests`, `write tests`
- `buat test`, `buat unit test`, `testing`
- `unit test`, `test coverage`, `buatkan test`

**Examples:**
```
"Buat test untuk utils.py"
"Generate unit tests"
"Test coverage untuk parser.py"
"Buatkan test function ini"
```

### Refactor Skill
- `refactor`, `improve`, `clean up`, `optimize`
- `perbaiki`, `optimasi`, `bersihkan`, `refactor kode`
- `improve quality`, `better code`, `lebih baik`

**Examples:**
```
"Refactor kode ini lebih baik"
"Optimasi function ini"
"Perbaiki kode di legacy.py"
"Clean up this module"
```

---

## 🎯 Target Extraction

Aron secara otomatis extract file path dari user input:

| User Input | Detected Skill | Extracted Target |
|------------|---------------|------------------|
| "Review src/orchestrator.py" | review | `src/orchestrator.py` |
| "Test utils.py" | test | `utils.py` |
| "Jelaskan file main.py" | explain | `main.py` |
| "Refactor kode di src/core" | refactor | `src/core` |
| "Review file ini" | review | _(none, will prompt)_ |

---

## 🏗️ Implementation Details

### Code Changes

#### 1. SKILL_TRIGGERS Dictionary
```python
SKILL_TRIGGERS = {
    "review": ["review", "check", "audit", ...],
    "explain": ["explain", "describe", "jelaskan", ...],
    "test": ["test", "generate tests", "buat test", ...],
    "refactor": ["refactor", "improve", "optimasi", ...],
}
```

#### 2. detect_skill_intent() Method
```python
def detect_skill_intent(self, user_input: str) -> Optional[str]:
    """Detect skill intent dari user input"""
    input_lower = user_input.lower()
    
    for skill_name, triggers in SKILL_TRIGGERS.items():
        for trigger in triggers:
            if trigger in input_lower:
                if self.skill_manager.get_skill(skill_name):
                    return skill_name
    
    return None
```

#### 3. extract_target_from_input() Method
```python
def extract_target_from_input(self, user_input: str) -> Optional[str]:
    """Extract file path dari user input"""
    # Regex patterns untuk extract file paths
    ...
```

#### 4. Integration in run_cycle()
```python
def run_cycle(self, initial_input: str):
    # 1. Greeting check
    # 2. SKILL AUTO-DETECT <- NEW!
    skill_name = self.detect_skill_intent(initial_input)
    if skill_name:
        target = self.extract_target_from_input(initial_input)
        console.print(f"🎯 Auto-detected skill: {skill_name}")
        asyncio.run(self._execute_skill_with_progress(skill_name, target or ""))
        return f"Skill '{skill_name}' executed"
    
    # 3. Simple shell commands
    # 4. Cognitive loop
```

---

## ✅ Test Results

### Intent Detection Tests
```
✅ "Review file ini" -> review
✅ "Jelaskan cara kerja function ini" -> explain
✅ "Buat test untuk utils.py" -> test
✅ "Refactor kode ini lebih baik" -> refactor
✅ "Check for bugs in main.py" -> review
✅ "Apa itu dependency injection?" -> explain
✅ "Generate unit tests" -> test
✅ "Optimasi function ini" -> refactor
✅ "ls -la" -> None (not a skill)
✅ "Halo aron" -> None (not a skill)
```

### Target Extraction Tests
```
✅ "Review src/orchestrator.py" -> src/orchestrator.py
✅ "Test utils.py" -> utils.py
✅ "Jelaskan file main.py" -> main.py
✅ "Refactor kode di src/core" -> src/core
✅ "Halo aron" -> None
```

**All tests: PASSED ✅**

---

## 🎮 Usage Examples

### 1. Code Review
```bash
User: "Review file orchestrator.py"
Aron: 🎯 Auto-detected skill: review
Aron: 🚀 Executing skill: review...
[Skill executes and shows results]
```

### 2. Explain Code
```bash
User: "Jelaskan cara kerja TaskPlanner"
Aron: 🎯 Auto-detected skill: explain
Aron: 🚀 Executing skill: explain...
[Skill explains the concept]
```

### 3. Generate Tests
```bash
User: "Buat test untuk utils.py"
Aron: 🎯 Auto-detected skill: test
Aron: 🚀 Executing skill: test...
[Skill generates tests]
```

### 4. Refactor
```bash
User: "Refactor kode ini lebih baik"
Aron: 🎯 Auto-detected skill: refactor
Aron: 🚀 Executing skill: refactor...
[Skill suggests refactoring]
```

---

## 🔄 Manual Override

Jika user tetap ingin menggunakan command manual:

```bash
/skill review src/orchestrator.py  # Still works!
/skill explain dependency injection  # Still works!
/skill  # List all skills - Still works!
```

---

## 📊 Comparison

| Feature | Manual Mode | Auto-Trigger Mode |
|---------|-------------|-------------------|
| Command | `/skill review file.py` | `Review file.py` |
| Steps | 2+ steps | 1 step |
| UX | Explicit | Natural language |
| Flexibility | High | High + Intuitive |
| Backward Compatible | ✅ | ✅ |

---

## 🚀 Benefits

1. **Natural Language** - User bicara natural, tidak perlu hafal command
2. **Faster Workflow** - Satu command langsung execute
3. **Backward Compatible** - `/skill` command tetap bekerja
4. **Smart Detection** - Context-aware intent detection
5. **Auto Target** - File path otomatis di-extract

---

## 📝 Files Modified

- ✅ `src/core/orchestrator.py`
  - Added `SKILL_TRIGGERS` dictionary
  - Added `detect_skill_intent()` method
  - Added `extract_target_from_input()` method
  - Integrated auto-detect in `run_cycle()`

---

## 🎯 Future Enhancements

- [ ] Multi-language support (Indonesia + English)
- [ ] Fuzzy matching untuk typo tolerance
- [ ] Confidence score untuk intent detection
- [ ] Learning from user feedback
- [ ] Custom trigger keywords via config

---

**Status**: ✅ Production Ready  
**Version**: 2.0.0 (Auto-Trigger)
