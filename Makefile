run_check:
	python3 -m pylint --disable=R,C --output-format=parseable src/
	python3 -m pylint --errors-only tests/

run_test:
	PYTHONPATH=$(shell pwd) python3 tests/test_database.py
	PYTHONPATH=$(shell pwd) python3 tests/test_html.py
	PYTHONPATH=$(shell pwd) python3 tests/test_main.py
