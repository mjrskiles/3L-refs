# Everything project-local: uv lives in .venv/, Hugo in bin/, uv's caches and
# managed Pythons in .uv/. No system installs.
UV_ENV := UV_CACHE_DIR=$(CURDIR)/.uv/cache UV_PYTHON_INSTALL_DIR=$(CURDIR)/.uv/python
UV     := $(UV_ENV) $(CURDIR)/.venv/bin/uv
HUGO   := $(CURDIR)/bin/hugo

.PHONY: setup test build serve check fonts

setup: ## bootstrap the whole toolchain (idempotent; macOS + Linux/RPi)
	@python3 -c 'import venv' 2>/dev/null || \
	  { echo "python3 venv module missing — on Debian/RPi OS: sudo apt install python3-venv"; exit 1; }
	test -x .venv/bin/uv || (python3 -m venv .venv && .venv/bin/pip install -q uv)
	tools/get_hugo.sh
	cd figures && $(UV) sync

test:
	cd figures && $(UV) run pytest -q

build:
	$(HUGO) --gc --minify

serve:
	$(HUGO) server -D

check: build test
	cd figures && $(UV) run python ../tools/check_origins.py ../public
	cd figures && $(UV) run python ../tools/check_tags.py ..

fonts: ## regenerate subset fonts into static/fonts/ (rarely needed)
	cd figures && $(UV) run python ../tools/subset_fonts.py
