# A makefile to handle common diffsitter grammars updates

.phony: check

check:
	nvchecker -c nvchecker.toml

update:
	cd updater && uv run python updater.py ../repos
