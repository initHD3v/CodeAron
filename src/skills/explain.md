---
name: explain
description: Jelaskan kode, arsitektur, atau konsep teknis dengan detail
category: understanding
allowedTools:
  - shell
  - file_read
  - grep_search
  - glob
auto_execute: true
---

# Explain Skill

Skill ini menjelaskan kode atau konsep teknis dengan cara yang mudah dipahami.

## Step 1: Pahami Request User

Identifikasi apa yang ingin dijelaskan:

- **File spesifik**: "Jelaskan file ini"
- **Function/Class**: "Bagaimana cara kerja function X?"
- **Arsitektur**: "Jelaskan struktur project ini"
- **Konsep**: "Apa itu dependency injection?"
- **Code snippet**: "Jelaskan kode ini"

## Step 2: Kumpulkan Konteks

### Untuk File/Code:
1. Baca file dengan `file_read`
2. Cari dependencies dengan `grep_search`
3. Lihat struktur folder dengan `shell: ls -la`

### Untuk Arsitektur:
1. Scan semua source files dengan `glob`
2. Identifikasi main entry points
3. Mapping dependencies antar modules
4. Lihat config files (package.json, setup.py, dll)

### Untuk Konsep:
1. Cari implementasi di codebase dengan `grep_search`
2. Lihat dokumentasi jika ada
3. Identifikasi use cases

## Step 3: Struktur Penjelasan

Berikan penjelasan dengan struktur:

### 1. Overview (Elevator Pitch)
1-2 kalimat yang menjelaskan "apa ini" dan "kenapa ada"

### 2. Purpose & Responsibility
- Apa tanggung jawab utama?
- Masalah apa yang diselesaikan?
- Kenapa pendekatan ini dipilih?

### 3. How It Works (Step by Step)
Jelaskan flow/alur dengan step-by-step:
```
Input → Process A → Process B → Output
```

### 4. Key Components
List komponen penting dan peran masing-masing:
- **Component A**: Bertugas untuk...
- **Component B**: Menangani...

### 5. Dependencies & Relationships
- Depends on: Module X, Y
- Used by: Module Z
- Integrates with: External service W

### 6. Examples
Berikan contoh usage jika applicable:
```python
# Example code
```

### 7. Common Pitfalls
- Hal yang sering salah
- Best practices untuk avoid issues

## Guidelines

- **Start simple**: Mulai dari high-level, baru detail
- **Use analogies**: Analogi membantu pemahaman
- **Show, don't just tell**: Sertakan code examples
- **Highlight patterns**: Tunjukkan design patterns yang digunakan
- **Connect to big picture**: Jelaskan bagaimana ini fit ke overall system

## Examples

```
/explain src/core/orchestrator.py
```

```
/explain bagaimana cara kerja TaskPlanner?
```

```
/explain arsitektur project ini
```
