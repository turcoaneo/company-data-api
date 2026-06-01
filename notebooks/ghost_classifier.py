# notebooks/ghost_classifier.py

import json
import math

from app.utils.path_util import get_project_root

# -------------------------------------------------
# Load exported weights (bias + per-feature weights)
# -------------------------------------------------

with open(get_project_root() / "notebooks/ghost_classifier_weights.json", "r", encoding="utf-8") as f:
    MODEL = json.load(f)

BIAS = float(MODEL["bias"])
WEIGHTS = MODEL["weights"]          # dict: feature_name -> weight
FEATURE_ORDER = MODEL["feature_order"]  # list: correct order for inference


# -------------------------------------------------
# Sigmoid
# -------------------------------------------------

def sigmoid(z: float) -> float:
    return 1.0 / (1.0 + math.exp(-z))


# -------------------------------------------------
# Score a feature vector (list or numpy array)
# -------------------------------------------------

def score_features(feature_vector) -> float:
    """
    feature_vector: list/array of floats in FEATURE_ORDER order
    returns: raw linear score z = w·x + b
    """
    z = BIAS
    for value, feature_name in zip(feature_vector, FEATURE_ORDER):
        z += WEIGHTS.get(feature_name, 0.0) * float(value)
    return z


# -------------------------------------------------
# Probability of being a ghost domain
# -------------------------------------------------

def ghost_probability(feature_vector) -> float:
    """
    Returns sigmoid(score)
    """
    return sigmoid(score_features(feature_vector))


# -------------------------------------------------
# Final classifier
# -------------------------------------------------

def is_ghost_features(feature_vector, threshold: float = 0.5) -> float:
    """
    Returns True/False based on threshold.
    """
    return ghost_probability(feature_vector) > threshold
