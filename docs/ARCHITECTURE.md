# CodeAron System Architecture Blueprint

## 1. High-Level Architecture
Sistem beroperasi sebagai *Deterministic Finite Automaton* (DFA) yang diperkaya dengan LLM lokal.

```mermaid
graph TD
    User((User)) -->|CLI Command| IO_Layer[I/O & TUI (Rich)]
    IO_Layer --> Orchestrator[Orchestrator (State Machine)]

    subgraph "Core Logic"
        Orchestrator -->|Request| Planner[Planning Engine]
        Orchestrator -->|Context| ContextMgr[Context Manager & RAG]
        Orchestrator -->|Execute| Executor[Action Executor]
    end

    subgraph "Intelligence Layer (Offline)"
        Inference[Inference Engine (MLX)]
        Model[(Local LLM - Quantized)]
        Inference <--> Model
    end

    subgraph "Safety & Verification"
        GitGuard[Git Transaction Manager]
        DartAnalyzer[Static Analysis Wrapper]
        BuildVerify[Build Verification System]
    end
```

## 2. Tech Stack
- **Language:** Python 3.11+
- **AI Engine:** MLX & MLX-LM (Apple Silicon Native)
- **Models:** DeepSeek-Coder-V2-Lite (Coding), Moondream2/Llava (Vision)
- **Database:** SQLite (FTS5 for Symbol Indexing)
- **CLI Framework:** Typer + Rich
- **Parsing:** Tree-sitter-dart

## 3. Core Modules
1.  **Orchestrator:** Mengelola state (IDLE, PLANNING, CODING, VERIFYING, ROLLBACK).
2.  **Aron-Guard:** Mencegah kode rusak masuk ke production dengan `git stash` dan `dart analyze`.
3.  **Aron-Eyes:** Modul Vision untuk analisis UI.
4.  **Aron-Hub:** Manajemen model LLM (download/update/switch).

## 4. Safety Protocol
- **Atomic Transactions:** Setiap perubahan dibungkus dalam git checkpoint.
- **3-Retry Policy:** Maksimal 3 kali percobaan perbaikan mandiri sebelum menyerah.
- **Clean Arch Enforcer:** Validasi dependensi antar layer.
