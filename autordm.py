from src.parser import ProjectParser
from src.feature_extractor import FeatureExtractor
from src.model_engine import ModelEngine
import json

parser = ProjectParser()
parser.parse_project()

extractor = FeatureExtractor(parser.files_data, start_point="./autordm.py")
features = extractor.extract()

model_engine = ModelEngine()
section = model_engine.generate_readme(features)

with open("readme-test.md", 'w') as _file:
    _file.write(section)