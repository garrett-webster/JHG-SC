import numpy as np

def fastchoices(options, weights=None, size=1):
    if weights is None:
        weights = np.ones(len(options))
    cumulative_weights = np.cumsum(weights)
    count = np.prod(size)
    vals = np.random.uniform(0.0, np.sum(weights), size=count)
    result = np.asarray(options)[
        np.argmax((vals < cumulative_weights[:, np.newaxis]).T, axis=1)
    ]
    return result.reshape(size)[0] if size == 1 else result.reshape(size)