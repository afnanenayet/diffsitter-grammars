# A makefile to handle common diffsitter grammars updates

.phony: check

check:
	nvchecker -c nvchecker.toml

update:
	cd updater && poetry run python updater.py ../repos
