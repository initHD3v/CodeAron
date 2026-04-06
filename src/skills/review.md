---
name: review
description: Review code changes untuk correctness, security, code quality, dan performance
category: code_analysis
allowedTools:
  - shell
  - file_read
  - grep_search
  - glob
auto_execute: false
---

# Code Review Skill

Skill ini melakukan code review komprehensif dari multiple dimensions.

## Step 1: Tentukan scope review

Berdasarkan input user:

- **File path**: Review file spesifik
  - Gunakan `file_read` untuk baca file
  - Gunakan `grep_search` untuk cari pattern terkait
  
- **Directory**: Review semua file dalam folder
  - Gunakan `glob` untuk list semua files
  - Prioritaskan file kode (.py, .js, .ts, .go, .rs, dll)

- **Git diff**: Review perubahan terbaru
  - Gunakan `git diff HEAD` untuk uncommitted changes
  - Gunakan `git diff --staged` untuk staged changes

## Step 2: Parallel Multi-Dimensional Review

Lakukan review dari 4 dimensi secara paralel:

### Dimension 1: Correctness & Security
- Logic errors dan edge cases
- Null/undefined handling
- Race conditions dan concurrency issues
- Security vulnerabilities (injection, XSS, SSRF, path traversal)
- Type safety issues
- Error handling gaps

### Dimension 2: Code Quality
- Code style consistency dengan surrounding code
- Naming conventions (variables, functions, classes)
- Code duplication dan opportunities for reuse
- Over-engineering atau unnecessary abstraction
- Missing atau misleading comments
- Dead code

### Dimension 3: Performance & Efficiency
- Performance bottlenecks (N+1 queries, unnecessary loops)
- Memory leaks atau excessive memory usage
- Unnecessary re-renders (untuk UI code)
- Inefficient algorithms atau data structures
- Missing caching opportunities

### Dimension 4: Business Logic & Design
- Business logic soundness
- Boundary interactions antara modules
- Implicit assumptions yang mungkin break
- Unexpected side effects atau hidden coupling
- Design pattern appropriateness

## Step 3: Present Findings

Format output dengan struktur:

### Summary
1-2 kalimat overview dari changes dan assessment.

### Findings
Gunakan severity levels:

- **🔴 Critical** - Must fix before merging. Bugs, security issues, data loss.
- **🟡 Suggestion** - Recommended improvement. Better patterns, potential issues.
- **🔵 Nice to have** - Optional optimization. Minor style tweaks.

Untuk setiap finding, include:

1. **File:line** (e.g., `src/foo.py:42`)
2. **What's wrong** - Clear description
3. **Why it matters** - Impact if not addressed
4. **Suggested fix** - Concrete code suggestion

### Verdict
Salah satu dari:

- **✅ Approve** - No critical issues, good to merge
- **❌ Request changes** - Has critical issues that need fixing
- **💬 Comment** - Has suggestions but no blockers

## Examples

```
/review src/orchestrator.py
```

```
/review
```
(Review uncommitted git changes)
