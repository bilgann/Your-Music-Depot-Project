import os
import sys

# Ensure the project root (parent of backend/) is on sys.path so that
# `from backend import ...` works when this file is run directly.
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from dotenv import load_dotenv

# Load .env before build_app() so env vars are always available,
# regardless of how the Flask reloader re-spawns this module.
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from backend import build_app

app = build_app()

if __name__ == '__main__':
    app.run(
        debug=True,
        # Exclude site-packages from the reloader to prevent third-party
        # package writes (e.g. pip, postgrest) from triggering spurious reloads.
        exclude_patterns=["**/site-packages/**"],
    )
