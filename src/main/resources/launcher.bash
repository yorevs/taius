#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

RUNTIME_NAME="taius.py"
RUNTIME_FILE="$PROJECT_DIR/$RUNTIME_NAME"
PATCHER="$SCRIPT_DIR/core-patcher.bash"

PATCH_DIR="$SCRIPT_DIR/patches"
APPLIED_PATCH_DIR="$PATCH_DIR/applied"
REJECTED_PATCH_DIR="$PATCH_DIR/rejected"

BACKUP_DIR="$SCRIPT_DIR/backups"
MODEL_DIR="$SCRIPT_DIR/model"
CORE_DIR="$MODEL_DIR/core"
SKILLS_DIR="$MODEL_DIR/skills"

CORE_VERSION_FILE="$CORE_DIR/.core-version"
CURRENT_CORE_VERSION="1"

SEMVER_MAJOR="0"
SEMVER_MINOR="1"
SEMVER_PATCH="0"

BUILD_FILE="$CORE_DIR/.build-number"
VERSION_FILE="$CORE_DIR/version.txt"
PATCHES_APPLIED=0

die() {
  echo "ERROR: $*" >&2
  exit 1
}

log() {
  echo "==> $*"
}

format_build_number() {
  printf "%04d" "$1"
}

current_build_number() {
  local raw

  raw="$(cat "$BUILD_FILE" 2>/dev/null || echo "0000")"
  echo "$((10#$raw))"
}

write_version() {
  local build
  local formatted

  mkdir -p "$CORE_DIR"

  build="$(current_build_number)"
  formatted="$(format_build_number "$build")"

  echo "$formatted" > "$BUILD_FILE"
  echo "$SEMVER_MAJOR.$SEMVER_MINOR.$SEMVER_PATCH+$formatted" > "$VERSION_FILE"
}

bump_version() {
  local build
  local next

  build="$(current_build_number)"
  next="$((build + 1))"

  echo "$(format_build_number "$next")" > "$BUILD_FILE"
  write_version
}

print_version() {
  [[ -f "$VERSION_FILE" ]] || write_version
  log "Version: $(cat "$VERSION_FILE")"
}

ensure_layout() {
  mkdir -p "$PATCH_DIR"
  mkdir -p "$APPLIED_PATCH_DIR"
  mkdir -p "$REJECTED_PATCH_DIR"
  mkdir -p "$BACKUP_DIR"
  mkdir -p "$MODEL_DIR"
  mkdir -p "$CORE_DIR"
  mkdir -p "$SKILLS_DIR"

  if [[ ! -f "$BUILD_FILE" ]]; then
    echo "0000" > "$BUILD_FILE"
  fi

  write_version

  [[ -f "$RUNTIME_FILE" ]] || die "$RUNTIME_NAME not found: $RUNTIME_FILE"
  [[ -f "$PATCHER" ]] || die "patcher not found: $PATCHER"

  chmod +x "$PATCHER"
}

patch_target_file() {
  local patch_file="$1"
  local target

  target="$(
    awk '
      /^\+\+\+ / {
        value = $2
        sub(/^b\//, "", value)
        print value
        exit
      }
    ' "$patch_file"
  )"

  [[ -n "$target" ]] || return 1
  [[ "$target" != "/dev/null" ]] || return 1

  case "$target" in
    "$RUNTIME_NAME")
      echo "$RUNTIME_FILE"
      ;;
    core/*.py)
      echo "$PROJECT_DIR/$target"
      ;;
    skills/*/skill.py)
      echo "$PROJECT_DIR/$target"
      ;;
    resources/core-patcher.bash)
      echo "$PROJECT_DIR/$target"
      ;;
    resources/launcher.bash)
      return 1
      ;;
    *)
      return 1
      ;;
  esac
}

has_patches() {
  find "$PATCH_DIR" -maxdepth 1 -type f -name "*.patch" | grep -q .
}

move_patch() {
  local patch_file="$1"
  local target_dir="$2"
  local suffix="$3"
  local timestamp

  timestamp="$(date +"%Y%m%d-%H%M%S")"
  mkdir -p "$target_dir"

  mv "$patch_file" "$target_dir/$(basename "$patch_file").$timestamp.$suffix"
}

apply_patches() {
  local patch_list
  local patch_file
  local target_file

  has_patches || return 0

  log "Patch files found."

  patch_list="$(mktemp)"

  find "$PATCH_DIR" -maxdepth 1 -type f -name "*.patch" -print0 \
    | xargs -0 stat -f "%m %N" \
    | sort -n \
    | cut -d " " -f 2- > "$patch_list"

  while IFS= read -r patch_file; do
    [[ -n "$patch_file" ]] || continue

    target_file="$(patch_target_file "$patch_file" || true)"

    if [[ -z "${target_file:-}" ]]; then
      log "Skipping unsupported patch target: $patch_file"
      move_patch "$patch_file" "$REJECTED_PATCH_DIR" "skipped"
      continue
    fi

    if [[ ! -f "$target_file" ]]; then
      log "Skipping patch with missing target: $target_file"
      move_patch "$patch_file" "$REJECTED_PATCH_DIR" "missing-target"
      continue
    fi

    log "Applying patch: $patch_file"
    log "Target: $target_file"

    "$PATCHER" "$target_file" "$patch_file"

    PATCHES_APPLIED=1

    move_patch "$patch_file" "$APPLIED_PATCH_DIR" "applied"
  done < "$patch_list"

  rm -f "$patch_list"
}

core_version_changed() {
  [[ ! -f "$CORE_VERSION_FILE" ]] && return 0

  local saved_version
  saved_version="$(cat "$CORE_VERSION_FILE")"

  [[ "$saved_version" != "$CURRENT_CORE_VERSION" ]]
}

cleanup_core_if_needed() {
  core_version_changed || return 0

  log "Core version changed."

  echo "$CURRENT_CORE_VERSION" > "$CORE_VERSION_FILE"
}

run_taius() {
  log "Launching $RUNTIME_NAME"

  cd "$PROJECT_DIR"
  python3 "$RUNTIME_FILE"
}

main() {
  cd "$PROJECT_DIR"

  ensure_layout
  apply_patches

  if [[ "$PATCHES_APPLIED" == "1" ]]; then
    bump_version
  else
    write_version
  fi

  print_version

  cleanup_core_if_needed
  run_taius
}

main "$@"
