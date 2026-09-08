#!/usr/bin/env bash
# autoresearch.sh — GEO-INFER CODE-01 index-refresh benchmark harness.
#
# Deterministic, fully offline workload measuring the state of the repository
# ledger surfaces (TODO.md, CHANGELOG.md, ISA.md) with respect to the
# 2026-09-07 published-history rewrite and the CODE-01 GitNexus index receipt:
#
#   1. Pre-rewrite SHA annotation audit — every commit-SHA-like token
#      (7-40 hex chars, at least one [a-f], not all digits) in the three
#      ledger files is checked against the published history: a token is a
#      current identifier only when reachable from refs/remotes/origin/main
#      (`git merge-base --is-ancestor`). Everything else — pre-rewrite GEO
#      commits, external-repo SHAs, content digests — is a historical
#      identifier and its file must carry the dated pre-rewrite history
#      note. Historical tokens in a file without the note are annotation
#      gaps.
#   2. CODE-01 receipt check — the CODE-01 ledger row must record a fresh
#      GitNexus receipt: non-BLOCKED status, a dated entry, an index SHA
#      that resolves to a local commit and the `.gitnexus` artifact
#      location.
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
LEDGER_FILES=(TODO.md CHANGELOG.md ISA.md)
for f in "${LEDGER_FILES[@]}"; do
  [[ -f $f ]] || err "ledger file missing: $f"
done

extract_shas() {
  # Commit-SHA-like tokens: 7-40 hex chars, whole words, at least one [a-f],
  # not all digits (filters dates/counts like 20260907), lowercased, unique.
  perl -ne 'while (/\b([0-9a-fA-F]{7,40})\b/g) {
    my $t = lc $1;
    next if $t =~ /^[0-9]+$/;
    next unless $t =~ /[a-f]/;
    print "$t\n";
  }' "$1" | sort -u
}

# Current identifier = reachable from the local origin/main remote-tracking
# ref (the published post-rewrite history; fetch before benchmark runs).
on_origin() {
  git merge-base --is-ancestor "$1" refs/remotes/origin/main >/dev/null 2>&1
}
# Local commit identity = object exists in this clone's object database.
local_commit() {
  git rev-parse --verify --quiet "${1}^{commit}" >/dev/null 2>&1
}

gaps=0
unresolved_total=0
notes_present=0

for f in "${LEDGER_FILES[@]}"; do
  note=0
  grep -qiE 'pre-rewrite' "$f" && note=1
  notes_present=$((notes_present + note))
  file_unresolved=0
  while IFS= read -r sha; do
    [[ -n $sha ]] || continue
    if on_origin "$sha"; then
      echo "audit: $f $sha current (reachable from origin/main)"
    else
      echo "audit: $f $sha HISTORICAL (not reachable from origin/main)"
      unresolved_total=$((unresolved_total + 1))
      file_unresolved=$((file_unresolved + 1))
    fi
  done < <(extract_shas "$f")
  if (( file_unresolved > 0 && note == 0 )); then
    echo "gap: $f carries $file_unresolved pre-rewrite identifier(s) without the history note"
    gaps=$((gaps + file_unresolved))
  fi
done

# --- CODE-01 receipt --------------------------------------------------------
receipt=0
row=$(grep -E '^\| \*\*CODE-01\*\*' TODO.md) || err "CODE-01 row not found in TODO.md"
if [[ $row != *BLOCKED-EXTERN* && $row == *2026-09-* && $row == *'.gitnexus'* ]]; then
  while IFS= read -r sha; do
    [[ -n $sha ]] || continue
    if local_commit "$sha"; then
      echo "receipt: CODE-01 row records local index SHA $sha"
      receipt=1
      break
    fi
  done < <(extract_shas <(printf '%s\n' "$row"))
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
