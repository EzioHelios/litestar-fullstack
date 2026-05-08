
import sys
from pathlib import Path

# Add src/py to sys.path
sys.path.append(str(Path(__file__).resolve().parents[3] / "src" / "py"))

from advanced_alchemy.base import metadata_registry

print("Inspecting Metadata Registry...")
# Use the public interface since _registry might be private or structured differently across versions
# but in the source we saw it's a dict-like object
for key in metadata_registry:
    metadata = metadata_registry.get(key)
    tables = list(metadata.tables.keys())
    print(f"Bind Key: '{key}' (type: {type(key)})")
    print(f"  Tables: {tables}")

# Also check orm_registry directly
from advanced_alchemy.base import orm_registry

print(f"\nORM Registry Metadata Tables: {list(orm_registry.metadata.tables.keys())}")
