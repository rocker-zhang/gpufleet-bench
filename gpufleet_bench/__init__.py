"""gpufleet-bench: public benchmark harness + question-only cases.

This package contains NO answer key. Ground-truth labels live in the CLOSED
eval-corpus repo and are pulled at a fixed tag by the closed benchmark-gate
pipeline. The harness here loads question-only cases, calls a pluggable solver
endpoint, and (given a separately-supplied answer key) computes the release
metrics.
"""

__version__ = "0.1.0"
