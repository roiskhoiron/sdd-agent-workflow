#!/usr/bin/env bash
# Pemasang sdd-agent-workflow untuk AI coding agent.
#
# Interaktif:      ./install.sh
# Tanpa bertanya:  ./install.sh --agent claude,codex --scope project --target ~/kerja/spesifikasi --yes
# Lewat internet:  curl -fsSL https://raw.githubusercontent.com/roiskhoiron/sdd-agent-workflow/master/install.sh | bash
# Copot:           ./install.sh --uninstall --scope project --target ~/kerja/spesifikasi
set -euo pipefail

REPO_URL="${SDD_REPO_URL:-https://github.com/roiskhoiron/sdd-agent-workflow.git}"
REPO_REF="${SDD_REPO_REF:-master}"

AGENT="" SCOPE="" TARGET="" YES=0 UNINSTALL=0
PASS=()

bold() { printf '\033[1m%s\033[0m\n' "$*"; }
info() { printf '%s\n' "$*"; }
die() { printf 'gagal: %s\n' "$*" >&2; exit 1; }

usage() {
  cat <<'USAGE'
Pemasang sdd-agent-workflow.

Pemakaian: install.sh [opsi]

Tanpa opsi, pemasang bertanya langkah demi langkah.

  --agent LIST        alat yang dipasang, dipisah koma:
                      claude, codex, gemini, opencode, cursor, copilot, generic
  --scope SCOPE       project (hanya satu folder proyek) atau global (semua proyek)
  --target DIR        folder proyek untuk scope project (default: folder sekarang)
  --role-mode MODE    native (subagent bawaan alat) atau headless (proses baru)
  --headless-cmd CMD  perintah sekali jalan untuk agen "generic", misal 'aider --message "<prompt>"'
  --yes, -y           jangan bertanya, pakai nilai yang diberikan
  --dry-run           tampilkan rencana tanpa menulis apa pun
  --force             timpa berkas yang sudah ada
  --uninstall         copot dari scope dan target yang diberikan
  -h, --help          tampilkan bantuan ini
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --agent) AGENT="${2:-}"; shift 2 ;;
    --agent=*) AGENT="${1#*=}"; shift ;;
    --scope) SCOPE="${2:-}"; shift 2 ;;
    --scope=*) SCOPE="${1#*=}"; shift ;;
    --target) TARGET="${2:-}"; shift 2 ;;
    --target=*) TARGET="${1#*=}"; shift ;;
    --role-mode|--headless-cmd) PASS+=("$1" "${2:-}"); shift 2 ;;
    --role-mode=*|--headless-cmd=*|--dry-run|--force) PASS+=("$1"); shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    -y|--yes) YES=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) die "opsi tidak dikenal: $1 (lihat --help)" ;;
  esac
done

# --- Python ---
command -v python3 >/dev/null 2>&1 || die "python3 tidak ditemukan. Pasang Python 3.8 atau lebih baru."
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' \
  || die "butuh Python 3.8 atau lebih baru, yang terpasang: $(python3 --version 2>&1)"

# --- Sumber workflow: folder repo ini, atau unduh bila dijalankan lewat curl ---
SRC=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "$(dirname "${BASH_SOURCE[0]}")/scripts/install_agent.py" ]; then
  SRC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
  command -v git >/dev/null 2>&1 || die "git dibutuhkan untuk mengunduh workflow."
  SRC="$(mktemp -d)"
  trap 'rm -rf "$SRC"' EXIT
  info "Mengunduh workflow dari $REPO_URL ($REPO_REF)..."
  git clone --quiet --depth 1 --branch "$REPO_REF" "$REPO_URL" "$SRC" || die "gagal mengunduh $REPO_URL"
fi
INSTALLER="$SRC/scripts/install_agent.py"

# --- Masukan interaktif dibaca dari terminal, juga saat dijalankan lewat curl | bash ---
TTY=""
if [ "$YES" -eq 0 ] && { [ -t 0 ] || { [ -r /dev/tty ] && (: </dev/tty) 2>/dev/null; }; }; then
  TTY=/dev/tty
fi
ask() { # ask "pertanyaan" "default" -> REPLY
  local q="$1" def="${2:-}"
  if [ -z "$TTY" ]; then REPLY="$def"; return; fi
  if [ -n "$def" ]; then printf '%s [%s]: ' "$q" "$def" >/dev/tty; else printf '%s: ' "$q" >/dev/tty; fi
  IFS= read -r REPLY </dev/tty || REPLY=""
  REPLY="${REPLY:-$def}"
}

KEYS=(claude codex gemini opencode cursor copilot generic)
LABELS=("Claude Code" "OpenAI Codex CLI" "Gemini CLI" "OpenCode" "Cursor (editor dan CLI)" \
        "GitHub Copilot (VS Code dan CLI)" "Agen lain yang membaca AGENTS.md")

