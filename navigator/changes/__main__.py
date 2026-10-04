import sys

from lookup.cli import main

raise SystemExit(main(["changes"] + sys.argv[1:]))
