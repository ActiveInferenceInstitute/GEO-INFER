#!/usr/bin/env bash
# autoresearch.sh — GEO-INFER CODE-01 index-refresh benchmark harness.
#
# Deterministic, fully offline workload measuring the state of the repository
# ledger surfaces (root TODO.md, CHANGELOG.md, ISA.md plus the two
# GEO-INFER-TEST GNN receipt files) with respect to the 2026-09-07
# published-history rewrite and the CODE-01 GitNexus index receipt:
#
#   1. Pre-rewrite SHA annotation audit — every commit-SHA-like token
#      (7-40 hex chars, at least one [a-f], not ellipsis-truncated) in the
#      ledger files is checked against the published history: a token is a
#      current identifier only when reachable from refs/remotes/origin/main
#      (`git merge-base --is-ancestor`). Everything else — pre-rewrite GEO
#      commits, external-repo SHAs, content digests — is a historical
#      identifier and its file must carry the dated pre-rewrite history
#      note. Historical tokens in a file without the note are annotation
#      gaps.
#   2. CODE-01 receipt check — the CODE-01 ledger row must record a fresh
#      GitNexus receipt: a REFRESHED-style non-blocked status with the
#      2026-09-07 date, the `.gitnexus` artifact location and an index SHA
#      that is an ancestor of HEAD (never a stale object-database
#      identifier).
#   3. gitnexus CLI availability probe (local evidence, no network).
#
#   Note: requires refs/remotes/origin/main (run `git fetch origin main`
#      before benchmarking); the harness itself performs no network access.

set -uo pipefail
export LC_ALL=C
cd "$(dirname "$0")" || exit 1

err() { echo "HARNESS_ERROR: $*" >&2; exit 1; }

git rev-parse --verify --quiet refs/remotes/origin/main >/dev/null 2>&1 \
  || err "refs/remotes/origin/main missing; run 'git fetch origin main' first"
command -v perl >/dev/null 2>&1 || err "perl not available"
LEDGER_FILES=(
  TODO.md
  CHANGELOG.md
  ISA.md
  GEO-INFER-TEST/docs/gnn_continuation_2026_09.md
  GEO-INFER-TEST/docs/gnn_space_time_2026_09.md
)
for f in "${LEDGER_FILES[@]}"; do
  [[ -f $f ]] || err "ledger file missing: $f"
done

sha_tmp=$(mktemp) || err "mktemp failed"
row_tmp=$(mktemp) || err "mktemp failed"
trap 'rm -f "$sha_tmp" "$row_tmp"' EXIT

# extract_shas <input> <output>: write unique commit-SHA-like tokens (7-40
# hex chars, whole words, at least one [a-f], not ellipsis-truncated — a
# trailing `…`/`...` marks a content-digest prefix, not a commit) to
# <output>. The pipeline status propagates via pipefail so a broken
# extraction can never be mistaken for a clean ledger.
extract_shas() {
  perl -ne 'while (/\b([0-9a-fA-F]{7,40})\b(?!\xe2\x80\xa6|\.{3})/g) {
    my $t = lc $1;
    next unless $t =~ /[a-f]/;
    print "$t\n";
  }' "$1" | sort -u > "$2"
}

# Current identifier = reachable from the local origin/main remote-tracking
# ref (the published post-rewrite history; fetch before benchmark runs).
on_origin() {
  git merge-base --is-ancestor "$1" refs/remotes/origin/main >/dev/null 2>&1
}
# Branch-history identity = ancestor of HEAD; rejects stale pre-rewrite
# objects that survive in the local object database.
on_head() {
  git merge-base --is-ancestor "$1" HEAD >/dev/null 2>&1
}

gaps=0
unresolved_total=0
notes_present=0

for f in "${LEDGER_FILES[@]}"; do
  # Annotation coverage = the file carries the dated pre-rewrite note.
  note=0
  grep -qiE 'pre-rewrite' "$f" && grep -q '2026-09-07' "$f" && note=1
  notes_present=$((notes_present + note))
  file_unresolved=0
  if ! extract_shas "$f" "$sha_tmp"; then
    err "SHA extraction failed for $f"
  fi
  while IFS= read -r sha; do
    [[ -n $sha ]] || continue
    if on_origin "$sha"; then
      echo "audit: $f $sha current (reachable from origin/main)"
    else
      echo "audit: $f $sha HISTORICAL (not reachable from origin/main)"
      unresolved_total=$((unresolved_total + 1))
      file_unresolved=$((file_unresolved + 1))
    fi
  done < "$sha_tmp"
  if (( file_unresolved > 0 && note == 0 )); then
    echo "gap: $f carries $file_unresolved pre-rewrite identifier(s) without the history note"
    gaps=$((gaps + file_unresolved))
  fi
done

# --- CODE-01 receipt --------------------------------------------------------
receipt=0
row=$(grep -m 1 -E '^\| \*\*CODE-01\*\*' TODO.md) || err "CODE-01 row not found in TODO.md"
if [[ $row != *BLOCKED-EXTERN* && $row == *REFRESHED* && $row == *2026-09-07* && $row == *'.gitnexus'* ]]; then
  printf '%s\n' "$row" > "$row_tmp"
  if ! extract_shas "$row_tmp" "$sha_tmp"; then
    err "CODE-01 row SHA extraction failed"
  fi
  while IFS= read -r sha; do
    [[ -n $sha ]] || continue
    if on_head "$sha"; then
      echo "receipt: CODE-01 row records index SHA $sha (ancestor of HEAD)"
      receipt=1
      break
    fi
  done < "$sha_tmp"
fi

cli=0
command -v gitnexus >/dev/null 2>&1 && cli=1

# ledger_gaps: one unit per unannotated pre-rewrite reference plus one unit
# while the CODE-01 row lacks a recorded fresh-index receipt.
ledger_gaps=$((gaps + (1 - receipt)))

echo "METRIC ledger_gaps=$ledger_gaps"
echo "METRIC sha_annotation_gaps=$gaps"
echo "METRIC index_receipt_valid=$receipt"
echo "METRIC unresolved_sha_refs=$unresolved_total"
echo "METRIC history_notes_present=$notes_present"
echo "METRIC gitnexus_cli_present=$cli"
exit 0
