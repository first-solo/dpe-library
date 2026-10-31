"""The one way anything writes to catalog/.

Catalog files carry `# verify this` annotations during backfill, and a
safe_load/safe_dump round-trip strips every one of them without a word, along
with reflowing block scalars and turning empty values into explicit nulls.
This module writes through ruamel.yaml in round-trip mode so that only the
fields being set change. dpelib stays on PyYAML; it only reads.

tests/test_apply_updates.py fails if that stops being true.
"""

from __future__ import annotations

from ruamel.yaml import YAML

import dpelib as L

# The settings are not cosmetic. Each was checked against the real catalog:
#   preserve_quotes  keeps '([0-9]{4}-[0-9]+)' quoted, since an unquoted regex
#                    starting with a YAML indicator would not survive.
#   indent(2, 2, 0)  matches what is on disk, so untouched list lines do not
#                    move. ruamel sets sequence indent globally at dump time
#                    rather than preserving it per file, so this has to agree
#                    with the repo's style.
#   width            defaults to 80, which wraps a long source_url onto a
#                    continuation line. Catalog URLs routinely exceed that.
_writer = YAML()
_writer.preserve_quotes = True
_writer.indent(mapping=2, sequence=2, offset=0)
_writer.width = 4096


def write_fields(doc_id: str, updates: dict) -> None:
    """Set `updates` in catalog/<doc_id>.yaml and leave every other byte alone.

    A dict value merges into an existing mapping rather than replacing it, so
    a comment sitting on a sibling key survives.
    """
    path = L.CATALOG / f"{doc_id}.yaml"
    with path.open() as fh:
        data = _writer.load(fh) or {}

    for k, v in updates.items():
        if isinstance(v, dict) and isinstance(data.get(k), dict):
            data[k].update(v)
        else:
            data[k] = v

    with path.open("w") as fh:
        _writer.dump(data, fh)
