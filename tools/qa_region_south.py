#!/usr/bin/env python3
"""Nothing is broken from the Aspen down to Tanaris - tools/audit_region_south.py, in the sweep.

    PYTHONPATH=. python3 tools/qa_region_south.py

Kyle, 13 Nov 2026: "we need to still ensure subzones, quests, npcs, and everything are not broken."
The audit is the readable report; this is the same pass as a check that fails, so the next change
to any of the nineteen maps is held to it.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tools.audit_region_south import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
