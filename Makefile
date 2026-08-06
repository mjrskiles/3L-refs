# Everything project-local: uv lives in .venv/, Hugo in bin/, uv's caches and
# managed Pythons in .uv/. No system installs.
UV_ENV := UV_CACHE_DIR=$(CURDIR)/.uv/cache UV_PYTHON_INSTALL_DIR=$(CURDIR)/.uv/python
UV     := $(UV_ENV) $(CURDIR)/.venv/bin/uv
HUGO   := $(CURDIR)/bin/hugo

.PHONY: setup test build serve serve-lan check fonts fonts-force

setup: ## bootstrap the whole toolchain (idempotent; macOS + Linux/RPi)
	@python3 -c 'import venv' 2>/dev/null || \
	  { echo "python3 venv module missing — on Debian/RPi OS: sudo apt install python3-venv"; exit 1; }
	test -x .venv/bin/uv || (python3 -m venv .venv && .venv/bin/pip install -q uv)
	tools/get_hugo.sh
	cd figures && $(UV) sync

test:
	cd figures && $(UV) run pytest -q

# --cleanDestinationDir: Hugo leaves files from previous builds in public/ otherwise.
# Renaming or unpublishing a page would leave the old copy behind — and deploy it.
build:
	$(HUGO) --gc --minify --cleanDestinationDir

LAN_IP := $(shell hostname -I 2>/dev/null | awk '{print $$1}')

serve:
	$(HUGO) server -D

# hugo server binds to 127.0.0.1, which is unreachable from another machine when
# the Pi is headless. Binds all interfaces and sets baseURL so live-reload's
# websocket resolves. LAN-only — do not expose this beyond the local network.
serve-lan:
	@echo "serving on http://$(LAN_IP):1313/  (drafts visible)"
	$(HUGO) server -D --bind 0.0.0.0 --baseURL http://$(LAN_IP):1313/

check: build test
	cd figures && $(UV) run python ../tools/check_origins.py ../public
	cd figures && $(UV) run python ../tools/check_tags.py ..

fonts: ## regenerate subset fonts into static/fonts/ (rarely needed)
	cd figures && $(UV) run python ../tools/subset_fonts.py $(FONT_ARGS)

# Changing UNICODES or LAYOUT_FEATURES does not invalidate the presence check in
# subset_fonts.py — use this after editing either, or nothing regenerates.
fonts-force: FONT_ARGS=--force
fonts-force: fonts