detected() { # apakah alat terlihat terpasang di mesin ini
  case "$1" in
    claude)   command -v claude >/dev/null 2>&1 || [ -d "$HOME/.claude" ] ;;
    codex)    command -v codex >/dev/null 2>&1 || [ -d "$HOME/.codex" ] ;;
    gemini)   command -v gemini >/dev/null 2>&1 || [ -d "$HOME/.gemini" ] ;;
    opencode) command -v opencode >/dev/null 2>&1 || [ -d "$HOME/.config/opencode" ] ;;
    cursor)   command -v cursor-agent >/dev/null 2>&1 || command -v cursor >/dev/null 2>&1 || [ -d "$HOME/.cursor" ] ;;
    copilot)  command -v copilot >/dev/null 2>&1 || [ -d "$HOME/.copilot" ] ;;
    *) return 1 ;;
  esac
}

if [ "$UNINSTALL" -eq 0 ] && [ -z "$AGENT" ]; then
  [ -n "$TTY" ] || die "tidak ada terminal untuk bertanya. Pakai --agent dan --scope (lihat --help)."
  bold "1. Pilih AI coding agent"
  defaults=()
  for i in "${!KEYS[@]}"; do
    mark="   "
    if detected "${KEYS[$i]}"; then mark=" * "; defaults+=("$((i + 1))"); fi
    printf '  %d)%s%s\n' "$((i + 1))" "$mark" "${LABELS[$i]}" >/dev/tty
  done
  info "  * terdeteksi di komputer ini" >/dev/tty
  info "  Boleh lebih dari satu, pisahkan dengan spasi. Contoh: 1 2" >/dev/tty
  ask "Nomor" "${defaults[*]:-1}"
  picked=()
  for n in $REPLY; do
    [[ "$n" =~ ^[0-9]+$ ]] && [ "$n" -ge 1 ] && [ "$n" -le "${#KEYS[@]}" ] || die "pilihan tidak valid: $n"
    picked+=("${KEYS[$((n - 1))]}")
  done
  [ "${#picked[@]}" -gt 0 ] || die "tidak ada alat yang dipilih"
  AGENT="$(IFS=,; echo "${picked[*]}")"
fi

if [ -z "$SCOPE" ]; then
  if [ -n "$TTY" ]; then
    bold "2. Pilih scope"
    info "  1) project  hanya untuk satu folder proyek, bisa di-commit dan dipakai bersama tim" >/dev/tty
    info "  2) global   untuk semua proyek di komputer ini, hanya untuk kamu" >/dev/tty
    ask "Nomor" "1"
    case "$REPLY" in 1|project) SCOPE=project ;; 2|global) SCOPE=global ;; *) die "pilihan tidak valid: $REPLY" ;; esac
  else
    SCOPE=project
  fi
fi
case "$SCOPE" in project|global) ;; *) die "--scope harus project atau global" ;; esac

if [ "$SCOPE" = project ] && [ -z "$TARGET" ]; then
  if [ -n "$TTY" ]; then
    bold "3. Folder proyek"
    info "  Folder tempat dokumen spesifikasi dan tiket akan ditulis." >/dev/tty
    ask "Folder" "$PWD"
    TARGET="$REPLY"
  else
    TARGET="$PWD"
  fi
fi
TARGET="${TARGET:-$PWD}"
TARGET="${TARGET/#\~/$HOME}"
if [ "$SCOPE" = project ] && [ "$UNINSTALL" -eq 0 ] && [ ! -d "$TARGET" ]; then
  ask "Folder $TARGET belum ada. Buat? (y/n)" "y"
  case "$REPLY" in y|Y|ya) mkdir -p "$TARGET" ;; *) die "dibatalkan" ;; esac
fi

ARGS=(--scope "$SCOPE" --target "$TARGET")
[ -n "$AGENT" ] && ARGS+=(--agent "$AGENT")
[ "${#PASS[@]}" -gt 0 ] && ARGS+=("${PASS[@]}")

if [ "$UNINSTALL" -eq 1 ]; then
  bold "Mencopot sdd-agent-workflow ($SCOPE${AGENT:+, $AGENT})"
  python3 "$INSTALLER" --uninstall "${ARGS[@]}"
  exit $?
fi

bold "Ringkasan"
info "  Alat   : $AGENT"
info "  Scope  : $SCOPE"
[ "$SCOPE" = project ] && info "  Folder : $TARGET"
if [ -n "$TTY" ]; then
  ask "Lanjutkan? (y/n)" "y"
  case "$REPLY" in y|Y|ya) ;; *) die "dibatalkan" ;; esac
fi

status=0
python3 "$INSTALLER" "${ARGS[@]}" || status=$?
if [ "$status" -eq 0 ] || [ "$status" -eq 3 ]; then
  echo
  bold "Langkah berikutnya"
  if [ "$SCOPE" = project ]; then
    info "  1. Buka $TARGET dengan coding agent pilihanmu."
  else
    info "  1. Buka folder kerja spesifikasimu dengan coding agent pilihanmu."
  fi
  info "  2. Jalankan initiate-epic-ticket dengan nama proyek dan kebutuhan."
  info "     Cara memanggilnya per alat ada di README, bagian \"Cara memanggil perintah\"."
  info "  3. Isi project.json dan foundation/ yang dibuat, lalu jalankan perintah yang sama lagi."
fi
exit "$status"
