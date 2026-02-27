import os
import re
import gc
import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.memory.models import CodeSymbol, save_symbol, init_db
from src.memory.vector_store import VectorStore
from src.core.config import settings
from rich.console import Console
from rich.live import Live
from rich.text import Text

console = Console()
logger = logging.getLogger("Indexer")

class ProjectIndexer:
    def __init__(self, project_path: str, vector_store: Optional[VectorStore] = None):
        self.project_path = Path(project_path)
        init_db()
        self.vector_store = vector_store or VectorStore()
        self.parsers = {}
        self.languages = {}
        self._init_treesitter()

    def _init_treesitter(self):
        """Mencoba memuat parser tree-sitter secara aman dengan timeout."""
        try:
            console.print("[dim]  Loading parsers...[/dim]")
            import tree_sitter_languages
            from tree_sitter import Parser

            supported = list(settings.SUPPORTED_EXTENSIONS.items())
            for idx, (ext, lang_name) in enumerate(supported, 1):
                if lang_name not in self.languages:
                    try:
                        language = tree_sitter_languages.get_language(lang_name)
                        self.languages[lang_name] = language
                        parser = Parser()
                        try:
                            parser.language = language
                        except AttributeError:
                            parser.set_language(language)
                        self.parsers[lang_name] = parser
                        console.print(f"[dim]    ✓ {lang_name}[/dim]")
                    except Exception as e:
                        logger.debug(f"Parser for {lang_name} not loaded: {e}")
                        console.print(f"[dim]    ✗ {lang_name} (skip)[/dim]")
            console.print("[bold green]  ✓ Parsers ready[/bold green]\n")
        except Exception as e:
            logger.warning(f"Tree-sitter initialization failed: {e}. Falling back to Regex.")
            console.print("[yellow]  ⚠ Tree-sitter failed, using regex fallback[/yellow]\n")

    def scan_project(self):
        """Memindai proyek dengan progress tracking."""
        start_time = time.time()
        console.print("[bold yellow]🧹 Cleaning old semantic memory...[/bold yellow]")
        self.vector_store.clear_all()

        console.print(f"\n[bold cyan]🔍 Indexing project:[/bold cyan] [dim]{self.project_path}[/dim]\n")

        count = 0
        file_count = 0
        batch_symbols = []
        errors = 0
        
        # Collect all files first for progress tracking
        files_to_index = []
        for root, dirs, files in os.walk(self.project_path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in settings.IGNORED_DIRS and not d.startswith('.')]
            for file in files:
                ext = os.path.splitext(file)[1]
                if ext in settings.SUPPORTED_EXTENSIONS:
                    file_path = os.path.join(root, file)
                    files_to_index.append((file_path, ext))
        
        total_files = len(files_to_index)
        console.print(f"[dim]  Found {total_files} files to index...[/dim]\n")
        
        # Index with progress
        for idx, (file_path, ext) in enumerate(files_to_index, 1):
            try:
                # Progress update every 10 files
                if idx % 10 == 0 or idx == total_files:
                    elapsed = time.time() - start_time
                    rate = idx / elapsed if elapsed > 0 else 0
                    console.print(f"[dim]  Progress: {idx}/{total_files} files ({rate:.1f} files/sec)[/dim]")
                
                found_symbols = self._index_file_to_list(file_path, ext)
                if found_symbols:
                    count += len(found_symbols)
                    batch_symbols.extend(found_symbols)

                    if len(batch_symbols) >= 20:
                        self.vector_store.add_symbols(batch_symbols)
                        batch_symbols = []
                file_count += 1
            except Exception as e:
                errors += 1
                logger.error(f"Error indexing {file_path}: {e}")
                if errors > 5:
                    console.print(f"[yellow]  ⚠ Too many errors, skipping remaining files[/yellow]")
                    break

        if batch_symbols:
            self.vector_store.add_symbols(batch_symbols)

        elapsed = time.time() - start_time
        gc.collect()
        
        status_color = "bold green" if errors == 0 else "bold yellow"
        console.print(f"\n[{status_color}]✅ Success![/bold green]")
        console.print(f"  [dim]• Files processed:[/dim] {file_count}")
        console.print(f"  [dim]• Symbols indexed:[/dim] {count}")
        console.print(f"  [dim]• Errors:[/dim] {errors}")
        console.print(f"  [dim]• Time elapsed:[/dim] {elapsed:.1f}s")

    def _index_file_to_list(self, file_path: str, ext: str) -> List[Dict[str, Any]]:
        rel_path = os.path.relpath(file_path, self.project_path)
        lang_name = settings.SUPPORTED_EXTENSIONS.get(ext)
        found_symbols = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                source_code = f.read()

            if lang_name in self.parsers:
                found_symbols = self._parse_with_treesitter(source_code, rel_path, lang_name)
            else:
                found_symbols = self._parse_with_regex(source_code, rel_path, ext)

            # Backup to SQL
            for s in found_symbols:
                try:
                    save_symbol(CodeSymbol(**s))
                except Exception as e:
                    logger.error(f"SQL Save Error: {e}")
                
            return found_symbols
        except Exception as e:
            logger.error(f"Error indexing {rel_path}: {e}")
            return []

    def _parse_with_treesitter(self, source_code: str, rel_path: str, lang_name: str) -> List[Dict[str, Any]]:
        symbols = []
        try:
            parser = self.parsers[lang_name]
            tree = parser.parse(bytes(source_code, "utf8"))
            language = self.languages[lang_name]

            query_scm = """
                (class_definition name: (identifier) @name) @def
                (function_definition name: (identifier) @name) @def
                (class_declaration name: (identifier) @name) @def
                (function_declaration name: (identifier) @name) @def
                (method_declaration name: (identifier) @name) @def
            """
            
            query = language.query(query_scm)
            captures = query.captures(tree.root_node)
            
            for node, tag in captures:
                if tag == 'def':
                    name_node = node.child_by_field_name('name')
                    if not name_node: continue
                        
                    symbol_name = source_code[name_node.start_byte:name_node.end_byte]
                    content = source_code[node.start_byte:node.end_byte]
                    
                    symbols.append({
                        "name": symbol_name,
                        "type": "Definition",
                        "file_path": rel_path,
                        "line_start": node.start_point[0] + 1,
                        "line_end": node.end_point[0] + 1,
                        "signature": symbol_name, 
                        "content": content[:1500] 
                    })
            return symbols
        except Exception as e:
            logger.debug(f"Treesitter parse error for {rel_path}: {e}")
            return []

    def _parse_with_regex(self, source_code: str, rel_path: str, ext: str) -> List[Dict[str, Any]]:
        patterns = {
            '.dart': [r'(class|mixin|enum)\s+(\w+)', r'(\w+)\s+(\w+)\s*\(.*?\)\s*{'],
            '.py': [r'class\s+(\w+)', r'def\s+(\w+)'],
            '.js': [r'class\s+(\w+)', r'function\s+(\w+)', r'const\s+(\w+)\s*=\s*\(.*?\)\s*=>']
        }
        
        symbols = []
        file_patterns = patterns.get(ext, [r'class\s+(\w+)', r'def\s+(\w+)'])
        lines = source_code.splitlines()
        
        for i, line in enumerate(lines):
            for pattern in file_patterns:
                match = re.search(pattern, line)
                if match:
                    name = match.group(1) if len(match.groups()) == 1 else match.group(2)
                    symbols.append({
                        "name": name,
                        "type": "RegexDef",
                        "file_path": rel_path,
                        "line_start": i + 1,
                        "line_end": min(i + 15, len(lines)),
                        "signature": line.strip(),
                        "content": "\n".join(lines[i:i+15])
                    })
                    break 
        return symbols
