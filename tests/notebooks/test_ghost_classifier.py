# test_ghost_classifier.py

import math

from notebooks.ghost_classifier import (
    score_features,
    ghost_probability,
    is_ghost_features,
    FEATURE_ORDER,
    WEIGHTS,
    BIAS,
)


class TestGhostClassifier:

    def test_sigmoid_range(self):
        assert 0 < ghost_probability([0] * len(FEATURE_ORDER)) < 1

    def test_score_features_linear(self):
        # Build a simple vector with 1s everywhere
        vec = [1.0] * len(FEATURE_ORDER)
        z = score_features(vec)

        # Manual check: bias + sum(weights)
        manual = BIAS + sum(WEIGHTS[f] for f in FEATURE_ORDER)
        assert math.isclose(z, manual, rel_tol=1e-6)

    def test_probability_valid_range(self):
        # Probability must always be between 0 and 1
        low = ghost_probability([0] * len(FEATURE_ORDER))
        high = ghost_probability([10] * len(FEATURE_ORDER))
        assert 0 <= low <= 1
        assert 0 <= high <= 1

    def test_is_ghost_threshold(self):
        # If probability > threshold → ghost
        vec = [0] * len(FEATURE_ORDER)
        prob = ghost_probability(vec)
        assert is_ghost_features(vec, threshold=prob - 0.01) is True
        assert is_ghost_features(vec, threshold=prob + 0.01) is False

    def test_feature_order_length(self):
        assert len(FEATURE_ORDER) == len(WEIGHTS)
