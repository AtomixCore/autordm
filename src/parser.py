import os
import ast
from typing import Dict, List, Any


class ProjectParser:
    """Parses a Python project directory to extract information about its structure."""
    def __init__(self, project_path: str = ".") -> None:
        self.project_path = project_path
        self.files_data: Dict[str, Any] = {}
        self.excluded_dirs = {
            "__pycache__", ".git", ".venv", "env", "venv", "build",
            "dist", "node_modules", ".idea", ".vscode", ".mypy_cache"
        }

    def parse_project(self) -> None:
        """Parse all Python files in the project directory"""
        for root, dirs, files in os.walk(self.project_path):
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]

            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    self.files_data[file_path] = self._parse_file(file_path)

    def _parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a single Python file to extract classes and functions"""
        with open(file_path, "r", encoding="utf-8") as f:
            file_content = f.read()

        tree = ast.parse(file_content)
        functions = []
        classes = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                doc = ast.get_docstring(node) or ""
                functions.append({"name": node.name, "doc": doc.strip()})
            elif isinstance(node, ast.ClassDef):
                doc = ast.get_docstring(node) or ""
                classes.append({"name": node.name, "doc": doc.strip()})

        return {"functions": functions, "classes": classes}

    def summary(self) -> str:
        """Generate a summary of the parsed project structure"""
        summary_lines = []
        for file_path, data in self.files_data.items():
            summary_lines.append(f"\nFile: {file_path}")
            summary_lines.append(f"  Classes:")
            if data["classes"]:
                for c in data["classes"]:
                    summary_lines.append(f"    - {c['name']}: {c['doc'][:60] or 'No docstring'}")
            else:
                summary_lines.append("    None")

            summary_lines.append(f"  Functions:")
            if data["functions"]:
                for f in data["functions"]:
                    summary_lines.append(f"    - {f['name']}: {f['doc'][:60] or 'No docstring'}")
            else:
                summary_lines.append("    None")

        return "\n".join(summary_lines)
