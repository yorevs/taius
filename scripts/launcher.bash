#!/usr/bin/env bash
set -euo pipefail

# Resolve the project layout and runtime entry point.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# The project root is the parent of the script directory
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# The resources directory is where patches, backups, and version files are stored
RESOURCE_DIR="$PROJECT_DIR/src/main/resources"

# The patch directory is where new patch files are placed for application
PATCH_DIR="$RESOURCE_DIR/patches"

# Applied patches are archived here with timestamped names for reference
APPLIED_PATCH_DIR="$PATCH_DIR/applied"

# Rejected patches are moved here with timestamped names for investigation and manual handling
REJECTED_PATCH_DIR="$PATCH_DIR/rejected"

# Backups of original files before patching are stored here with timestamped names for recovery if needed
export BACKUP_DIR="$RESOURCE_DIR/backups"

# The model directory contains the trained models and related code for the core and skills
MODEL_DIR="$RESOURCE_DIR/model"

# The model core data
CORE_DIR="$MODEL_DIR/core"

# The model skills data
SKILLS_DIR="$MODEL_DIR/skills"

# The Python path is set to the main source directory for runtime execution
export PYTHONPATH="$PROJECT_DIR/src/main"

# The runtime entry point is the main module in the taius package
RUNTIME_NAME="__main__.py"

# The full path to the runtime file and the patcher utility
RUNTIME_FILE="$PROJECT_DIR/src/main/taius/$RUNTIME_NAME"

# The patcher is a standalone script that applies unified diff patches to target files
PATCHER="$SCRIPT_DIR/code-patcher.bash"

# The core version file tracks the layout version of the core directory, which can trigger cleanup if it changes.
CORE_VERSION_FILE="$CORE_DIR/.core-version"

# The current core version is a simple string that should be updated whenever the layout of the core directory changes in a way that would invalidate existing patches. This allows the launcher to detect when the core has changed and perform any necessary cleanup or adjustments before applying patches.
CURRENT_CORE_VERSION="1"

# semver: major.minor.patch+build
SEMVER_MAJOR="0"
SEMVER_MINOR="1"
SEMVER_PATCH="0"
BUILD_FILE="$CORE_DIR/.build-number"
VERSION_FILE="$CORE_DIR/version.txt"

# A flag to track whether any patches were applied during this run, which will trigger a version bump if true.
PATCHES_APPLIED=0

# Exit immediately with a consistent error message.
die() {
  echo "ERROR: $*" >&2
  exit 1
}

# Emit a launcher progress message.
log() {
  echo "==> $*"
}

# Format build numbers as zero-padded four digit values.
format_build_number() {
  printf "%04d" "$1"
}

# Read the persisted build number, defaulting to zero when missing.
current_build_number() {
  local raw

  raw="$(cat "$BUILD_FILE" 2>/dev/null || echo "0000")"
  echo "$((10#$raw))"
}

# Write the current semantic version to the version files.
write_version() {
  local build
  local formatted

  mkdir -p "$CORE_DIR"

  build="$(current_build_number)"
  formatted="$(format_build_number "$build")"

  echo "$formatted" > "$BUILD_FILE"
  echo "$SEMVER_MAJOR.$SEMVER_MINOR.$SEMVER_PATCH+$formatted" > "$VERSION_FILE"
}

# Increment the build number and refresh the version files.
bump_version() {
  local build
  local next

  build="$(current_build_number)"
  next="$((build + 1))"

  format_build_number "$next" > "$BUILD_FILE"
  write_version
}

# Print the current version, creating it first if needed.
print_version() {
  [[ -f "$VERSION_FILE" ]] || write_version
  log "Version: $(cat "$VERSION_FILE")"
}

# Ensure all expected directories and files exist before launch.
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

# Map a patch file back to its target path inside the project.
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

# Check whether there are any patch files waiting to be applied.
has_patches() {
  find "$PATCH_DIR" -maxdepth 1 -type f -name "*.patch" | grep -q .
}

# Move a patch into a result folder with a timestamped suffix.
move_patch() {
  local patch_file="$1"
  local target_dir="$2"
  local suffix="$3"
  local timestamp

  timestamp="$(date +"%Y%m%d-%H%M%S")"
  mkdir -p "$target_dir"

  mv "$patch_file" "$target_dir/$(basename "$patch_file").$timestamp.$suffix"
}

# Apply pending patches in timestamp order and archive the results.
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

# Detect whether the core layout version has changed since the last run.
core_version_changed() {
  [[ ! -f "$CORE_VERSION_FILE" ]] && return 0

  local saved_version
  saved_version="$(cat "$CORE_VERSION_FILE")"

  [[ "$saved_version" != "$CURRENT_CORE_VERSION" ]]
}

# Record the current core layout version when it changes.
cleanup_core_if_needed() {
  core_version_changed || return 0

  log "Core version changed."

  echo "$CURRENT_CORE_VERSION" > "$CORE_VERSION_FILE"
}

# Launch the Taius Python entry point from the project root.
run_taius() {
  log "Launching $RUNTIME_FILE"

  cd "$PROJECT_DIR"
  python3 "$RUNTIME_FILE"
}

# Prepare the project, apply patches, print the version, and launch Taius.
main() {
  cd "$PYTHONPATH"
  pwd

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
