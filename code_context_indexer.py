import re
from pathlib import Path
from typing import Dict, List

from utils import read_text_file


class CodeContextIndexer:
    """
    Builds a searchable index from the developer's code context.

    Research purpose:
    This module supports context orchestration by breaking a program body into
    structured code blocks. Instead of sending the full codebase, later modules
    can select only relevant blocks from this index.
    """

    def build_index(self, codebase_folder: Path) -> Dict:
        indexed_files = []
        total_lines = 0
        total_blocks = 0

        for file_path in sorted(codebase_folder.iterdir()):
            if file_path.is_file() and file_path.suffix.lower() in [".js", ".py", ".java", ".ts"]:
                file_index = self._index_file(file_path)
                indexed_files.append(file_index)
                total_lines += file_index["line_count"]
                total_blocks += len(file_index["code_blocks"])

        return {
            "indexing_status": "success",
            "total_files_indexed": len(indexed_files),
            "total_code_lines": total_lines,
            "total_code_blocks": total_blocks,
            "indexed_files": indexed_files
        }

    def _index_file(self, file_path: Path) -> Dict:
        content = read_text_file(file_path)
        lines = content.splitlines()

        code_blocks = self._extract_javascript_style_blocks(
            file_name=file_path.name,
            lines=lines
        )

        return {
            "file_name": file_path.name,
            "file_extension": file_path.suffix.lower(),
            "line_count": len(lines),
            "code_blocks": code_blocks
        }

    def _extract_javascript_style_blocks(self, file_name: str, lines: List[str]) -> List[Dict]:
        """
        Extracts function-level blocks from JavaScript-like files.

        PP1 note:
        The prototype uses a practical function-block extractor for demonstration.
        The full version can expand this into AST-based parsing.
        """
        blocks = []
        current_block = []
        current_name = None
        start_line = 0
        brace_balance = 0
        inside_function = False

        function_pattern = re.compile(
            r"^\s*(async\s+)?function\s+([a-zA-Z0-9_]+)\s*\("
        )

        for index, line in enumerate(lines, start=1):
            match = function_pattern.match(line)

            if match and not inside_function:
                inside_function = True
                current_name = match.group(2)
                start_line = index
                current_block = [line]
                brace_balance = line.count("{") - line.count("}")

                if brace_balance == 0 and "{" in line:
                    blocks.append(
                        self._create_block(file_name, current_name, start_line, index, current_block)
                    )
                    inside_function = False
                    current_block = []
                    current_name = None

                continue

            if inside_function:
                current_block.append(line)
                brace_balance += line.count("{") - line.count("}")

                if brace_balance == 0:
                    blocks.append(
                        self._create_block(file_name, current_name, start_line, index, current_block)
                    )
                    inside_function = False
                    current_block = []
                    current_name = None

        return blocks

    def _create_block(
        self,
        file_name: str,
        block_name: str,
        start_line: int,
        end_line: int,
        block_lines: List[str]
    ) -> Dict:
        content = "\n".join(block_lines)

        called_functions = self._extract_called_functions(content)

        return {
            "block_id": f"{file_name}:{block_name}:{start_line}-{end_line}",
            "file_name": file_name,
            "block_type": "function",
            "block_name": block_name,
            "start_line": start_line,
            "end_line": end_line,
            "line_count": end_line - start_line + 1,
            "content": content,
            "tokens": self._extract_code_tokens(content),
            "called_functions": called_functions
        }

    def _extract_code_tokens(self, content: str) -> List[str]:
        tokens = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]*", content)
        cleaned = []

        ignore_words = {
            "function", "async", "await", "return", "const", "let", "var", "if",
            "else", "true", "false", "null", "then", "catch", "new", "throw",
            "Error", "console", "log", "json", "fetch"
        }

        for token in tokens:
            token_lower = token.lower()
            if token_lower not in ignore_words and token_lower not in cleaned:
                cleaned.append(token_lower)

        return cleaned

    def _extract_called_functions(self, content: str) -> List[str]:
        possible_calls = re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", content)

        ignore_calls = {
            "function", "if", "for", "while", "switch", "catch", "then",
            "json", "stringify", "tolowercase", "includes", "filter"
        }

        calls = []

        for call in possible_calls:
            call_lower = call.lower()
            if call_lower not in ignore_calls and call not in calls:
                calls.append(call)

        return calls