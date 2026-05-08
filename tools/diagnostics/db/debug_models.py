
import asyncio
import sys
from pathlib import Path

# Add src/py to sys.path
sys.path.append(str(Path(__file__).resolve().parents[3] / "src" / "py"))

import importlib
import pkgutil

from advanced_alchemy.base import metadata_registry


async def debug_metadata():
    import app.domain
    print(f"Searching for models in {app.domain.__path__}")

    # Discover and import all domain models
    for _, module_name, is_pkg in pkgutil.iter_modules(app.domain.__path__, "app.domain."):
        print(f"Checking module: {module_name}")
        try:
            mod = importlib.import_module(f"{module_name}.models")
            print(f"  Imported {module_name}.models")
        except ImportError as e:
            print(f"  Could not import {module_name}.models: {e}")

    print("\nMetadata registry contents:")
    for key, metadata in metadata_registry._metadata.items():
        print(f"\nMetadata '{key}':")
        print(f"  Tables: {list(metadata.tables.keys())}")

if __name__ == "__main__":
    asyncio.run(debug_metadata())
