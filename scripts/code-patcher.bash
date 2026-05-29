#!/usr/bin/env bash
set -euo pipefail

# The file to be patched
TARGET_FILE="${1:-}"

# The patch file or '-' to read from stdin
PATCH_FILE="${2:-}"

# Directory to store backups of patched files (optional, defaults to 'resources/backups')
BACKUP_DIR="${BACKUP_DIR:-resources/backups}"

# Show the expected command shape when arguments are missing.
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

# Exit immediately with a consistent error message.
die() {
  echo "ERROR: $*" >&2
  exit 1
}

# Verify that the system patch utility is available.
ensure_tools() {
  command -v patch >/dev/null 2>&1 || die "'patch' command not found"
}

# Create a timestamped backup copy of the file being patched.
backup_file() {
  local file="$1"
  local timestamp

  mkdir -p "${BACKUP_DIR}"
  timestamp="$(date +"%Y%m%d-%H%M%S")"

  cp "$file" "${BACKUP_DIR}/$(basename "$file").$timestamp.bak"
  echo "${BACKUP_DIR}/$(basename "$file").$timestamp.bak"
}

# Validate that the patch applies cleanly before making changes.
validate_patch() {
  local target="$1"
  local patch_source="$2"

  [[ -f "${target}" ]] || die "target file not found: ${target}"
  [[ -f "${patch_source}" ]] || die "patch file not found: ${patch_source}"

  patch --dry-run --forward --reject-file=- "${target}" < "${patch_source}" >/dev/null || {
    die "patch dry-run failed: ${patch_source}"
  }

  echo "Patch dry-run passed: ${patch_source}"
}

# Apply a patch, restoring the backup if the operation fails.
apply_patch() {
  local target="$1"
  local patch_source="$2"
  local backup
  local tmp_patch=""

  [[ -f "${target}" ]] || die "target file not found: ${target}"

  if [[ "${patch_source}" == "-" ]]; then
    tmp_patch="$(mktemp)"
    cat > "$tmp_patch"
    patch_source="$tmp_patch"
  fi

  validate_patch "${target}" "${patch_source}"

  backup="$(backup_file "${target}")"
  echo "Backup created: ${backup}"

  patch --forward --backup --reject-file=- "${target}" < "${patch_source}" || {
    cp "${backup}" "${target}"

    if [[ -n "$tmp_patch" ]]; then
      rm -f "$tmp_patch"
    fi

    die "patch failed; restored backup"
  }

  if [[ -n "$tmp_patch" ]]; then
    rm -f "$tmp_patch"
  fi

  echo "Patch applied successfully: ${target}"
}

# Validate arguments, verify tooling, and apply the patch.
main() {
  if [[ -z "$TARGET_FILE" || -z "$PATCH_FILE" ]]; then
    usage
    exit 1
  fi

  ensure_tools
  apply_patch "$TARGET_FILE" "$PATCH_FILE"
}

main "$@"
