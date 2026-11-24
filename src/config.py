# Shared settings so results repeat.
import random

import numpy as np

SEED = 42


def set_seeds(seed=SEED):
    random.seed(seed)
    np.random.seed(seed)