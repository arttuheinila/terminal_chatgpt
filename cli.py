"""Parse command-line options used for one-shot piped requests."""
import argparse

def parse_args(argv:  list[str] | None = None) -> argparse.Namespace:
    """Return a mode selection and optional instruction from CLI arguments."""

    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group()

    modes.add_argument("--mode")
    modes.add_argument("--debug", action="store_const", const="debug", dest="mode")
    modes.add_argument("--review", action="store_const", const="review", dest="mode")
    modes.add_argument("--brief", action="store_const", const="brief", dest="mode")
    modes.add_argument("--rewrite", action="store_const", const="rewrite", dest="mode")

    parser.add_argument("question", nargs="*", help="Optional instruction for the input")
    return parser.parse_args(argv)
