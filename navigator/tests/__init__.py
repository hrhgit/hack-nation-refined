"""Standard-library discovery for python3 -m unittest."""

import sys
from pathlib import Path

# Existing tests import neighboring fixtures by their top-level module names.
# Preserve that convention both for default discovery and discovery with -s tests.
sys.path.insert(0, str(Path(__file__).resolve().parent))
