from src.parser import ProjectParser
from src.feature_extractor import FeatureExtractor
from src.prompt import PromptTemplates
import json

parser = ProjectParser()
parser.parse_project()

extractor = FeatureExtractor(parser.files_data, start_point="./autordm.py")
features = extractor.extract()

prompts = PromptTemplates(features)
overview = prompts.all_prompts()
print()