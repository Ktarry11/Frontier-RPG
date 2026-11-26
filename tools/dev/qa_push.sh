#!/bin/bash
# Run the full QA gate (tools/qa_quest_overhaul.py) and push to origin/main ONLY if it passes.
# Standing rule: push only after QA is green; never edit tracked files while this runs.
cd "$(dirname "$0")/../.." || exit 1
OUT=/tmp/frontier_qa_last.txt
PYTHONPATH=. timeout 1500 python3 tools/qa_quest_overhaul.py > "$OUT" 2>&1
if grep -q "quest overhaul OK" "$OUT"; then
  git push -q origin HEAD:main 2>&1 | grep -iv "moved\|github.com"; echo "QA OK, pushed"
else
  grep -A30 "problem(s)" "$OUT" | head -30; echo "QA FAILED, not pushed (full log: $OUT)"
fi
