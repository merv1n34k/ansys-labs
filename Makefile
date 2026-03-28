.PHONY: setup dev build test test-all lint fmt clean
.PHONY: l1g l2g l3g l4g l5g allg
.PHONY: l1s l2s l3s l4s l5s
.PHONY: l1p l2p l3p l4p l5p
.PHONY: reports reports-clean

GEOM_DIR := geometry
ANSYS_DIR := ansys
STEP_DIR := $(GEOM_DIR)/step
RESULTS_DIR := results
REPORTS_DIR := reports

LABS := lab1 lab2 lab3 lab4 lab5
RUNWB2 ?= xvfb-run --auto-servernum ../ansys.sh wb
export ANSYS_LABS_ROOT := $(CURDIR)
export QT_QPA_PLATFORM ?= offscreen

# ── Standard targets ──────────────────────────────────────────────

setup:
	cd $(GEOM_DIR) && uv sync

test:
	cd $(GEOM_DIR) && uv run python -c "import cadquery; print('cadquery OK')"

test-all: test

lint:
	cd $(GEOM_DIR) && uv run ruff check .

fmt:
	cd $(GEOM_DIR) && uv run ruff format .

build: allg reports

dev:
	@echo "No dev server — run individual targets: make l1g, make l1s, etc."

clean: reports-clean
	rm -rf $(STEP_DIR)/*.step
	rm -rf $(ANSYS_DIR)/projects/

# ── Geometry targets (runs anywhere with uv + cadquery) ───────────

allg: l1g l2g l3g l4g l5g

l1g:
	cd $(GEOM_DIR) && uv run python lab1.py

l2g:
	cd $(GEOM_DIR) && uv run python lab2.py

l3g:
	cd $(GEOM_DIR) && uv run python lab3.py

l4g:
	cd $(GEOM_DIR) && uv run python lab4.py

l5g:
	cd $(GEOM_DIR) && uv run python lab5.py

# ── ANSYS solve targets (runs on Linux with ANSYS) ────────────────

l1s:
	$(RUNWB2) -B -R $(ANSYS_DIR)/lab1.wbjn

l2s:
	$(RUNWB2) -B -R $(ANSYS_DIR)/lab2.wbjn

l3s:
	$(RUNWB2) -B -R $(ANSYS_DIR)/lab3.wbjn

l4s:
	$(RUNWB2) -B -R $(ANSYS_DIR)/lab4.wbjn

l5s:
	$(RUNWB2) -B -R $(ANSYS_DIR)/lab5.wbjn

# ── Post-processing targets (runs on Linux with ANSYS) ────────────

l1p:
	$(RUNWB2) -B -R $(ANSYS_DIR)/lab1_post.wbjn

l2p:
	$(RUNWB2) -B -R $(ANSYS_DIR)/lab2_post.wbjn

l3p:
	$(RUNWB2) -B -R $(ANSYS_DIR)/lab3_post.wbjn

l4p:
	$(RUNWB2) -B -R $(ANSYS_DIR)/lab4_post.wbjn

l5p:
	$(RUNWB2) -B -R $(ANSYS_DIR)/lab5_post.wbjn

# ── Reports (LaTeX) ──────────────────────────────────────────────

reports:
	$(MAKE) -C $(REPORTS_DIR) all

reports-clean:
	$(MAKE) -C $(REPORTS_DIR) clean
