import threading
from typing import Dict, Any
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from src.prompt import PromptTemplates
from src.memory import ModelLRUStore


class ModelEngine:
    """
    ModelEngine
    ------------
    A lightweight inference engine that uses small local models
    (no online API dependencies) to generate README or text sections.

    Integrates with ModelLRUStore for memory-efficient model caching.
    """

    def __init__(self, model_id: str = "microsoft/phi-2", device: str = "cpu", max_models: int = 2):
        self.model_id = model_id
        self.device = device
        self.store = ModelLRUStore(max_models=max_models)
        self.lock = threading.Lock()

    # ---------------- Internal Helpers ---------------- #

    def _load_model(self):
        """Load model + tokenizer, cached via ModelLRUStore"""
        cached_model = self.store.get(self.model_id)
        if cached_model:
            return cached_model

        tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        model = AutoModelForCausalLM.from_pretrained(self.model_id)
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            device_map="auto" if self.device != "cpu" else None
        )

        self.store.set(self.model_id, pipe)
        return pipe

    # ---------------- Public Interface ---------------- #

    def generate_text(self, prompt: str, max_length: int = 512) -> str:
        """
        Generates text using the loaded model.
        Thread-safe and uses cached model if available.
        """
        with self.lock:
            pipe = self._load_model()
            output = pipe(prompt, max_new_tokens=max_length, do_sample=True, temperature=0.7)
            return output[0]["generated_text"].strip()

    def generate_readme(self, project_data: Dict[str, Any], base_path: str = ".") -> str:
        """
        Builds a full README file using the PromptTemplates class.
        Each section is generated sequentially using the model.
        """
        tmpl = PromptTemplates(project_data, base_path=base_path)
        prompts = tmpl.all_prompts()

        readme_sections = []
        readme_sections.append(f"# {tmpl.project_name}\n")

        for section_name, prompt in prompts.items():
            text = self.generate_text(prompt, max_length=400)
            readme_sections.append(f"\n## {section_name.capitalize()}\n{text}\n")

        return "\n".join(readme_sections)

    def list_loaded_models(self):
        """Return all currently loaded models in memory"""
        return self.store.list_loaded()


