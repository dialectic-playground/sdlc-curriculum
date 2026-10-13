# Makefile for dialectic-playground/sdlc-curriculum (container-first; see tools/container.mk).
#
#   make                 same as `make check`
#   make check           everything CI checks: curriculum, wiring, consistency, launchers
#   make curriculum      structure, help text, and every fixture (check-curriculum.py)
#   make wiring          the BASE-MAKEFILE contract fails loudly on an undefined hook
#   make consistency     generated assignment/ files and the CI template's pins are in sync
#   make launchers       `#!` script launchers work as tools on this OS (Windows included)
#   make scaffold        regenerate every project's assignment/ from the templates
#   make dp-info | dp-shell | dp-image
#
# Every goal runs in the toolchain container built from ./Containerfile: podman, then docker,
# then the local system. Override with DP_RUNTIME=podman|docker|local or DP_IMAGE=<image>.

DP_HOST_GOALS += help
include tools/container.mk
ifeq ($(DP_DELEGATE),)

SHELL := /bin/sh
.DEFAULT_GOAL := check
ifeq ($(OS),Windows_NT)
  PYTHON ?= python
else
  PYTHON ?= python3
endif
WIRING_PROJECT := projects/00-hello-world/assignment
CI_TEMPLATE := shared/ci/cross-platform-ci.yml

.PHONY: check curriculum wiring consistency launchers scaffold help

check: curriculum wiring consistency launchers

curriculum:
	$(PYTHON) shared/tools/check-curriculum.py

wiring:
	$(MAKE) --no-print-directory -C $(WIRING_PROJECT) help
	@if $(MAKE) --no-print-directory -C $(WIRING_PROJECT) all > /dev/null 2>&1; then \
		echo "expected 'make all' to fail when DP_BUILD is undefined" >&2; exit 1; \
	else echo "wiring: undefined hooks fail loudly (as required)"; fi

consistency:
	$(PYTHON) tools/scaffold-project.py --force > /dev/null
	git diff --exit-code --stat -- projects/ \
		|| { echo "run 'make scaffold' and commit the regenerated assignment/ files" >&2; exit 1; }
	@status=0; \
	if grep -E '^[[:space:]]*(- )?uses:' $(CI_TEMPLATE) | grep -vqE '@[0-9a-f]{40} # v[0-9]'; then \
		echo "$(CI_TEMPLATE) has an action not pinned as '@<40-hex-sha> # vX.Y.Z'" >&2; status=1; \
	fi; \
	for pin in $$(grep -oE '[a-z0-9_.-]+/[a-z0-9_.-]+@[0-9a-f]{40}' $(CI_TEMPLATE) | sort -u); do \
		grep -qF "$$pin" .github/workflows/ci.yml \
			|| { echo "$(CI_TEMPLATE) pins $$pin, unlike .github/workflows/ci.yml" >&2; status=1; }; \
	done; \
	[ $$status -eq 0 ] && echo "consistency: CI template pins match .github/workflows/ci.yml"; exit $$status

launchers:
	$(PYTHON) shared/tools/selftest-launchers.py

scaffold:
	$(PYTHON) tools/scaffold-project.py --force

help:
	@sed -n '3,14p' Makefile | sed 's/^# \{0,1\}//'

endif
