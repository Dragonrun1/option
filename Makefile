.PHONY: docs test publish lint

test:
	pytest

docs:
	PYTHONPATH=.. make -C docs html
	touch docs/_build/html/.nojekyll

lint:
	mypy -p option
	ruff check
