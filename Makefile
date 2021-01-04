.PHONY: lint
lint:
	flake8 .

.PHONY: mypy
mypy:
	mypy .
