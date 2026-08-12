#!/usr/bin/env bash
# Fetch a pinned Hugo binary into ./bin/ — no system install.
# Supports macOS (arm64/x86_64) and Linux (arm64/armv7/x86_64), so the same
# checkout works on a MacBook and on a Raspberry Pi.
#
# Non-extended Hugo is deliberate: the site uses plain CSS (no SCSS), so the
# extended build's libsass/CGO dependency buys nothing and costs portability.
set -euo pipefail

HUGO_VERSION="0.164.0"
BASE="https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}"

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BIN="$ROOT/bin"

if [ -x "$BIN/hugo" ] && "$BIN/hugo" version | grep -q "v$HUGO_VERSION"; then
  echo "hugo v$HUGO_VERSION already present at bin/hugo"
  exit 0
fi

OS="$(uname -s)"
ARCH="$(uname -m)"

case "$OS" in
  Darwin) ASSET="hugo_${HUGO_VERSION}_darwin-universal.pkg" ;;
  Linux)
    case "$ARCH" in
      aarch64|arm64) ASSET="hugo_${HUGO_VERSION}_linux-arm64.tar.gz" ;;
      x86_64|amd64)  ASSET="hugo_${HUGO_VERSION}_linux-amd64.tar.gz" ;;
      armv7l|armv6l) ASSET="hugo_${HUGO_VERSION}_linux-arm.tar.gz" ;;
      *) echo "unsupported Linux arch: $ARCH" >&2; exit 1 ;;
    esac
    ;;
  *) echo "unsupported OS: $OS" >&2; exit 1 ;;
esac

# sha256 verification: coreutils on Linux, perl-ish shasum on macOS
if command -v sha256sum >/dev/null 2>&1; then
  SHACHECK="sha256sum -c -"
elif command -v shasum >/dev/null 2>&1; then
  SHACHECK="shasum -a 256 -c -"
else
  echo "need sha256sum or shasum to verify the download" >&2; exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

# --retry-all-errors: GitHub's release CDN throws transient 503s, which plain
# --retry treats as permanent; two deploys died on exactly that (2026-08-12).
CURL="curl -fsSL --retry 5 --retry-delay 3 --retry-all-errors"

echo "fetching $ASSET ..."
$CURL -o "$TMP/$ASSET" "$BASE/$ASSET"
$CURL -o "$TMP/checksums.txt" "$BASE/hugo_${HUGO_VERSION}_checksums.txt"
(cd "$TMP" && grep " $ASSET\$" checksums.txt | $SHACHECK)

mkdir -p "$BIN"
case "$OS" in
  Darwin)
    # macOS releases ship only as .pkg; pkgutil expands it without installing.
    pkgutil --expand-full "$TMP/$ASSET" "$TMP/expanded"
    HUGO_BIN="$(find "$TMP/expanded" -type f -name hugo | head -1)"
    [ -n "$HUGO_BIN" ] || { echo "hugo binary not found in pkg" >&2; exit 1; }
    cp "$HUGO_BIN" "$BIN/hugo"
    ;;
  Linux)
    tar -xzf "$TMP/$ASSET" -C "$TMP" hugo
    cp "$TMP/hugo" "$BIN/hugo"
    ;;
esac

chmod +x "$BIN/hugo"
"$BIN/hugo" version
