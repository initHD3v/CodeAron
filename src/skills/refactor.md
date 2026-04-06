---
name: refactor
description: Refactor code untuk improve quality tanpa mengubah behavior
category: improvement
allowedTools:
  - shell
  - file_read
  - grep_search
  - file_write
  - validator
auto_execute: false
---

# Refactor Skill

Skill ini melakukan refactoring code untuk improve quality tanpa mengubah external behavior.

## Step 1: Analyze Current Code

1. **Baca code** dengan `file_read`
2. **Identifikasi code smells**:
   - Long methods (> 50 lines)
   - Large classes (> 500 lines)
   - Duplicate code
   - Long parameter lists (> 5 params)
   - Deep nesting (> 4 levels)
   - Magic numbers/strings
   - Poor naming (single letter, vague names)

3. **Cari dependencies**:
   - Functions/classes yang memanggil code ini
   - Dependencies external

## Step 2: Identify Refactoring Opportunities

### Common Refactorings:

| Code Smell | Refactoring |
|------------|-------------|
| Long Method | Extract Method |
| Large Class | Extract Class |
| Duplicate Code | Extract Method/Class |
| Long Parameter List | Introduce Parameter Object |
| Deep Nesting | Guard Clauses, Extract Method |
| Magic Numbers | Named Constants |
| Poor Naming | Rename |
| Switch Statements | Polymorphism/Strategy Pattern |
| Feature Envy | Move Method |
| Data Clumps | Extract Class |

## Step 3: Plan Refactoring

Untuk setiap refactoring:

1. **Define goal**: Apa yang ingin dicapai?
2. **Identify risks**: Apa yang bisa break?
3. **Plan tests**: Tests apa yang perlu di-run untuk verify?
4. **Incremental steps**: Break into small, safe steps

## Step 4: Execute Refactoring

### Extract Method Example:

**Before:**
```python
def process_order(order):
    # ... 50 lines of code ...
    # Calculate tax
    tax_rate = 0.1
    tax = order.amount * tax_rate
    # ... more code ...
```

**After:**
```python
def process_order(order):
    # ... code ...
    tax = calculate_tax(order.amount)
    # ... more code ...

def calculate_tax(amount: float) -> float:
    """Calculate tax based on amount."""
    tax_rate = 0.1
    return amount * tax_rate
```

### Rename Example:

**Before:**
```python
def calc(a, b):
    return a * b + (a * b * 0.1)
```

**After:**
```python
def calculate_total_with_tax(price: float, quantity: float) -> float:
    """Calculate total price including 10% tax."""
    subtotal = price * quantity
    tax = subtotal * 0.1
    return subtotal + tax
```

## Step 5: Validate Changes

1. **Run existing tests** - Pastikan tidak ada regression
2. **Run validator** - Check syntax dan type errors
3. **Manual verification** - Compare behavior before/after

## Step 6: Document Changes

Buat summary:
- **What changed**: List refactorings yang dilakukan
- **Why**: Alasan untuk setiap change
- **Benefits**: Improvement yang didapat (readability, maintainability, dll)

## Guidelines

- **Small steps**: Refactor incrementally, bukan big-bang
- **Tests first**: Pastikan ada tests sebelum refactor
- **One thing at a time**: Jangan mix refactoring dengan feature work
- **Preserve behavior**: External behavior harus tetap sama
- **Commit often**: Commit setiap successful refactoring step

## Examples

```
/refactor src/utils.py
```

```
/refactor extract methods yang terlalu panjang di orchestrator.py
```

```
/refactor rename variable yang tidak jelas di parser.py
```

## Output Format

Berikan:
1. **Diff** dari perubahan
2. **Explanation** untuk setiap refactoring
3. **Before/After** comparison
4. **Verification steps** yang sudah dilakukan
