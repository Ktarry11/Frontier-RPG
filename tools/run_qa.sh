#!/usr/bin/env bash
# Run QA scripts in parallel, one log each, and print "<exit code> <script>" per script.
#
#   bash tools/run_qa.sh qa_quest_hubs qa_secrets audit_quest_directions
#
# One fixed command for every QA run, so the same command can be allowed once instead of a different shell
# pipeline each time (Kyle, 17 Nov 2026: "Why can't I select always allow"). Logs go to $QA_LOGS
# (default /tmp/frontier_qa), named <script>.log.
cd "$(dirname "$0")/.." || exit 2
LOGS="${QA_LOGS:-/tmp/frontier_qa}"
mkdir -p "$LOGS"
export PYTHONPATH=. SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy
printf '%s\n' "$@" | sed 's/\.py$//' | xargs -P "${QA_JOBS:-3}" -I{} sh -c \
  'timeout 1500 python3 tools/{}.py > "'"$LOGS"'/{}.log" 2>&1; echo "$? {}"'
