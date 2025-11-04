import os
import json
from typing import Dict, Any, List


class PromptTemplates:
    """
    Builds intelligent, ready-to-use prompts for the ModelEngine.
    Integrates extracted project data directly into well-structured templates.
    """

    def __init__(self, project_info: Dict[str, Any], base_path: str = "."):
        self.data = project_info
        self.base_path = os.path.abspath(base_path)
        self.project_name = os.path.basename(self.base_path)

        self.project_type = self.data.get("project_type", "Unknown Project")
        self.main_features = self.data.get("main_features", [])
        self.dependencies = self.data.get("dependencies", [])
        self.entry_points = self.data.get("entry_points", [])
        self.notable_classes = self.data.get("notable_classes", [])
        self.notable_functions = self.data.get("notable_functions", [])

    # ---------------- Core Methods ----------------

    def build_context_summary(self) -> str:
        """
        Builds a readable technical context from extracted data.
        Used as the base context for all prompts.
        """
        ctx = []
        ctx.append(f"Project Name: {self.project_name}")
        ctx.append(f"Project Type: {self.project_type}")
        ctx.append(f"Main Features: {', '.join(self.main_features)}")
        ctx.append(f"Entry Points: {', '.join(self.entry_points)}")
        ctx.append(f"Dependencies: {', '.join(self.dependencies)}")
        ctx.append(f"Notable Classes: {', '.join(self.notable_classes)}")
        ctx.append(f"Notable Functions: {', '.join(self.notable_functions)}")

        return "\n".join(ctx)

    # ---------------- Prompt Builders ----------------

    def readme_overview(self) -> str:
        """Prompt for generating a professional README Overview section."""
        return (
            "You are an AI README generator.\n"
            "Using the following project context, write a professional, concise README overview section.\n"
            "Focus on what the project does, its purpose, and how it's structured.\n\n"
            f"PROJECT CONTEXT:\n{self.build_context_summary()}\n\n"
            "README OVERVIEW:"
        )

    def readme_features(self) -> str:
        """Prompt for generating the Features section."""
        return (
            "Generate a 'Features' section for the README based on the following extracted project info.\n"
            "Use bullet points and highlight any interesting capabilities.\n\n"
            f"{self.build_context_summary()}\n\n"
            "FEATURES SECTION:"
        )

    def readme_installation(self) -> str:
        """Prompt for generating Installation instructions."""
        entry = self.entry_points[0] if self.entry_points else "main.py"
        return (
            "Generate a clear and friendly 'Installation' section for the README.\n"
            "Assume the user wants to install and run the project locally.\n\n"
            f"ENTRY POINT: {entry}\n"
            f"PROJECT NAME: {self.project_name}\n\n"
            "INSTALLATION SECTION:"
        )

    def readme_usage(self) -> str:
        """Prompt for generating Usage examples."""
        entry = self.entry_points[0] if self.entry_points else "main.py"
        return (
            "Create a 'Usage' section for the README showing how to run or import the project.\n"
            "If it's a CLI, show how to execute it from the terminal.\n"
            "If it's a Python library, show how to import and use the main class or function.\n\n"
            f"ENTRY POINT: {entry}\n"
            f"PROJECT NAME: {self.project_name}\n"
            f"CLASSES: {', '.join(self.notable_classes)}\n"
            f"FUNCTIONS: {', '.join(self.notable_functions)}\n\n"
            "USAGE SECTION:"
        )

    def readme_license(self) -> str:
        """Prompt for generating License text."""
        return (
            "Generate a short 'License' section for a Python open-source project.\n"
            "Default to MIT if no specific license is found.\n\n"
            f"PROJECT NAME: {self.project_name}\n\n"
            "LICENSE SECTION:"
        )

    def readme_summary_prompt(self) -> str:
        """Prompt for a summarized project description (short paragraph)."""
        return (
            "Summarize the project based on the extracted information below.\n"
            "Be short, clear, and accurate.\n\n"
            f"{self.build_context_summary()}\n\n"
            "SUMMARY:"
        )

    # ---------------- Utility ----------------

    def all_prompts(self) -> Dict[str, str]:
        """Return all generated prompts as a dictionary."""
        return {
            "overview": self.readme_overview(),
            "features": self.readme_features(),
            "installation": self.readme_installation(),
            "usage": self.readme_usage(),
            "license": self.readme_license(),
            "summary": self.readme_summary_prompt(),
        }

    def export_prompts_json(self) -> str:
        """Export all prompts as JSON (for debugging or external use)."""
        return json.dumps(self.all_prompts(), indent=2)