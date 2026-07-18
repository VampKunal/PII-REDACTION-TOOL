import os
import psutil

def print_memory(label):
    process = psutil.Process(os.getpid())
    print(f"{label}: {process.memory_info().rss / 1024 / 1024:.2f} MB")

print_memory("Start")

import spacy
print_memory("After importing spacy")

nlp = spacy.load("en_core_web_sm")
print_memory("After loading spacy en_core_web_sm")

from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
print_memory("After importing presidio")

configuration = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
}
provider = NlpEngineProvider(nlp_configuration=configuration)
nlp_engine = provider.create_engine()
print_memory("After creating nlp_engine")

analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
print_memory("After creating AnalyzerEngine")
