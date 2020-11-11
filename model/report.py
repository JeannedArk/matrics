# -*- coding: utf-8 -*-
import numpy as np
from dataclasses import dataclass


@dataclass
class Report:
    accuracy: float
    hamming_score: float
    sklearn_report: str
    confusion_matrix: np.ndarray
