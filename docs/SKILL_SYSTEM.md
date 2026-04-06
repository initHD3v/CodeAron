# 📚 CodeAron Skill System

## Overview

Skill System adalah framework untuk specialized agents di CodeAron. Setiap skill adalah agent otonom yang dirancang untuk menyelesaikan task spesifik dengan kualitas tinggi.

Terinspirasi dari [Qwen Code](https://github.com/QwenLM/qwen-code) Skill System.

## 🎯 Built-in Skills

### 1. **Review** (`/skill review`)
Review code untuk correctness, security, code quality, dan performance.

**Features:**
- Multi-dimensional review (4 dimensions)
- Security vulnerability detection
- Performance bottleneck identification
- Code quality assessment
- Actionable findings dengan severity levels

**Usage:**
```bash
# Review file spesifik
/skill review src/orchestrator.py

# Review git diff (uncommitted changes)
/skill review
```

**Output:**
- 🔴 Critical issues (must fix)
- 🟡 Suggestions (recommended)
- 🔵 Nice to have (optional)

---

### 2. **Explain** (`/skill explain`)
Jelaskan kode, arsitektur, atau konsep teknis dengan detail.

**Features:**
- High-level overview → detailed explanation
- Component relationships mapping
- Usage examples
- Common pitfalls

**Usage:**
```bash
# Explain file
/skill explain src/core/orchestrator.py

# Explain concept
/skill explain dependency injection
```

---

### 3. **Test** (`/skill test`)
Generate comprehensive unit tests untuk code.

**Features:**
- Happy path tests
- Edge cases coverage
- Error handling tests
- Mock external dependencies
- Follow project testing conventions

**Usage:**
```bash
# Generate tests for file
/skill test src/utils/parser.py
```

**Output:**
- Complete test file
- Instructions untuk run tests
- Coverage summary

---

### 4. **Refactor** (`/skill refactor`)
Refactor code untuk improve quality tanpa mengubah behavior.

**Features:**
- Code smell detection
- Refactoring suggestions
- Before/after comparison
- Validation steps

**Usage:**
```bash
# Refactor file
/skill refactor src/legacy_module.py

# Specific refactoring
/skill refactor extract long methods
```

---

## 🛠️ Command Reference

### Basic Commands

| Command | Description |
|---------|-------------|
| `/skill` | List semua available skills |
| `/skill list` | List semua skills (alias) |
| `/skill <name>` | Execute skill dengan prompt |
| `/skill <name> <target>` | Execute skill dengan target spesifik |

### Examples

```bash
# List semua skills
/skill

# Review file
/skill review main.py

# Explain concept
/skill explain async/await

# Generate tests
/skill test utils.py

# Refactor code
/skill refactor legacy.py
```

---

## 📝 Membuat Custom Skills

### Format File

Skill didefinisikan dalam file Markdown dengan YAML frontmatter:

```markdown
---
name: my_custom_skill
description: Deskripsi singkat skill
category: custom
allowedTools:
  - shell
  - file_read
  - grep_search
auto_execute: false
---

# Skill Instructions

## Step 1: Gather Information
Jelaskan langkah pertama...

## Step 2: Analysis
Jelaskan langkah kedua...

## Step 3: Output
Format output yang diharapkan...

## Examples
```bash
/skill my_custom_skill target
```
```

### YAML Frontmatter Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Unique identifier untuk skill |
| `description` | string | ✅ | Brief description |
| `category` | string | ❌ | Grouping (default: "general") |
| `allowedTools` | list | ❌ | Tools yang bisa digunakan |
| `auto_execute` | boolean | ❌ | Skip confirmation (default: false) |

### Lokasi Skills

- **Built-in skills**: `src/skills/`
- **Custom skills**: `.codearon/skills/` (project-specific)
- **User skills**: `~/.codearon/skills/` (global)

---

## 🏗️ Architecture

```
src/core/skill_manager.py    - Load & manage skills
src/core/skill_executor.py   - Execute skills
src/skills/                  - Skill definitions
    ├── review.md
    ├── explain.md
    ├── test.md
    └── refactor.md
```

### Components

#### 1. SkillManager
- Load skills dari directory
- Parse YAML frontmatter
- Index by category
- Singleton pattern

#### 2. SkillExecutor
- Execute skills dengan multi-agent pattern
- Progress tracking
- Cancellation support
- Async execution

#### 3. SkillDefinition
- Dataclass untuk skill metadata
- YAML parser
- Step extraction

---

## 🔌 Integration

### With Orchestrator

Skill system terintegrasi dengan orchestrator via:
- `/skill` command handler
- Auto-completion untuk skill names
- Progress indicator saat execution
- Result formatting dengan Rich panels

### With Tools

Skills menggunakan tools yang ada:
- `shell` - Execute system commands
- `file_read` - Baca file content
- `file_write` - Tulis file content
- `grep_search` - Cari pattern
- `glob` - List files by pattern
- `validator` - Validate code changes

---

## 🧪 Testing

```bash
# Run skill system tests
python -m unittest tests.test_skill_system -v

# Test specific component
python -m unittest tests.test_skill_system.TestSkillManager -v
```

### Test Coverage

- ✅ Skill loading & parsing
- ✅ YAML frontmatter validation
- ✅ Skill execution
- ✅ Error handling
- ✅ Singleton pattern
- ✅ Category filtering

---

## 🚀 Best Practices

### Untuk Skill Creators

1. **Keep it focused**: Satu skill = satu responsibility
2. **Clear instructions**: Step-by-step yang jelas
3. **Define allowed tools**: Minimal permissions principle
4. **Add examples**: Bantu user understand usage
5. **Test thoroughly**: Pastikan skill bekerja dengan benar

### Untuk Skill Users

1. **Review before execute**: Check `allowedTools` dan `auto_execute`
2. **Provide context**: Semakin spesifik target, semakin baik hasil
3. **Iterate**: Gunakan feedback untuk refine results
4. **Share**: Contribute custom skills ke community

---

## 📈 Future Enhancements

- [ ] Custom skills dari user (`.codearon/skills/`)
- [ ] Skill marketplace/community sharing
- [ ] Skill composition (chain multiple skills)
- [ ] Skill learning from feedback
- [ ] Parallel skill execution
- [ ] Skill profiling & optimization

---

## 🙏 Acknowledgments

Skill System ini terinspirasi dari:
- [Qwen Code Skills](https://github.com/QwenLM/qwen-code)
- [Claude Code Skills](https://www.anthropic.com/claude-code)

---

## 📖 Related Documentation

- [CodeAron README](../README.md)
- [Configuration Guide](../docs/CONFIGURATION.md)
- [Tools Reference](../docs/TOOLS.md)
