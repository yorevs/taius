#!/usr/bin/env bash
set -euo pipefail

TARGET_FILE="${1:-}"
PATCH_FILE="${2:-}"

usage() {
  cat <<'EOF'
Usage:
  ./core-patcher.bash <target-file> <patch-file>
  ./core-patcher.bash <target-file> - < patch.diff

Examples:
  ./core-patcher.bash src/demo/devel/mather.py resources/patches/mather.patch
  ./core-patcher.bash src/demo/devel/mather.py - <<'PATCH'
--- src/demo/devel/mather.py
+++ src/demo/devel/mather.py
@@ -1,3 +1,4 @@
 import os
+import time
 import re
PATCH
EOF
}

die() {
  echo "ERROR: $*" >&2
  exit 1
}

ensure_tools() {
  command -v patch >/dev/null 2>&1 || die "'patch' command not found"
}

backup_file() {
  local file="$1"
  local backup_dir="resources/backups"
  local timestamp

  mkdir -p "$backup_dir"
  timestamp="$(date +"%Y%m%d-%H%M%S")"

  cp "$file" "$backup_dir/$(basename "$file").$timestamp.bak"
  echo "$backup_dir/$(basename "$file").$timestamp.bak"
}

validate_patch() {
  local target="$1"
  local patch_source="$2"

  [[ -f "$target" ]] || die "target file not found: $target"
  [[ -f "$patch_source" ]] || die "patch file not found: $patch_source"

  patch --dry-run --forward --reject-file=- "$target" < "$patch_source" >/dev/null || {
    die "patch dry-run failed: $patch_source"
  }

  echo "Patch dry-run passed: $patch_source"
}


apply_patch() {
  local target="$1"
  local patch_source="$2"
  local backup
  local tmp_patch=""

  [[ -f "$target" ]] || die "target file not found: $target"

  if [[ "$patch_source" == "-" ]]; then
    tmp_patch="$(mktemp)"
    cat > "$tmp_patch"
    patch_source="$tmp_patch"
  fi

  validate_patch "$target" "$patch_source"

  backup="$(backup_file "$target")"
  echo "Backup created: $backup"

  patch --forward --backup --reject-file=- "$target" < "$patch_source" || {
    cp "$backup" "$target"

    if [[ -n "$tmp_patch" ]]; then
      rm -f "$tmp_patch"
    fi

    die "patch failed; restored backup"
  }

  if [[ -n "$tmp_patch" ]]; then
    rm -f "$tmp_patch"
  fi

  echo "Patch applied successfully: $target"
}

main() {
  if [[ -z "$TARGET_FILE" || -z "$PATCH_FILE" ]]; then
    usage
    exit 1
  fi

  ensure_tools
  apply_patch "$TARGET_FILE" "$PATCH_FILE"
}

main "$@"
