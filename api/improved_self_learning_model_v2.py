"""
Forwarder module for backward compatibility.
The canonical implementation resides in `models/improved_self_learning_model_v2.py`.
"""

import sys
from pathlib import Path

# Add project root to sys.path if not present
project_root = str(Path(__file__).resolve().parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from models.improved_self_learning_model_v2 import *
    from models.improved_self_learning_model_v2 import ImprovedSelfLearningModelV2
except ImportError:
    from improved_self_learning_model_v2 import *  # type: ignore
    from improved_self_learning_model_v2 import ImprovedSelfLearningModelV2  # type: ignore
