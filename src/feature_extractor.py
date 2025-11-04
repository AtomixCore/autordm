import os
import re
import ast
from typing import Dict, Any, List


class FeatureExtractor:
    """
    Advanced feature extraction engine for AutoReadme.
    Extracts insights, dependencies, and main project traits.
    """

    def __init__(self, parsed_data: Dict[str, Any], start_point: str | None = None) -> None:
        self.parsed_data = parsed_data
        self.start_point = start_point
        self.features: Dict[str, Any] = {
            "project_type": "unknown",
            "main_features": [],
            "dependencies": [],
            "entry_points": [],
            "notable_classes": [],
            "notable_functions": [],
        }

    def extract(self) -> Dict[str, Any]:
        self._detect_project_type()
        self._extract_dependencies()
        self._extract_features_from_docstrings()
        self._extract_features_from_structure()
        self._find_entry_points()
        self._collect_notable_elements()
        return self.features

    # -----------------------
    # INTERNAL EXTRACTION LOGIC
    # -----------------------

    def _detect_project_type(self) -> None:
        """Guess the general type of project"""
        all_code = " ".join(self.parsed_data.keys()).lower()
        if "flask" in all_code or "fastapi" in all_code:
            self.features["project_type"] = "Web Application"
        elif "click" in all_code or "argparse" in all_code:
            self.features["project_type"] = "CLI Tool"
        elif any(lib in all_code for lib in ("torch", "tensorflow", "transformers", "sklearn")):
            self.features["project_type"] = "AI / ML Library"
        else:
            self.features["project_type"] = "Python Library"

    def _extract_dependencies(self) -> None:
        """Extract imported modules using AST for accuracy"""
        deps = set()
        for path in self.parsed_data.keys():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            deps.add(alias.name.split(".")[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            deps.add(node.module.split(".")[0])
            except Exception:
                continue
        self.features["dependencies"] = sorted(deps)

    def _extract_features_from_docstrings(self) -> None:
        """Analyze docstrings to extract meaningful keywords"""
        docs = []
        for file_data in self.parsed_data.values():
            for kind in ("functions", "classes"):
                for item in file_data.get(kind, []):
                    doc = item.get("doc", "")
                    if len(doc) > 10:
                        docs.append(doc.lower())

        keywords = {"api", "cli", "database", "network", "model", "parser", "training", "config", "utility"}
        found = [kw for kw in keywords if any(kw in d for d in docs)]
        self.features["main_features"].extend(found)

    def _extract_features_from_structure(self) -> None:
        """Add context-based features from filenames and class names"""
        file_names = " ".join(os.path.basename(p).lower() for p in self.parsed_data.keys())
        class_names = " ".join(
            c["name"].lower() for f in self.parsed_data.values() for c in f.get("classes", [])
        )

        structure_keywords = {
            "trainer": "training",
            "api": "api",
            "parser": "parser",
            "cli": "cli",
            "agent": "agent",
            "server": "web server",
            "database": "database",
            "utils": "utilities",
        }

        for key, feature in structure_keywords.items():
            if key in file_names or key in class_names:
                self.features["main_features"].append(feature)

        self.features["main_features"] = sorted(list(set(self.features["main_features"]))) or ["General utilities"]

    def _find_entry_points(self) -> None:
        """Find or infer main script / entry file"""
        if self.start_point:
            if os.path.exists(self.start_point):
                self.features["entry_points"].append(self.start_point)
                return
            else:
                # بحث ذكي بالاسم فقط
                for path in self.parsed_data.keys():
                    if os.path.basename(path) == self.start_point:
                        self.features["entry_points"].append(path)
                        return

        for path in self.parsed_data.keys():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                    if "if __name__" in content and "__main__" in content:
                        self.features["entry_points"].append(path)
                        return
            except Exception:
                pass

        for path, file_data in self.parsed_data.items():
            for f in file_data.get("functions", []):
                if f["name"].lower() == "main":
                    self.features["entry_points"].append(path)
                    return

    def _collect_notable_elements(self) -> None:
        """Collect the most meaningful classes/functions"""

        classes, functions = [], []
        for file_data in self.parsed_data.values():
            for c in file_data.get("classes", []):
                # Include only documented classes
                if c["doc"]:
                    classes.append(f"{c['name']}()")
            for f in file_data.get("functions", []):
                # Include only documented functions that do NOT start with '_'
                if f["doc"] and not f["name"].startswith("_"):
                    functions.append(f"{f['name']}()")

        self.features["notable_classes"] = sorted(list(set(classes)))[:5]
        self.features["notable_functions"] = sorted(list(set(functions)))[:5]
