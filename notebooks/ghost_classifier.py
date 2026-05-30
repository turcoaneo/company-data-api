# notebooks/ghost_classifier.py

import json
import re

# Load exported weights
with open("ghost_classifier_weights.json", "r", encoding="utf-8") as f:
    MODEL = json.load(f)

BIAS = MODEL["bias"]
WEIGHTS = MODEL["weights"]

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str):
    return TOKEN_RE.findall(text.lower())


def score_html(html: str) -> float:
    tokens = tokenize(html)
    return BIAS + sum(WEIGHTS.get(tok, 0.0) for tok in tokens)


def is_ghost(html: str, threshold: float = 0.0) -> bool:
    return score_html(html) > threshold
