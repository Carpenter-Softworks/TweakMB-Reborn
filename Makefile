.PHONY: help branch check clean install rebase tag test untag

MAKEFLAGS += --no-print-directory

help:
	@echo "TweakMB-Reborn Dev Tools - Available commands:"
	@echo "  make branch           - create or reset a git branch from a source (prompts for names and pushes)"
	@echo "  make check            - verify local environment (Python >=3.13 and .venv present)"
	@echo "  make clean            - remove Python build artifacts (__pycache__, .pytest_cache, dist, etc.)"
	@echo "  make install          - create .venv (if missing), pip install -e '.[dev]' and regenerate requirements.txt"
	@echo "  make rebase           - interactive git rebase against a target (defaults to origin/main)"
	@echo "  make tag              - create, sign and push a new git tag (auto-increments latest tag suggestion)"
	@echo "  make test             - run ruff lint, pyright, jscpd copy-paste check, and pytest"
	@echo "  make untag            - delete a local and remote git tag (prompts for tag to delete)"

branch:
	@scripts/branch.sh
 
check:
	@scripts/check.sh
 
clean:
	@scripts/clean.sh
 
install:
	@scripts/install.sh
 
rebase:
	@scripts/rebase.sh

tag:
	@scripts/tag.sh

test:
	@scripts/test.sh
 
untag:
	@scripts/untag.sh
