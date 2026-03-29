import os
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
