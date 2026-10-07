#!/usr/bin/env bash
# Build the repo at BASE (default: HEAD) and in the working tree into separate dirs and show what differs.
# Only intended files should differ. Usage: diff-builds.sh "<build cmd>" <output-dir> [base-ref]
#   diff-builds.sh "node tools/build-pages.mjs" . HEAD     # generator writes into the repo root
#   diff-builds.sh "npm run build" dist origin/main
set -euo pipefail
CMD=${1:?build command}; OUT=${2:?output dir relative to repo root}; BASE=${3:-HEAD}
ROOT=$(git rev-parse --show-toplevel); TMP=$(mktemp -d); trap 'git -C "$ROOT" worktree remove --force "$TMP/base" 2>/dev/null; rm -rf "$TMP"' EXIT
git -C "$ROOT" worktree add --detach "$TMP/base" "$BASE" >/dev/null
[ -d "$ROOT/node_modules" ] && ln -s "$ROOT/node_modules" "$TMP/base/node_modules"
echo "[diff-builds] building BASE=$BASE"; (cd "$TMP/base" && bash -c "$CMD" >/dev/null)
echo "[diff-builds] building working tree"; (cd "$ROOT" && bash -c "$CMD" >/dev/null)
EXC=(--exclude=.git --exclude=node_modules)
echo "[diff-builds] files that differ (base vs work) in $OUT:"
diff -rq "${EXC[@]}" "$TMP/base/$OUT" "$ROOT/$OUT" | sed "s#$TMP/base#BASE#; s#$ROOT#WORK#" || true
