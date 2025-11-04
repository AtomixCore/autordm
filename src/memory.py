import threading, sys, time, logging
from collections import OrderedDict
try:
    from pympler import asizeof
except ImportError: 
    asizeof = None


class ModelLRUStore:
    """
    Keeps loaded HuggingFace (or other) model instances alive in memory.
    Prevents repeated loading, with LRU eviction.
    """

    def __init__(self, max_models: int = 2):
        self.max_models = max_models
        self.models = OrderedDict()
        self.lock = threading.Lock()

    def get(self, model_id):
        """Retrieve a model instance from memory, updating its LRU status"""
        with self.lock:
            if model_id not in self.models:
                return None
            model = self.models.pop(model_id)
            self.models[model_id] = model
            return model

    def set(self, model_id, model):
        """Store a model instance in memory, evicting LRU if needed"""
        with self.lock:
            if model_id in self.models:
                self.models.pop(model_id)
            elif len(self.models) >= self.max_models:
                self.models.popitem(last=False)
            self.models[model_id] = model

    def list_loaded(self):
        """List currently loaded model IDs"""
        with self.lock:
            return list(self.models.keys())

    def unload(self, model_id):
        """Unload a specific model from memory"""
        with self.lock:
            if model_id in self.models:
                self.models.pop(model_id)