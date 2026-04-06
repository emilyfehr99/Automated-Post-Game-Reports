import json
import os
import sys
import logging
logging.basicConfig(level=logging.INFO)

from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2

model = ImprovedSelfLearningModelV2()
model.recalculate_performance_from_scratch()
perf = model.get_model_performance()
print(f"Performance: {perf}")
